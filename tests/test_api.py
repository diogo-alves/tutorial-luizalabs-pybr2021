from http import HTTPStatus
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from orders.api import app, get_order_items
from orders.exceptions import APIConnectionError, OrderNotFoundError
from orders.schemas import Item


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def override_get_order_items():
    def _override_get_order_items(items_or_error):
        def mock_get_order_items(order_id: UUID) -> list[Item]:
            if isinstance(items_or_error, Exception):
                raise items_or_error
            return items_or_error

        app.dependency_overrides[get_order_items] = mock_get_order_items

    yield _override_get_order_items
    app.dependency_overrides.clear()


class TestHealthCheck:
    def test_should_return_status_code_200(self, client):
        response = client.get("/healthcheck")
        assert response.status_code == HTTPStatus.OK

    def test_response_format_should_be_json(self, client):
        response = client.get("/healthcheck")
        assert response.headers['Content-Type'] == 'application/json'

    def test_response_should_have_info(self, client):
        response = client.get("/healthcheck")
        assert response.json() == {'status': 'ok'}


class TestListOrderItems:
    def test_when_order_id_type_is_invalid_should_return_an_error(
        self, client
    ):
        order_id = 'invalid-id'
        response = client.get(f'/orders/{order_id}/items')
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_when_order_is_not_found_should_return_an_error(
        self, client, override_get_order_items
    ):
        override_get_order_items(OrderNotFoundError())
        order_id = '7e290683-d67b-4f96-a940-44bef1f69d21'
        response = client.get(f'/orders/{order_id}/items')
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_when_order_is_found_should_return_status_code_200(
        self, client, override_get_order_items
    ):
        override_get_order_items([])
        order_id = '7e290683-d67b-4f96-a940-44bef1f69d21'
        response = client.get(f'/orders/{order_id}/items')
        assert response.status_code == HTTPStatus.OK

    def test_when_order_is_found_should_return_items(
        self, client, override_get_order_items
    ):
        items = [
            Item(
                sku='1',
                description='Item 1',
                image_url='http://url.com/img1',
                reference='ref1',
                quantity=1,
            ),
            Item(
                sku='2',
                description='Item 2',
                image_url='http://url.com/img2',
                reference='ref2',
                quantity=2,
            ),
        ]
        override_get_order_items(items)
        order_id = '7e290683-d67b-4f96-a940-44bef1f69d21'
        response = client.get(f'/orders/{order_id}/items')
        assert response.json() == items

    def test_when_service_fail_should_return_an_error(
        self, client, override_get_order_items
    ):
        override_get_order_items(APIConnectionError())
        order_id = 'ea78b59b-885d-4e7b-9cd0-d54acadb4933'
        response = client.get(f'/orders/{order_id}/items')
        assert response.status_code == HTTPStatus.BAD_GATEWAY
