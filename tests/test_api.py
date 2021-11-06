from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from orders.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_healthcheck_response_should_return_status_code_200(client):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK


def test_healthcheck_response_should_return_json(client):
    response = client.get("/healthcheck")
    assert response.headers['Content-Type'] == 'application/json'


def test_healthcheck_response_should_have_info(client):
    response = client.get("/healthcheck")
    assert response.json() == {'status': 'ok'}
