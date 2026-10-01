from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

DATASET = "superstore_fixed_benchmark_10000plus.csv"

QUERY = "Break down total sales and profit margins across regions"


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_datasets():
    response = client.get("/api/datasets")

    assert response.status_code == 200

    body = response.json()

    assert "datasets" in body
    assert len(body["datasets"]) > 0


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


def test_preview():
    response = client.get(
        "/api/preview",
        params={
            "dataset": DATASET,
            "rows": 5
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "columns" in body
    assert "rows" in body


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

    assert body["pipeline"]
    assert body["plan"]
    assert body["metrics"]
    assert body["insights"]


def test_pdf_report():
    response = client.post(
        "/api/report/pdf",
        json={
            "query": QUERY,
            "dataset": DATASET
        }
    )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith("application/pdf")


def test_invalid_dataset():

    response = client.post(
        "/api/analyze",
        json={
            "query": QUERY,
            "dataset": "does_not_exist.csv"
        }
    )

    assert response.status_code == 404