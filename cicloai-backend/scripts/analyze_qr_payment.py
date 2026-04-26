#!/usr/bin/env python3
"""
Extract payment metadata from receipt images stored in tmp/images/ using tesseract-ocr.

Usage:
  python3 scripts/analyze_qr_payment.py
  python3 scripts/analyze_qr_payment.py --input-dir tmp/images
  python3 scripts/analyze_qr_payment.py --lang spa --psm 6 --oem 3
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SPANISH_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


@dataclass
class PaymentAnalysis:
    file_name: str
    amount: str | None
    transaction_date: str | None
    transaction_id: str | None
    confidence_notes: list[str]
    raw_text: str


def collect_images(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    return sorted(
        path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def normalize_spaces(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def run_tesseract(image_path: Path, lang: str, psm: int, oem: int) -> str:
    if shutil.which("tesseract") is None:
        raise RuntimeError("Tesseract is not installed or not available in PATH")

    command = [
        "tesseract",
        str(image_path),
        "stdout",
        "-l",
        lang,
        "--psm",
        str(psm),
        "--oem",
        str(oem),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    if completed.returncode != 0:
        error_output = completed.stderr.strip() or "Tesseract OCR failed"
        raise RuntimeError(error_output)

    extracted = normalize_spaces(completed.stdout)
    if not extracted:
        raise RuntimeError("Tesseract returned no text")

    return extracted


def parse_amount(text: str) -> tuple[str | None, list[str]]:
    notes: list[str] = []
    patterns = [
        r"(?i)(?:monto|importe|total|Bs|monto pagado)\s*[:\-]?\s*(bs\.?|bob)?\s*(\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{2})?)",
        r"(?i)(bs\.?|bob)\s*(\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{2})?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(match.lastindex or 1)
            if match.lastindex and match.lastindex > 1:
                value = match.group(match.lastindex)
            return value.replace(",", "."), notes

    notes.append("No se encontro un monto con los patrones configurados.")
    return None, notes


def parse_transaction_id(text: str) -> tuple[str | None, list[str]]:
    notes: list[str] = []
    patterns = [
        r"(?i)(?:id(?:\s+de)?\s+transacci[oó]n|nro\.?\s+de\s+operaci[oó]n|n[úu]mero\s+de\s+transacci[oó]n|referencia|trx)\s*[:\-]?\s*([A-Z0-9\-]{6,})",
        r"(?i)(?:operaci[oó]n|transacci[oó]n)\s*[:\-]?\s*([A-Z0-9\-]{6,})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip(), notes

    notes.append("No se encontro un id de transaccion con los patrones configurados.")
    return None, notes


def parse_transaction_date(text: str) -> tuple[str | None, list[str]]:
    notes: list[str] = []
    patterns = [
        r"(?i)(?:fecha|fecha de transacci[oó]n|fecha de pago)\s*[:\-]?\s*(\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóú]+\s*,\s*\d{4})",
        r"(?i)(?:fecha|fecha de transacci[oó]n|fecha de pago)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)",
        r"(?i)(\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóú]+\s*,\s*\d{4})",
        r"(\d{4}[/-]\d{1,2}[/-]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue

        candidate = match.group(1).strip()
        normalized = normalize_date(candidate)
        return normalized or candidate, notes

    notes.append("No se encontro una fecha con los patrones configurados.")
    return None, notes


def normalize_date(value: str) -> str | None:
    month_name_match = re.fullmatch(
        r"(?i)\s*(\d{1,2})\s+de\s+([A-Za-zÁÉÍÓÚáéíóú]+)\s*,\s*(\d{4})\s*",
        value,
    )
    if month_name_match:
        day = int(month_name_match.group(1))
        month_name = month_name_match.group(2).strip().lower()
        year = int(month_name_match.group(3))
        month = SPANISH_MONTHS.get(month_name)
        if month is not None:
            try:
                return datetime(year, month, day).date().isoformat()
            except ValueError:
                return None

    for fmt in (
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            parsed = datetime.strptime(value, fmt)
            if "H" in fmt:
                return parsed.isoformat(sep=" ")
            return parsed.date().isoformat()
        except ValueError:
            continue
    return None


def analyze_text(file_name: str, text: str) -> PaymentAnalysis:
    amount, amount_notes = parse_amount(text)
    transaction_date, date_notes = parse_transaction_date(text)
    transaction_id, id_notes = parse_transaction_id(text)

    return PaymentAnalysis(
        file_name=file_name,
        amount=amount,
        transaction_date=transaction_date,
        transaction_id=transaction_id,
        confidence_notes=amount_notes + date_notes + id_notes,
        raw_text=text,
    )


def print_results(results: Iterable[PaymentAnalysis]) -> None:
    payload = [asdict(result) for result in results]
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze QR payment receipts from images with tesseract-ocr.")
    parser.add_argument("--input-dir", default="tmp/images", help="Directory containing payment receipt images.")
    parser.add_argument("--lang", default="spa", help="Tesseract language pack. Example: spa or spa+eng.")
    parser.add_argument("--psm", type=int, default=6, help="Tesseract page segmentation mode.")
    parser.add_argument("--oem", type=int, default=3, help="Tesseract OCR engine mode.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    image_files = collect_images(input_dir)

    if not image_files:
        raise SystemExit(f"No supported images found in {input_dir}")

    results: list[PaymentAnalysis] = []

    for image_path in image_files:
        try:
            raw_text = run_tesseract(image_path, lang=args.lang, psm=args.psm, oem=args.oem)
            results.append(analyze_text(image_path.name, raw_text))
        except Exception as exc:
            results.append(
                PaymentAnalysis(
                    file_name=image_path.name,
                    amount=None,
                    transaction_date=None,
                    transaction_id=None,
                    confidence_notes=[f"Error procesando archivo: {exc}"],
                    raw_text="",
                )
            )

    print_results(results)


if __name__ == "__main__":
    main()
