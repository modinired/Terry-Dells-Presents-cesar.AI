#!/usr/bin/env python3
"""Quick runtime benchmark for CESAR.ai orchestrator."""

import asyncio
from time import perf_counter
from uuid import uuid4

from main_orchestrator import CESARAIOrchestrator


async def run_benchmark() -> None:
    orchestrator = CESARAIOrchestrator()
    await orchestrator.ensure_started()

    samples = [
        "Generate a summary of weekly sales data",
        "Prepare customer follow-up emails",
        "Update the CRM pipeline with recent leads",
        "Analyze spreadsheet performance metrics",
    ]

    start = perf_counter()
    for sample in samples:
        task_payload = {
            "task_id": f"benchmark-{uuid4()}",
            "task_type": "report_generation",
            "task_description": sample,
            "priority": "routine",
            "source": "benchmark",
        }
        result = await orchestrator.delegate_task(task_payload)
        print(f"Task '{sample}' => {result.get('status')}")

    elapsed = perf_counter() - start
    print(f"Completed {len(samples)} tasks in {elapsed:.2f}s")

    await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(run_benchmark())
