"""
Autonomous Data Analysis Agent
Automated Functional Test Suite

Run:
    python test.py

Or:
    pytest -v

These tests verify the major backend functionality:
- API health
- Dataset discovery
- Dataset profiling
- Dataset preview
- Autonomous analysis
- Analytical workflow
- Metrics and insights
- Report generation
- PDF report generation
- Live dataset refresh
- Invalid dataset handling
"""

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

DATASET = "superstore_fixed_benchmark_10000plus.csv"

QUERY = "Break down total sales and profit margins across regions"


# ============================================================
# 1. HEALTH CHECK
# ============================================================

def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert "agent" in body
    assert "runtime" in body

    print("✓ TC-01 Health check passed")


# ============================================================
# 2. DATASET DISCOVERY
# ============================================================

def test_datasets():
    response = client.get("/api/datasets")

    assert response.status_code == 200

    body = response.json()

    assert "datasets" in body
    assert len(body["datasets"]) > 0

    dataset_names = [
        dataset["name"]
        for dataset in body["datasets"]
    ]

    assert DATASET in dataset_names

    print("✓ TC-02 Dataset discovery passed")


# ============================================================
# 3. DATASET PROFILING
# ============================================================

def test_profile():
    response = client.get(
        "/api/profile",
        params={"dataset": DATASET}
    )

    assert response.status_code == 200

    body = response.json()

    assert body["rows"] >= 10000
    assert body["columns"] >= 20

    assert "column_profiles" in body
    assert "duplicate_rows" in body
    assert "dataset" in body

    print("✓ TC-03 Dataset profiling passed")


# ============================================================
# 4. DATASET PREVIEW
# ============================================================

def test_preview():
    response = client.get(
        "/api/preview",
        params={
            "dataset": DATASET,
            "rows": 10
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "columns" in body
    assert "rows" in body

    assert len(body["columns"]) > 0
    assert len(body["rows"]) <= 10

    print("✓ TC-04 Dataset preview passed")


# ============================================================
# 5. AUTONOMOUS ANALYSIS
# ============================================================

def test_analyze():
    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == QUERY
    assert body["dataset"] == DATASET

    assert "pipeline" in body
    assert "plan" in body
    assert "metrics" in body
    assert "insights" in body

    assert len(body["pipeline"]) > 0
    assert len(body["plan"]) > 0
    assert len(body["insights"]) > 0

    print("✓ TC-05 Autonomous analysis passed")


# ============================================================
# 6. WORKFLOW EXECUTION
# ============================================================

def test_workflow():
    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    body = response.json()

    pipeline = body["pipeline"]

    assert len(pipeline) >= 3

    # Verify important workflow stages
    labels = [
        step.get("label", "").lower()
        for step in pipeline
    ]

    workflow_text = " ".join(labels)

    assert "planner" in workflow_text
    assert "execution" in workflow_text
    assert "synthesis" in workflow_text

    print("✓ TC-06 Analytical workflow passed")


# ============================================================
# 7. METRICS VALIDATION
# ============================================================

def test_metrics():
    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    body = response.json()

    metrics = body["metrics"]

    assert isinstance(metrics, dict)
    assert len(metrics) > 0

    print("✓ TC-07 Metrics generation passed")


# ============================================================
# 8. INSIGHT GENERATION
# ============================================================

def test_insights():
    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    body = response.json()

    insights = body["insights"]

    assert isinstance(insights, list)
    assert len(insights) > 0

    for insight in insights:
        assert isinstance(insight, str)
        assert len(insight.strip()) > 0

    print("✓ TC-08 Evidence-based insights passed")


# ============================================================
# 9. CHART GENERATION
# ============================================================

def test_chart_generation():
    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "chart" in body

    chart = body["chart"]

    assert chart is not None

    if isinstance(chart, dict):
        assert "type" in chart or "data" in chart

    print("✓ TC-09 Chart generation passed")


# ============================================================
# 10. TEXT REPORT
# ============================================================

def test_report():
    response = client.post(
        "/api/report",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    assert "text/plain" in response.headers.get(
        "content-type",
        ""
    )

    content = response.text

    assert "AUTONOMOUS DATA ANALYSIS REPORT" in content
    assert "EXECUTIVE SUMMARY" in content
    assert "DATA QUALITY" in content
    assert "KEY METRICS" in content

    print("✓ TC-10 Text report generation passed")


# ============================================================
# 11. PDF REPORT
# ============================================================

def test_pdf_report():
    response = client.post(
        "/api/report/pdf",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    assert response.headers.get(
        "content-type",
        ""
    ).startswith("application/pdf")

    assert len(response.content) > 1000

    print("✓ TC-11 PDF report generation passed")


# ============================================================
# 12. INVALID DATASET
# ============================================================

def test_invalid_dataset():
    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": "dataset_that_does_not_exist.csv"
        }
    )

    assert response.status_code == 404

    print("✓ TC-12 Invalid dataset handling passed")


# ============================================================
# 13. INVALID FILE TYPE
# ============================================================

def test_invalid_upload():

    files = {
        "file": (
            "invalid.txt",
            b"This is not a supported dataset",
            "text/plain"
        )
    }

    response = client.post(
        "/api/upload",
        files=files
    )

    assert response.status_code == 400

    print("✓ TC-13 Invalid file upload handling passed")


# ============================================================
# 14. LIVE DATASET REFRESH
# ============================================================

def test_live_refresh():
    response = client.post(
        "/api/live/refresh"
    )

    # If the live dataset exists, this should succeed.
    assert response.status_code == 200

    body = response.json()

    assert "message" in body
    assert "filename" in body
    assert "rows" in body

    assert body["rows"] > 0

    print("✓ TC-14 Live dataset refresh passed")


# ============================================================
# TEST RUNNER
# ============================================================

def run_all_tests():

    tests = [
        test_health,
        test_datasets,
        test_profile,
        test_preview,
        test_analyze,
        test_workflow,
        test_metrics,
        test_insights,
        test_chart_generation,
        test_report,
        test_pdf_report,
        test_invalid_dataset,
        test_invalid_upload,
        test_live_refresh,
    ]

    print("\n")
    print("=" * 65)
    print("AUTONOMOUS DATA ANALYSIS AGENT")
    print("AUTOMATED TEST SUITE")
    print("=" * 65)

    passed = 0
    failed = 0

    for test in tests:

        try:
            test()
            passed += 1

        except Exception as error:
            failed += 1

            print(
                f"✗ {test.__name__} FAILED"
            )

            print(
                f"  Reason: {error}"
            )

    print("\n" + "=" * 65)

    print(f"Tests Passed : {passed}")
    print(f"Tests Failed : {failed}")
    print(f"Total Tests  : {len(tests)}")

    print("=" * 65)

    if failed == 0:
        print("\n✓ ALL TESTS PASSED SUCCESSFULLY\n")
    else:
        print(
            f"\n✗ {failed} TEST(S) FAILED\n"
        )


if __name__ == "__main__":
    run_all_tests()