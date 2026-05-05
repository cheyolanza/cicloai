from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy import Select, and_, delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus
from cicloai.infrastructure.models.bike_race_category import BikeRaceCategory
from cicloai.infrastructure.models.category import Category
from cicloai.infrastructure.models.competition_biker import CompetitionBiker
from cicloai.infrastructure.models.race_qr_payment import RaceQrPayment

BIKER_STATUSES = {"habilitado", "deshabilitado", "pendiente"}
BIKER_GENDERS = {"hombre", "mujer"}
BIKER_SORT_FIELDS = {
    "full_name",
    "gender",
    "age",
    "bike_team_name",
    "detected_category",
    "created_at",
    "status",
}
PAYMENT_VALIDATED_STATUS = "validated"
CATEGORY_SEXES = {"varones", "damas"}
CATEGORY_TYPES = {"Cicloturista", "Aficionado", "Federado"}
CATEGORY_STATUSES = {"active", "deactive"}


@dataclass(frozen=True)
class AdminDashboardMetrics:
    active_race_id: UUID | None
    active_race_name: str | None
    active_race_registered_bikers: int


@dataclass(frozen=True)
class AdminBikerListResult:
    items: list[tuple[CompetitionBiker, RaceQrPayment | None]]
    total: int


@dataclass(frozen=True)
class AdminPaymentRecord:
    payment: RaceQrPayment
    race: BikeRace
    bikers: list[CompetitionBiker]
    total_collected: Decimal


@dataclass(frozen=True)
class AdminCategoryRecord:
    category: Category
    races: list[BikeRace]


@dataclass(frozen=True)
class AdminRaceInput:
    name: str
    location_name: str
    location: str | None
    strava_map_html: str | None
    year: int
    date_of_race: date | None
    status: str
    cost: Decimal
    currency: str


@dataclass(frozen=True)
class AdminBikerInput:
    full_name: str
    email: str
    dni: str
    dni_extension: str
    birth_date: date
    gender: str
    requested_category: str
    detected_category: str
    bike_team_name: str
    payment_status: str
    payment_reference: str
    status: str


@dataclass(frozen=True)
class AdminCategoryInput:
    name: str
    category_type: str
    sex: str
    age_from: int
    age_to: int | None
    born_from: int
    born_to: int
    race_ids: list[UUID]


class AdminService:
    """Admin operations for races and registered bikers."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def dashboard_metrics(self) -> AdminDashboardMetrics:
        active_race = self._get_active_race()
        if active_race is None:
            return AdminDashboardMetrics(
                active_race_id=None,
                active_race_name=None,
                active_race_registered_bikers=0,
            )

        total = self._db.execute(
            select(func.count(CompetitionBiker.id)).where(
                CompetitionBiker.race_id == active_race.id
            )
        ).scalar_one()
        return AdminDashboardMetrics(
            active_race_id=active_race.id,
            active_race_name=active_race.name,
            active_race_registered_bikers=int(total),
        )

    def list_races(self) -> list[tuple[BikeRace, int]]:
        statement = (
            select(BikeRace, func.count(CompetitionBiker.id))
            .join(
                CompetitionBiker, CompetitionBiker.race_id == BikeRace.id, isouter=True
            )
            .group_by(BikeRace.id)
            .order_by(BikeRace.created_at.desc())
        )
        return [(race, int(total)) for race, total in self._db.execute(statement).all()]

    def create_race(self, race_input: AdminRaceInput) -> BikeRace:
        self._validate_race_input(race_input)
        self._ensure_single_active_race(race_input.status)

        race = BikeRace(
            name=race_input.name.strip(),
            location_name=race_input.location_name.strip(),
            location=race_input.location.strip() if race_input.location else None,
            strava_map_html=race_input.strava_map_html.strip()
            if race_input.strava_map_html
            else None,
            year=race_input.year,
            date_of_race=race_input.date_of_race,
            status=race_input.status,
            race_cost=int(race_input.cost),
            cost=race_input.cost,
            currency=race_input.currency,
        )
        self._db.add(race)
        self._commit_or_raise(
            "No se pudo crear la carrera. Verifica que no exista una carrera con el mismo nombre y gestión."
        )
        self._db.refresh(race)
        return race

    def update_race(self, race_id: UUID, race_input: AdminRaceInput) -> BikeRace:
        self._validate_race_input(race_input)
        race = self._get_race(race_id)
        self._ensure_single_active_race(race_input.status, race_id=race_id)

        race.name = race_input.name.strip()
        race.location_name = race_input.location_name.strip()
        race.location = race_input.location.strip() if race_input.location else None
        race.strava_map_html = (
            race_input.strava_map_html.strip() if race_input.strava_map_html else None
        )
        race.year = race_input.year
        race.date_of_race = race_input.date_of_race
        race.status = race_input.status
        race.race_cost = int(race_input.cost)
        race.cost = race_input.cost
        race.currency = race_input.currency
        self._commit_or_raise("No se pudo actualizar la carrera.")
        self._db.refresh(race)
        return race

    def deactivate_race(self, race_id: UUID) -> BikeRace:
        race = self._get_race(race_id)
        race.status = BikeRaceStatus.DEACTIVE.value
        self._db.commit()
        self._db.refresh(race)
        return race

    def list_categories(self) -> list[AdminCategoryRecord]:
        statement = select(Category).order_by(
            func.upper(Category.name).asc(), Category.sex.asc()
        )
        categories = list(self._db.execute(statement).scalars().all())
        return [
            AdminCategoryRecord(
                category=category, races=self._category_races(category.id)
            )
            for category in categories
        ]

    def category_record(self, category_id: UUID) -> AdminCategoryRecord:
        category = self._get_category(category_id)
        return AdminCategoryRecord(
            category=category, races=self._category_races(category.id)
        )

    def create_category(self, category_input: AdminCategoryInput) -> Category:
        self._validate_category_input(category_input)
        category = Category(
            name=category_input.name.strip(),
            category_type=category_input.category_type,
            sex=category_input.sex,
            age_from=category_input.age_from,
            age_to=category_input.age_to,
            born_from=category_input.born_from,
            born_to=category_input.born_to,
            status="active",
        )
        self._db.add(category)
        try:
            self._db.flush()
            self._sync_category_races(category.id, category_input.race_ids)
            self._db.commit()
        except ValueError:
            self._db.rollback()
            raise
        except IntegrityError as exc:
            self._db.rollback()
            raise ValueError(
                "No se pudo crear la categoría. Verifica que no exista una categoría con el mismo nombre, sexo y tipo."
            ) from exc
        self._db.refresh(category)
        return category

    def update_category(
        self, category_id: UUID, category_input: AdminCategoryInput
    ) -> Category:
        self._validate_category_input(category_input)
        category = self._get_category(category_id)
        category.name = category_input.name.strip()
        category.category_type = category_input.category_type
        category.sex = category_input.sex
        category.age_from = category_input.age_from
        category.age_to = category_input.age_to
        category.born_from = category_input.born_from
        category.born_to = category_input.born_to
        try:
            self._sync_category_races(category.id, category_input.race_ids)
            self._db.commit()
        except ValueError:
            self._db.rollback()
            raise
        except IntegrityError as exc:
            self._db.rollback()
            raise ValueError("No se pudo actualizar la categoría.") from exc
        self._db.refresh(category)
        return category

    def update_category_status(self, category_id: UUID, status: str) -> Category:
        self._validate_category_status(status)
        category = self._get_category(category_id)
        category.status = status
        self._db.commit()
        self._db.refresh(category)
        return category

    def list_bikers(
        self,
        race_id: UUID,
        *,
        page: int,
        page_size: int,
        search: str | None,
        sort_by: str,
        sort_direction: str,
    ) -> AdminBikerListResult:
        self._get_race(race_id)
        page = max(page, 0)
        page_size = min(max(page_size, 1), 100)
        sort_by = sort_by if sort_by in BIKER_SORT_FIELDS else "created_at"
        sort_direction = sort_direction if sort_direction in {"asc", "desc"} else "desc"

        base_filters = [CompetitionBiker.race_id == race_id]
        search_value = (search or "").strip()
        if search_value:
            search_pattern = f"%{search_value}%"
            base_filters.append(
                or_(
                    CompetitionBiker.full_name.ilike(search_pattern),
                    CompetitionBiker.bike_team_name.ilike(search_pattern),
                    CompetitionBiker.detected_category.ilike(search_pattern),
                    CompetitionBiker.requested_category.ilike(search_pattern),
                    CompetitionBiker.dni.ilike(search_pattern),
                    CompetitionBiker.status.ilike(search_pattern),
                    CompetitionBiker.gender.ilike(search_pattern),
                )
            )

        total = self._db.execute(
            select(func.count(CompetitionBiker.id)).where(*base_filters)
        ).scalar_one()
        statement = (
            select(CompetitionBiker, RaceQrPayment)
            .join(
                RaceQrPayment,
                or_(
                    RaceQrPayment.competition_biker_id == CompetitionBiker.id,
                    and_(
                        CompetitionBiker.payment_group_id.is_not(None),
                        RaceQrPayment.payment_group_id
                        == CompetitionBiker.payment_group_id,
                    ),
                ),
                isouter=True,
            )
            .where(*base_filters)
        )
        statement = self._apply_biker_sort(
            statement, sort_by=sort_by, sort_direction=sort_direction
        )
        statement = statement.offset(page * page_size).limit(page_size)
        return AdminBikerListResult(
            items=list(self._db.execute(statement).all()), total=int(total)
        )

    def list_bikers_for_export(self, race_id: UUID) -> list[CompetitionBiker]:
        self._get_race(race_id)
        statement = (
            select(CompetitionBiker)
            .where(
                CompetitionBiker.race_id == race_id,
                CompetitionBiker.status == "habilitado",
            )
            .order_by(
                func.upper(CompetitionBiker.full_name).asc(),
                func.upper(CompetitionBiker.detected_category).asc(),
            )
        )
        return list(self._db.execute(statement).scalars().all())

    def update_biker(
        self, biker_id: UUID, biker_input: AdminBikerInput
    ) -> CompetitionBiker:
        self._validate_biker_input(biker_input)
        biker = self._get_biker(biker_id)

        biker.full_name = biker_input.full_name.strip()
        biker.email = biker_input.email.strip().lower()
        biker.dni = biker_input.dni.strip()
        biker.dni_extension = biker_input.dni_extension.strip().upper()
        biker.birth_date = biker_input.birth_date
        biker.gender = biker_input.gender
        biker.requested_category = biker_input.requested_category.strip().upper()
        biker.detected_category = biker_input.detected_category.strip()
        biker.bike_team_name = biker_input.bike_team_name.strip().upper()
        biker.payment_status = biker_input.payment_status.strip()
        biker.payment_reference = biker_input.payment_reference.strip()
        biker.status = biker_input.status
        self._commit_or_raise("No se pudo actualizar el corredor.")
        self._db.refresh(biker)
        return biker

    def update_biker_status(self, biker_id: UUID, status: str) -> CompetitionBiker:
        self._validate_biker_status(status)
        biker = self._get_biker(biker_id)
        biker.status = status
        self._db.commit()
        self._db.refresh(biker)
        return biker

    def list_payments(self) -> list[AdminPaymentRecord]:
        total_collected = self._total_collected()
        statement = (
            select(RaceQrPayment, BikeRace)
            .join(BikeRace, BikeRace.id == RaceQrPayment.bike_race_id)
            .order_by(RaceQrPayment.created_at.desc())
        )
        records: list[AdminPaymentRecord] = []
        for payment, race in self._db.execute(statement).all():
            records.append(
                AdminPaymentRecord(
                    payment=payment,
                    race=race,
                    bikers=self._payment_bikers(payment),
                    total_collected=total_collected,
                )
            )
        return records

    def validate_payment(self, payment_id: UUID) -> AdminPaymentRecord:
        payment = self._get_payment(payment_id)
        race = self._get_race(payment.bike_race_id)
        bikers = self._payment_bikers(payment)
        if not bikers:
            raise ValueError("El pago no tiene corredores asociados.")

        if payment.payment_group_id is None and len(bikers) != 1:
            raise ValueError(
                "El pago individual debe estar asociado a un solo corredor."
            )

        if payment.payment_group_id is not None:
            group_bikers = self._group_bikers(payment)
            if len(group_bikers) <= 1:
                raise ValueError(
                    "El pago grupal debe estar asociado a más de un corredor."
                )
            if {biker.id for biker in group_bikers} != {biker.id for biker in bikers}:
                raise ValueError(
                    "El pago grupal solo puede validarse para el grupo completo."
                )
            bikers = group_bikers

        payment.status = PAYMENT_VALIDATED_STATUS
        payment.rejection_reason = None
        for biker in bikers:
            biker.payment_status = PAYMENT_VALIDATED_STATUS
            biker.payment_reference = payment.id_transaction or biker.payment_reference
            biker.status = "habilitado"

        self._db.commit()
        self._db.refresh(payment)
        refreshed_bikers = self._payment_bikers(payment)
        return AdminPaymentRecord(
            payment=payment,
            race=race,
            bikers=refreshed_bikers,
            total_collected=self._total_collected(),
        )

    def get_payment_proof_path(self, payment_id: UUID) -> Path:
        payment = self._get_payment(payment_id)

        proof_path = Path(payment.proof_file_path)
        if not proof_path.exists():
            raise ValueError("El archivo del comprobante no existe.")

        return proof_path

    def _get_active_race(self) -> BikeRace | None:
        statement = (
            select(BikeRace)
            .where(BikeRace.status == BikeRaceStatus.ACTIVE.value)
            .limit(1)
        )
        return self._db.execute(statement).scalar_one_or_none()

    def _get_race(self, race_id: UUID) -> BikeRace:
        race = self._db.get(BikeRace, race_id)
        if race is None:
            raise ValueError("No se encontró la carrera.")
        return race

    def _get_biker(self, biker_id: UUID) -> CompetitionBiker:
        biker = self._db.get(CompetitionBiker, biker_id)
        if biker is None:
            raise ValueError("No se encontró el corredor.")
        return biker

    def _get_category(self, category_id: UUID) -> Category:
        category = self._db.get(Category, category_id)
        if category is None:
            raise ValueError("No se encontró la categoría.")
        return category

    def _get_payment(self, payment_id: UUID) -> RaceQrPayment:
        payment = self._db.get(RaceQrPayment, payment_id)
        if payment is None:
            raise ValueError("No se encontró el pago.")
        return payment

    def _category_races(self, category_id: UUID) -> list[BikeRace]:
        statement = (
            select(BikeRace)
            .join(BikeRaceCategory, BikeRaceCategory.race_id == BikeRace.id)
            .where(BikeRaceCategory.category_id == category_id)
            .order_by(BikeRace.year.desc(), func.upper(BikeRace.name).asc())
        )
        return list(self._db.execute(statement).scalars().all())

    def _sync_category_races(self, category_id: UUID, race_ids: list[UUID]) -> None:
        unique_race_ids = list(dict.fromkeys(race_ids))
        if unique_race_ids:
            existing_count = self._db.execute(
                select(func.count(BikeRace.id)).where(BikeRace.id.in_(unique_race_ids))
            ).scalar_one()
            if int(existing_count) != len(unique_race_ids):
                raise ValueError("Una o más carreras seleccionadas no existen.")

        self._db.execute(
            delete(BikeRaceCategory).where(BikeRaceCategory.category_id == category_id)
        )
        self._db.add_all(
            [
                BikeRaceCategory(race_id=race_id, category_id=category_id)
                for race_id in unique_race_ids
            ]
        )

    def _payment_bikers(self, payment: RaceQrPayment) -> list[CompetitionBiker]:
        if payment.payment_group_id is not None:
            return self._group_bikers(payment)
        if payment.competition_biker_id is None:
            return []
        biker = self._db.get(CompetitionBiker, payment.competition_biker_id)
        return [biker] if biker is not None else []

    def _group_bikers(self, payment: RaceQrPayment) -> list[CompetitionBiker]:
        if payment.payment_group_id is None:
            return []
        statement = (
            select(CompetitionBiker)
            .where(
                CompetitionBiker.race_id == payment.bike_race_id,
                CompetitionBiker.payment_group_id == payment.payment_group_id,
            )
            .order_by(CompetitionBiker.full_name.asc())
        )
        return list(self._db.execute(statement).scalars().all())

    def _total_collected(self) -> Decimal:
        total = Decimal("0")
        payments = self._db.execute(
            select(RaceQrPayment).where(
                RaceQrPayment.status == PAYMENT_VALIDATED_STATUS
            )
        ).scalars()
        for payment in payments:
            bikers = self._payment_bikers(payment)
            if bikers and all(biker.status == "habilitado" for biker in bikers):
                total += payment.expected_amount
        return total

    def _ensure_single_active_race(
        self, status: str, race_id: UUID | None = None
    ) -> None:
        if status != BikeRaceStatus.ACTIVE.value:
            return

        statement = select(BikeRace.id).where(
            BikeRace.status == BikeRaceStatus.ACTIVE.value
        )
        if race_id is not None:
            statement = statement.where(BikeRace.id != race_id)

        if self._db.execute(statement.limit(1)).scalar_one_or_none() is not None:
            raise ValueError("Solo puede existir una carrera activa.")

    def _validate_race_input(self, race_input: AdminRaceInput) -> None:
        if not race_input.name.strip():
            raise ValueError("El nombre de la carrera es obligatorio.")
        if not race_input.location_name.strip():
            raise ValueError("La ubicación de la carrera es obligatoria.")
        if race_input.year < 2000:
            raise ValueError("La gestión de la carrera no es válida.")
        if race_input.status not in {
            BikeRaceStatus.ACTIVE.value,
            BikeRaceStatus.DEACTIVE.value,
        }:
            raise ValueError("El estado de la carrera no es válido.")
        if race_input.currency not in {"BOB", "USD"}:
            raise ValueError("La moneda no es válida.")
        if race_input.cost < Decimal("0"):
            raise ValueError("El costo de la carrera no puede ser negativo.")

    def _validate_category_input(self, category_input: AdminCategoryInput) -> None:
        current_year = date.today().year
        if not category_input.name.strip():
            raise ValueError("El nombre de la categoría es obligatorio.")
        if category_input.sex not in CATEGORY_SEXES:
            raise ValueError("El sexo de la categoría no es válido.")
        if category_input.category_type not in CATEGORY_TYPES:
            raise ValueError("El tipo de categoría no es válido.")
        if category_input.age_from < 0:
            raise ValueError("La edad desde no puede ser negativa.")
        if (
            category_input.age_to is not None
            and category_input.age_to < category_input.age_from
        ):
            raise ValueError("La edad hasta debe ser mayor o igual a la edad desde.")
        if category_input.born_from < 1900 or category_input.born_from > current_year:
            raise ValueError("El año de nacimiento desde no es válido.")
        if category_input.born_to < 1900 or category_input.born_to > current_year:
            raise ValueError("El año de nacimiento hasta no es válido.")

    def _validate_category_status(self, status: str) -> None:
        if status not in CATEGORY_STATUSES:
            raise ValueError("El estado de la categoría no es válido.")

    def _validate_biker_input(self, biker_input: AdminBikerInput) -> None:
        if not biker_input.full_name.strip():
            raise ValueError("El nombre del corredor es obligatorio.")
        if not biker_input.email.strip():
            raise ValueError("El email del corredor es obligatorio.")
        if not biker_input.dni.strip().isdigit() or len(biker_input.dni.strip()) != 7:
            raise ValueError("El DNI debe contener exactamente 7 dígitos.")
        if not biker_input.dni_extension.strip():
            raise ValueError("La extensión del DNI es obligatoria.")
        if biker_input.gender not in BIKER_GENDERS:
            raise ValueError("El sexo del corredor no es válido.")
        if not biker_input.requested_category.strip():
            raise ValueError("La categoría solicitada es obligatoria.")
        if not biker_input.detected_category.strip():
            raise ValueError("La categoría detectada es obligatoria.")
        if not biker_input.bike_team_name.strip():
            raise ValueError("El equipo es obligatorio.")
        if not biker_input.payment_status.strip():
            raise ValueError("El estado de pago es obligatorio.")
        if not biker_input.payment_reference.strip():
            raise ValueError("La referencia de pago es obligatoria.")
        self._validate_biker_status(biker_input.status)

    def _validate_biker_status(self, status: str) -> None:
        if status not in BIKER_STATUSES:
            raise ValueError("El estado del corredor no es válido.")

    def _apply_biker_sort(
        self,
        statement: Select[tuple[CompetitionBiker, RaceQrPayment | None]],
        *,
        sort_by: str,
        sort_direction: str,
    ) -> Select[tuple[CompetitionBiker, RaceQrPayment | None]]:
        if sort_by == "age":
            order_column = (
                CompetitionBiker.birth_date.desc()
                if sort_direction == "asc"
                else CompetitionBiker.birth_date.asc()
            )
            return statement.order_by(order_column, CompetitionBiker.full_name.asc())

        sort_columns = {
            "full_name": func.upper(CompetitionBiker.full_name),
            "gender": CompetitionBiker.gender,
            "bike_team_name": func.upper(CompetitionBiker.bike_team_name),
            "detected_category": func.upper(CompetitionBiker.detected_category),
            "created_at": CompetitionBiker.created_at,
            "status": CompetitionBiker.status,
        }
        order_column = sort_columns.get(sort_by, CompetitionBiker.created_at)
        order_column = (
            order_column.asc() if sort_direction == "asc" else order_column.desc()
        )
        return statement.order_by(order_column, CompetitionBiker.full_name.asc())

    def _commit_or_raise(self, message: str) -> None:
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise ValueError(message) from exc
