from http import HTTPStatus

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import APIConnectionError, OrderNotFoundError
from .schemas import Item
from .services import get_order_items

app = FastAPI()


@app.exception_handler(APIConnectionError)
def api_connection_exception_handler(request: Request, exc: APIConnectionError):
    return JSONResponse(
        status_code=HTTPStatus.BAD_GATEWAY,
        content={'message': 'Falha de comunicação com o servidor remoto'}
    )


@app.exception_handler(OrderNotFoundError)
def order_not_found_exception_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={'message': 'Pedido não encontrado'}
    )


@app.get('/healthcheck')
async def healthcheck():
    return {'status': 'ok'}


@app.get('/orders/{order_id}/items')
def list_items(items: list[Item] = Depends(get_order_items)):
    return items
