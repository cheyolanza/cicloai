#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def post_json(url: str, payload: dict, timeout: float = 5.0) -> tuple[int, float]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    started_at = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
            return response.status, (time.perf_counter() - started_at) * 1000
    except urllib.error.HTTPError as exc:
        exc.read()
        return exc.code, (time.perf_counter() - started_at) * 1000


def percentile(values: list[float], percentage: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(round((len(ordered) - 1) * percentage)), len(ordered) - 1)
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple load test for CicloAI /query endpoint."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()

    ingest_payload = {
        "text": "CicloAI valida inscripciones, archivos Excel, categorias y pagos con OCR para carreras de ciclismo.",
        "metadata": {"source": "load-test"},
    }
    post_json(f"{args.base_url}/ingest", ingest_payload)

    payload = {"question": "Como valida CicloAI los pagos?", "top_k": 2}
    started_at = time.perf_counter()
    results: list[tuple[int, float]] = []

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(post_json, f"{args.base_url}/query", payload)
            for _ in range(args.requests)
        ]
        for future in as_completed(futures):
            results.append(future.result())

    total_seconds = time.perf_counter() - started_at
    latencies = [latency for status, latency in results if 200 <= status < 300]
    errors = [status for status, _ in results if not 200 <= status < 300]
    summary = {
        "requests": args.requests,
        "concurrency": args.concurrency,
        "successful": len(latencies),
        "errors": len(errors),
        "rps": round(args.requests / total_seconds, 2),
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0.0,
        "p95_latency_ms": round(percentile(latencies, 0.95), 2),
        "max_latency_ms": round(max(latencies), 2) if latencies else 0.0,
    }

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "load_test.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (reports_dir / "load_test.md").write_text(
        render_markdown(summary), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def render_markdown(summary: dict) -> str:
    return "\n".join(
        [
            "# Reporte de Prueba de Carga",
            "",
            f"- Requests: {summary['requests']}",
            f"- Concurrencia: {summary['concurrency']}",
            f"- Exitosos: {summary['successful']}",
            f"- Errores: {summary['errors']}",
            f"- Throughput: {summary['rps']} req/s",
            f"- Latencia promedio: {summary['avg_latency_ms']} ms",
            f"- Latencia p95: {summary['p95_latency_ms']} ms",
            f"- Latencia maxima: {summary['max_latency_ms']} ms",
            "",
        ]
    )


if __name__ == "__main__":
    main()
