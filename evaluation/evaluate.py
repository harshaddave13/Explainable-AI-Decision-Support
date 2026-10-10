
import json
import time
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
RESULTS_DIR = BASE_DIR / "results"
API_URL = "http://127.0.0.1:8000/ask"


def evaluate_question(test):
    start = time.perf_counter()

    try:
        response = requests.post(
            API_URL,
            json={"question": test["question"]},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        error = None

    except (requests.RequestException, ValueError) as exc:
        data = {}
        error = str(exc)

    latency_ms = round(
        (time.perf_counter() - start) * 1000, 2
    )

    expected_status = test["expected_answer_status"]
    actual_status = data.get("answer_status")

    sources = data.get("sources", [])
    expected_sources = test.get("expected_sources", [])

    source_hit = None

    if expected_sources:
        source_hit = any(
            actual.get("filename") == expected.get("filename")
            and actual.get("page") == expected.get("page")
            for expected in expected_sources
            for actual in sources
        )

    return {
        "id": test["id"],
        "category": test["category"],
        "question": test["question"],
        "expected_answer_status": expected_status,
        "actual_answer_status": actual_status,
        "status_correct": (
            actual_status == expected_status
            if error is None
            else False
        ),
        "retrieval_status": data.get("retrieval_status"),
        "source_hit": source_hit,
        "latency_ms": latency_ms,
        "answer": data.get("answer"),
        "sources": sources,
        "error": error
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    results = []

    print(f"Running {len(questions)} evaluation tests...\n")

    for test in questions:
        result = evaluate_question(test)
        results.append(result)

        outcome = "PASS" if result["status_correct"] else "FAIL"

        print(
            f"{result['id']} | {outcome} | "
            f"{result['latency_ms']} ms | "
            f"{result['actual_answer_status']}"
        )

        if result["error"]:
            print(f"  Error: {result['error']}")

    total = len(results)
    passed = sum(r["status_correct"] for r in results)

    successful = [
        r for r in results
        if r["error"] is None
    ]

    source_checks = [
        r["source_hit"]
        for r in successful
        if r["source_hit"] is not None
    ]

    status_accuracy = passed / total if total else 0

    source_hit_rate = (
        sum(source_checks) / len(source_checks)
        if source_checks
        else None
    )

    average_latency = (
        sum(r["latency_ms"] for r in successful) / len(successful)
        if successful
        else None
    )

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "status_accuracy": status_accuracy,
        "source_hit_rate": source_hit_rate,
        "average_latency_ms": average_latency,
        "results": results
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"evaluation_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total tests: {total}")
    print(f"Answer-status accuracy: {status_accuracy:.1%}")

    if source_hit_rate is not None:
        print(f"Expected-source hit rate: {source_hit_rate:.1%}")

    if average_latency is not None:
        print(f"Average latency: {average_latency:.2f} ms")

    print(f"Report saved to: {output_file}")


if __name__ == "__main__":
    main()
