from http import HTTPStatus
from itertools import chain
from uuid import UUID

import httpx
from starlette.config import Config

from .exceptions import APIConnectionError, OrderNotFoundError
from .schemas import Item

config = Config('.env')

API_KEY = config('MAGALU_API_KEY')
MAGALU_API_URL = config('MAGALU_API_URL')
TENANT_ID = config('MAGALU_TENANT_ID')
MAESTRO_SERVICE_URL = config('MAESTRO_SERVICE_URL')


def _get_order_items_by_package(order_id: UUID, package_id: UUID) -> list[Item]:
    response = httpx.get(
        f'{MAESTRO_SERVICE_URL}/orders/{order_id}/packages/{package_id}/items',
        headers={'X-Api-Key': API_KEY, 'X-Tenant-Id': TENANT_ID}
    )
    response.raise_for_status()
    return [
        Item(
            sku=item['product'].get('code'),
            description=item['product'].get('description', ''),
            image_url=item['product'].get('image_url', ''),
            reference=item['product'].get('reference', ''),
            quantity=item.get('quantity'),
        )
        for item in response.json()
    ]


def get_order_items(order_id: UUID) -> list[Item]:
    try:
        response = httpx.get(
            f'{MAESTRO_SERVICE_URL}/orders/{order_id}',
            headers={'X-Api-Key': API_KEY, 'X-Tenant-Id': TENANT_ID}
        )
        response.raise_for_status()
        packages = response.json()['packages']
        return list(chain.from_iterable(
            _get_order_items_by_package(order_id, package['uuid'])
            for package in packages
        ))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == HTTPStatus.NOT_FOUND:
            raise OrderNotFoundError() from exc
        raise exc
    except httpx.HTTPError as exc:
        raise APIConnectionError() from exc
