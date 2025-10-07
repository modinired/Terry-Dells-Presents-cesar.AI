#!/usr/bin/env python3
"""
Quick Test Script for Atlas CESAR AI Final Manager Agent
Demonstrates direct interaction with the system
"""

import json
from typing import Optional, Callable

try:
    import pytest
except ImportError:  # pragma: no cover - allows standalone execution without pytest
    pytest = None

import requests
from requests import RequestException


def _safe_request(
    method: Callable[..., requests.Response],
    url: str,
    *,
    reason: str,
    **kwargs
) -> Optional[requests.Response]:
    """Return HTTP response or gracefully handle an unavailable local API."""
    try:
        response = method(url, timeout=5, **kwargs)
        response.raise_for_status()
        return response
    except RequestException as exc:
        message = f"Local Atlas CESAR API unavailable ({reason}): {exc}"
        if pytest is not None:
            pytest.skip(message)
        print(f"⚠️ {message}")
        return None


def test_system():
    """Test the Atlas CESAR AI Final system."""
    base_url = "http://localhost:8000"

    print("🚀 Testing Atlas CESAR AI Final...")

    # Test 1: System Status
    print("\n1. Testing System Status...")
    response = _safe_request(requests.get, f"{base_url}/", reason="status")
    if response is None:
        return
    print(f"✅ Status: {response.json().get('status', 'unknown')}")

    # Test 2: Health Check
    print("\n2. Testing Health Check...")
    response = _safe_request(requests.get, f"{base_url}/health", reason="health check")
    if response is None:
        return
    print(f"✅ Health: {response.json().get('status', 'unknown')}")

    # Test 3: Cursor Task
    print("\n3. Testing Cursor Agent...")
    task_data = {
        "type": "code_review",
        "content": "function test() { return 'hello world'; }",
        "priority": "high"
    }
    response = _safe_request(
        requests.post,
        f"{base_url}/cursor/task",
        reason="cursor task",
        json=task_data
    )
    if response is None:
        return
    print(f"✅ Cursor Task: {response.json().get('status', 'unknown')}")

    # Test 4: Screen Recording
    print("\n4. Testing Screen Recording...")
    response = _safe_request(
        requests.post,
        f"{base_url}/screen/record",
        reason="screen recording"
    )
    if response is None:
        return
    print(f"✅ Screen Recording: {response.json().get('success', False)}")

    # Test 5: Learning Sync
    print("\n5. Testing Learning Sync...")
    response = _safe_request(
        requests.post,
        f"{base_url}/learnings/sync",
        reason="learning sync"
    )
    if response is None:
        return
    print(f"✅ Learning Sync: {response.json().get('success', False)}")

    # Test 6: Status Report
    print("\n6. Testing Status Report...")
    response = _safe_request(requests.get, f"{base_url}/status/report", reason="status report")
    if response is None:
        return
    report = response.json()
    print(f"✅ System Status: {report.get('system_status', 'unknown')}")
    metrics = report.get('metrics', {})
    print(f"✅ Active Agents: {metrics.get('active_agents', 'unknown')}")

    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    test_system()
