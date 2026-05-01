from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
import re
from uuid import UUID, uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus
from cicloai.infrastructure.models.bike_race_category import BikeRaceCategory
from cicloai.infrastructure.models.bike_team import BikeTeam
from cicloai.infrastructure.models.category import Category
from cicloai.infrastructure.models.competition_biker import CompetitionBiker
from cicloai.application.payment_proof_ocr_service import PaymentProofOcrService
from cicloai.application.payment_validation_service import PaymentValidationService


@dataclass(frozen=True)
class NewBikerRegistrationInput:
    dni: str
    dni_extension: str
    full_name: str
    email: str
    birth_date: date
    gender: str
    requested_category: str
    bike_team_name: str
    payment_proof_filename: str
    payment_proof_content_type: str | None
    payment_proof_path: Path


@dataclass(frozen=True)
class CategoryValidationResult:
    category_id: UUID | None
    detected_category: str
    valid: bool
    message: str
    rules_source: str


@dataclass(frozen=True)
class BulkBikerInput:
    dni: str
    full_name: str
    gender: str
    requested_category: str
    birth_date: date


@dataclass(frozen=True)
class BulkRegistrationResult:
    race_id: UUID
    race_name: str
    inserted_competitors: int
    unit_cost: int
    currency: str
    total_amount: int
    message: str


@dataclass(frozen=True)
class RegistrationReview:
    race_id: UUID
    race_name: str
    age: int
    dni: str
    dni_extension: str
    full_name: str
    email: str
    birth_date: date
    gender: str
    requested_category: str
    category_id: UUID | None
    detected_category: str
    bike_team_name: str
    payment_id: UUID
    payment_status: str
    payment_reference: str
    payment_message: str
    payment_provider: str
    payment_extracted_text: str | None
    payment_expected_amount: str
    payment_extracted_amount: str | None
    payment_currency: str
    payment_transaction_id: str | None
    payment_date: date | None
    payment_bank_name: str | None
    category_message: str
    rules_source: str

    def to_token_payload(self) -> dict[str, str]:
        return {
            "race_id": str(self.race_id),
            "race_name": self.race_name,
            "age": str(self.age),
            "dni": self.dni,
            "dni_extension": self.dni_extension,
            "full_name": self.full_name,
            "email": self.email,
            "birth_date": self.birth_date.isoformat(),
            "gender": self.gender,
            "requested_category": self.requested_category,
            "category_id": str(self.category_id) if self.category_id else "",
            "detected_category": self.detected_category,
            "bike_team_name": self.bike_team_name,
            "payment_id": str(self.payment_id),
            "payment_status": self.payment_status,
            "payment_reference": self.payment_reference,
            "payment_message": self.payment_message,
            "payment_provider": self.payment_provider,
            "payment_extracted_text": self.payment_extracted_text or "",
            "payment_expected_amount": self.payment_expected_amount,
            "payment_extracted_amount": self.payment_extracted_amount or "",
            "payment_currency": self.payment_currency,
            "payment_transaction_id": self.payment_transaction_id or "",
            "payment_date": self.payment_date.isoformat() if self.payment_date else "",
            "payment_bank_name": self.payment_bank_name or "",
            "category_message": self.category_message,
            "rules_source": self.rules_source,
        }

    @classmethod
    def from_token_payload(cls, payload: dict[str, str]) -> "RegistrationReview":
        return cls(
            race_id=UUID(payload["race_id"]),
            race_name=payload["race_name"],
            age=int(payload["age"]),
            dni=payload["dni"],
            dni_extension=payload["dni_extension"],
            full_name=payload["full_name"],
            email=payload["email"],
            birth_date=date.fromisoformat(payload["birth_date"]),
            gender=payload.get("gender", "hombre"),
            requested_category=payload["requested_category"],
            category_id=UUID(payload["category_id"]) if payload.get("category_id") else None,
            detected_category=payload["detected_category"],
            bike_team_name=payload["bike_team_name"],
            payment_id=UUID(payload["payment_id"]),
            payment_status=payload["payment_status"],
            payment_reference=payload["payment_reference"],
            payment_message=payload["payment_message"],
            payment_provider=payload.get("payment_provider", "mock"),
            payment_extracted_text=payload.get("payment_extracted_text") or None,
            payment_expected_amount=payload.get("payment_expected_amount", "0.00"),
            payment_extracted_amount=payload.get("payment_extracted_amount") or None,
            payment_currency=payload.get("payment_currency", "BOB"),
            payment_transaction_id=payload.get("payment_transaction_id") or None,
            payment_date=date.fromisoformat(payload["payment_date"]) if payload.get("payment_date") else None,
            payment_bank_name=payload.get("payment_bank_name") or None,
            category_message=payload["category_message"],
            rules_source=payload["rules_source"],
        )


class BulkExcelService:
    """Parses and validates the bulk registration template boundary.

    The current implementation reads CSV files that Excel opens natively and
    applies strict column validation. `.xlsx`/`.xls` are intentionally rejected
    until OpenPyXL/Pandas is added, keeping the contract ready for a real parser
    without pretending to process binary spreadsheets.
    """

    REQUIRED_COLUMNS = ("DNI", "Nombre Completo", "Categoria", "Fecha Nacimiento", "Genero")

    def parse(self, filename: str, file_bytes: bytes) -> list[BulkBikerInput]:
        if not filename.lower().endswith(".csv"):
            raise ValueError("Por ahora la plantilla debe subirse en formato CSV compatible con Excel.")

        try:
            content = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("El archivo debe estar codificado en UTF-8.") from exc

        reader = csv.DictReader(StringIO(content))
        headers = tuple(reader.fieldnames or ())
        missing_columns = [column for column in self.REQUIRED_COLUMNS if column not in headers]
        if missing_columns:
            raise ValueError(f"Faltan columnas obligatorias: {', '.join(missing_columns)}.")

        competitors: list[BulkBikerInput] = []
        for row_number, row in enumerate(reader, start=2):
            dni = (row.get("DNI") or "").strip()
            full_name = (row.get("Nombre Completo") or "").strip()
            requested_category = (row.get("Categoria") or "").strip()
            birth_date_value = (row.get("Fecha Nacimiento") or "").strip()
            gender = self._normalize_gender((row.get("Genero") or "").strip(), row_number)

            if not dni or not full_name or not requested_category or not birth_date_value:
                raise ValueError(f"La fila {row_number} tiene datos obligatorios incompletos.")

            if not dni.isdigit() or len(dni) != 7:
                raise ValueError(f"La fila {row_number} tiene un DNI inválido. Debe contener 7 dígitos.")

            birth_date = self._parse_birth_date(birth_date_value, row_number)

            competitors.append(
                BulkBikerInput(
                    dni=dni,
                    full_name=full_name,
                    gender=gender,
                    requested_category=requested_category,
                    birth_date=birth_date,
                )
            )

        if not competitors:
            raise ValueError("La plantilla no contiene competidores.")

        return competitors

    def _parse_birth_date(self, value: str, row_number: int) -> date:
        """Accepts ISO dates plus common Excel-exported date formats.

        CSV files created from Excel frequently contain `DD/MM/YYYY`,
        `DD-MM-YYYY`, or numeric serial dates. Normalizing those here keeps the
        upload endpoint forgiving while still returning a precise row error.
        """

        normalized = value.strip()
        for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(normalized, date_format).date()
            except ValueError:
                continue

        if normalized.replace(".", "", 1).isdigit():
            serial = int(float(normalized))
            if serial > 0:
                return date(1899, 12, 30) + timedelta(days=serial)

        raise ValueError(
            f"La fila {row_number} tiene fecha inválida. Usa YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY."
        )

    def _normalize_gender(self, value: str, row_number: int) -> str:
        normalized = value.strip().capitalize()
        if normalized not in {"Masculino", "Femenino"}:
            raise ValueError(f"La fila {row_number} tiene un género inválido. Usa Masculino o Femenino.")
        return normalized


class RegistrationService:
    """Coordinates first-race review and final biker registration.

    Review generation is deliberately separate from final insertion so the
    agent can show a Human-in-the-Loop confirmation before any database write.
    The same orchestration can later be reused by existing-user and bulk flows.
    """

    def __init__(
        self,
        db: Session,
        payment_ocr: PaymentProofOcrService,
        payment_validator: PaymentValidationService,
    ) -> None:
        self._db = db
        self._payment_ocr = payment_ocr
        self._payment_validator = payment_validator

    def build_first_race_review(self, registration: NewBikerRegistrationInput) -> RegistrationReview:
        race = self._get_active_race()
        self._validate_identity(registration)
        self._validate_team(registration.bike_team_name)
        reference_date = race.date_of_race or date.today()
        age = self._calculate_age(birth_date=registration.birth_date, reference_date=reference_date)

        payment_ocr_result = self._payment_ocr.analyze_payment_proof(registration.payment_proof_path)
        payment_result = self._payment_validator.validate_payment_proof(
            race=race,
            ocr_result=payment_ocr_result,
            proof_path=registration.payment_proof_path,
            expected_amount=race.cost,
        )
        category_result = self._resolve_category(
            birth_date=registration.birth_date,
            requested_category=registration.requested_category,
            gender=registration.gender,
            race=race,
        )

        if not category_result.valid:
            self._db.rollback()
            raise ValueError(category_result.message)

        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise ValueError("El id de transacción ya fue registrado previamente.") from exc

        return RegistrationReview(
            race_id=race.id,
            race_name=race.name,
            age=age,
            dni=registration.dni,
            dni_extension=registration.dni_extension.upper(),
            full_name=registration.full_name.strip(),
            email=registration.email.strip().lower(),
            birth_date=registration.birth_date,
            gender=self._normalize_competition_gender(registration.gender),
            requested_category=registration.requested_category.strip().upper(),
            category_id=category_result.category_id,
            detected_category=category_result.detected_category,
            bike_team_name=registration.bike_team_name.strip().upper(),
            payment_id=payment_result.payment_id,
            payment_status=payment_result.status,
            payment_reference=payment_result.reference,
            payment_message=payment_result.message,
            payment_provider=payment_result.provider,
            payment_extracted_text=payment_result.extracted_text,
            payment_expected_amount=str(payment_result.expected_amount),
            payment_extracted_amount=str(payment_result.extracted_amount) if payment_result.extracted_amount else None,
            payment_currency=payment_result.currency,
            payment_transaction_id=payment_result.id_transaction,
            payment_date=payment_result.payment_date,
            payment_bank_name=payment_result.bank_name,
            category_message=category_result.message,
            rules_source=category_result.rules_source,
        )

    def register_bulk_from_template(self, filename: str, file_bytes: bytes) -> BulkRegistrationResult:
        race = self._get_active_race()
        competitors = BulkExcelService().parse(filename=filename, file_bytes=file_bytes)
        self._ensure_bulk_file_has_no_duplicates(competitors)

        payment_group_id = uuid4()
        bikers: list[CompetitionBiker] = []
        for competitor in competitors:
            category_result = self._resolve_category(
                birth_date=competitor.birth_date,
                requested_category=competitor.requested_category,
                gender=competitor.gender,
                race=race,
            )
            if not category_result.valid:
                raise ValueError(f"{competitor.full_name}: {category_result.message}")

            self._ensure_competitor_not_registered(
                race_id=race.id,
                dni=competitor.dni,
                full_name=competitor.full_name,
            )

            bikers.append(
                CompetitionBiker(
                    race_id=race.id,
                    category_id=category_result.category_id,
                    payment_group_id=payment_group_id,
                    full_name=competitor.full_name.strip(),
                    email=f"bulk-{competitor.dni}@cicloai.local",
                    dni=competitor.dni,
                    dni_extension="SC",
                    birth_date=competitor.birth_date,
                    gender=self._normalize_competition_gender(competitor.gender),
                    requested_category=competitor.requested_category.strip().upper(),
                    detected_category=category_result.detected_category,
                    bike_team_name="INDEPENDIENTE",
                    payment_status="pending_bulk_payment",
                    payment_reference=f"BULK-{str(payment_group_id)[:8].upper()}",
                    status="pendiente",
                )
            )

        self._db.add_all(bikers)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise ValueError("La plantilla contiene competidores que ya están inscritos.") from exc

        inserted = len(bikers)
        unit_cost = int(race.cost)
        total_amount = unit_cost * inserted
        return BulkRegistrationResult(
            race_id=race.id,
            race_name=race.name,
            inserted_competitors=inserted,
            unit_cost=unit_cost,
            currency=race.currency,
            total_amount=total_amount,
            message="Competidores registrados. Puedes continuar al pago total de la inscripción masiva.",
        )

    def register_from_review(self, review: RegistrationReview) -> CompetitionBiker:
        self._ensure_not_registered(review)
        if review.payment_status != "validated":
            raise ValueError("El pago no fue validado. Sube otro comprobante antes de confirmar la inscripción.")

        biker = CompetitionBiker(
            race_id=review.race_id,
            category_id=review.category_id,
            full_name=review.full_name,
            email=review.email,
            dni=review.dni,
            dni_extension=review.dni_extension,
            birth_date=review.birth_date,
            gender=self._normalize_competition_gender(review.gender),
            requested_category=review.requested_category,
            detected_category=review.detected_category,
            bike_team_name=review.bike_team_name,
            payment_status=review.payment_status,
            payment_reference=review.payment_reference,
            status="pendiente",
        )
        self._db.add(biker)

        try:
            self._db.flush()
            self._payment_validator.attach_to_biker(review.payment_id, biker.id)
            self._db.commit()
        except ValueError:
            self._db.rollback()
            raise
        except IntegrityError as exc:
            self._db.rollback()
            raise ValueError("El ciclista ya está registrado para esta carrera.") from exc

        self._db.refresh(biker)
        return biker

    def _calculate_age(self, *, birth_date: date, reference_date: date) -> int:
        years = reference_date.year - birth_date.year
        has_not_had_birthday = (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day)
        return years - 1 if has_not_had_birthday else years

    def _normalize_competition_gender(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"masculino", "hombre", "male", "m"}:
            return "hombre"
        if normalized in {"femenino", "mujer", "female", "f"}:
            return "mujer"
        raise ValueError("El sexo del corredor no es válido.")

    def _normalize_category_type(self, value: str) -> str:
        normalized = value.strip().upper()
        category_types = {
            "CICLOTURISTA": "Cicloturista",
            "CICLOTURISTAS": "Cicloturista",
            "AFICIONADO": "Aficionado",
            "AFICIONADOS": "Aficionado",
            "NOVATO": "Aficionado",
            "NOVATOS": "Aficionado",
            "FEDERADO": "Federado",
            "FEDERADOS": "Federado",
        }
        if normalized not in category_types:
            raise ValueError("El tipo de categoría seleccionado no es válido.")
        return category_types[normalized]

    def _resolve_category(
        self,
        *,
        birth_date: date,
        requested_category: str,
        gender: str,
        race: BikeRace,
    ) -> CategoryValidationResult:
        reference_date = race.date_of_race or date.today()
        if birth_date >= reference_date:
            return CategoryValidationResult(
                category_id=None,
                detected_category="Sin Categoria",
                valid=False,
                message="La fecha de nacimiento debe ser anterior a la fecha de referencia de la carrera.",
                rules_source="categories",
            )

        category_type = self._normalize_category_type(requested_category)
        competition_gender = self._normalize_competition_gender(gender)
        category_sex = "varones" if competition_gender == "hombre" else "damas"
        age = self._calculate_age(birth_date=birth_date, reference_date=reference_date)
        birth_year = birth_date.year

        statement = (
            select(Category)
            .join(BikeRaceCategory, BikeRaceCategory.category_id == Category.id)
            .where(
                BikeRaceCategory.race_id == race.id,
                Category.status == "active",
                Category.category_type == category_type,
                Category.sex == category_sex,
                Category.age_from <= age,
                or_(Category.age_to.is_(None), Category.age_to >= age),
                or_(
                    and_(Category.born_from <= birth_year, Category.born_to >= birth_year),
                    and_(Category.born_from >= birth_year, Category.born_to <= birth_year),
                ),
            )
            .order_by(Category.age_from.desc(), Category.age_to.asc().nulls_last(), func.upper(Category.name).asc())
            .limit(1)
        )
        category = self._db.execute(statement).scalar_one_or_none()
        if category is None:
            return CategoryValidationResult(
                category_id=None,
                detected_category="Sin Categoria",
                valid=True,
                message="No existe una categoría habilitada para la carrera con ese tipo y edad.",
                rules_source="categories",
            )

        return CategoryValidationResult(
            category_id=category.id,
            detected_category=category.name,
            valid=True,
            message="Categoría resuelta por tipo, edad y categorías habilitadas en la carrera.",
            rules_source="categories",
        )

    def _ensure_not_registered(self, review: RegistrationReview) -> None:
        """Blocks duplicate registrations for the same race.

        The public agent cannot allow a person to register twice. We compare
        exact DNI and normalized full name before insert so the frontend gets a
        controlled business message; database constraints back this up for
        concurrent requests.
        """

        self._ensure_competitor_not_registered(
            race_id=review.race_id,
            dni=review.dni,
            full_name=review.full_name,
        )

    def _ensure_competitor_not_registered(self, race_id: UUID, dni: str, full_name: str) -> None:
        normalized_name = full_name.strip().upper()
        statement = select(CompetitionBiker).where(
            CompetitionBiker.race_id == race_id,
            (
                (CompetitionBiker.dni == dni)
                | (func.upper(CompetitionBiker.full_name) == normalized_name)
            ),
        )
        existing = self._db.execute(statement).scalars().first()

        if existing is None:
            return

        if existing.dni == dni:
            raise ValueError("La persona ya está inscrita para esta carrera con el mismo DNI.")

        raise ValueError("La persona ya está inscrita para esta carrera con el mismo nombre.")

    def _ensure_bulk_file_has_no_duplicates(self, competitors: list[BulkBikerInput]) -> None:
        seen_dni: set[str] = set()
        seen_names: set[str] = set()

        for competitor in competitors:
            normalized_name = competitor.full_name.strip().upper()
            if competitor.dni in seen_dni:
                raise ValueError(f"La plantilla contiene DNI duplicado: {competitor.dni}.")
            if normalized_name in seen_names:
                raise ValueError(f"La plantilla contiene nombre duplicado: {competitor.full_name}.")

            seen_dni.add(competitor.dni)
            seen_names.add(normalized_name)

    def _get_active_race(self) -> BikeRace:
        statement = (
            select(BikeRace)
            .where(BikeRace.status == BikeRaceStatus.ACTIVE.value)
            .order_by(BikeRace.created_at.desc())
            .limit(1)
        )
        race = self._db.execute(statement).scalar_one_or_none()
        if race is None:
            raise ValueError("No hay carreras habilitadas actualmente.")
        return race

    def _validate_identity(self, registration: NewBikerRegistrationInput) -> None:
        if not registration.dni.isdigit() or len(registration.dni) != 7:
            raise ValueError("El DNI debe contener exactamente 7 dígitos.")

        if registration.dni_extension.upper() not in {"BE", "CH", "CO", "LP", "OR", "PA", "PO", "SC", "TJ"}:
            raise ValueError("La extensión del DNI no es válida.")

        if not registration.full_name.strip():
            raise ValueError("El nombre completo es obligatorio.")

        email = registration.email.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("El email del participante no es válido.")

    def _validate_team(self, bike_team_name: str) -> None:
        statement = select(BikeTeam).where(
            func.upper(BikeTeam.name) == bike_team_name.strip().upper(),
            BikeTeam.active.is_(True),
        )
        if self._db.execute(statement).scalar_one_or_none() is None:
            raise ValueError("El equipo seleccionado no está activo.")
