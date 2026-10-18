"""/health reports MongoDB reachability; JSON logs carry the request fields."""

import json
import logging

from pymongo.errors import ServerSelectionTimeoutError

from config.json_formatter import JsonFormatter


def test_health_ok_when_database_answers(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


def test_health_503_when_database_is_down(client, monkeypatch):
    def down(*_args, **_kwargs):
        raise ServerSelectionTimeoutError("no servers")

    monkeypatch.setattr("routes.health_routes.ping_database", down)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "down"}


def test_json_formatter_emits_one_object_with_extra_fields():
    record = logging.makeLogRecord(
        {
            "name": "app",
            "levelname": "INFO",
            "msg": "request",
            "path": "/health",
            "status": 200,
        }
    )
    entry = json.loads(JsonFormatter().format(record))
    assert entry["message"] == "request"
    assert entry["level"] == "INFO"
    assert entry["path"] == "/health"
    assert entry["status"] == 200
    assert entry["ts"].endswith("+00:00")


def test_requests_are_logged_with_status_and_duration(client, caplog):
    with caplog.at_level(logging.INFO, logger="config.logging"):
        client.get("/health")
    request_logs = [r for r in caplog.records if r.getMessage() == "request"]
    assert request_logs, "middleware did not log the request"
    last = request_logs[-1]
    assert (last.method, last.path, last.status) == ("GET", "/health", 200)
    assert last.duration_ms >= 0
