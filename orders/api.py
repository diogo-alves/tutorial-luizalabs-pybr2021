from http import HTTPStatus

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import APIConnectionError, OrderNotFoundError
from .schemas import ErrorResponse, HealthCheckResponse, Item
from .services import get_order_items

app = FastAPI()


@app.exception_handler(APIConnectionError)
def api_connection_exception_handler(
    request: Request, exc: APIConnectionError
):
    return JSONResponse(
        status_code=HTTPStatus.BAD_GATEWAY,
        content={'message': 'Falha de comunicação com o servidor remoto'},
    )


@app.exception_handler(OrderNotFoundError)
def order_not_found_exception_handler(
    request: Request, exc: OrderNotFoundError
):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={'message': 'Pedido não encontrado'},
    )


@app.get(
    path='/healthcheck',
    tags=["healthcheck"],
    summary='Integridade do sistema',
    description='Checa se o servidor está online',
    response_model=HealthCheckResponse,
)
async def healthcheck():
    return HealthCheckResponse(status='ok')


@app.get(
    path='/orders/{order_id}/items',
    responses={
        HTTPStatus.NOT_FOUND.value: {
            'description': 'Pedido não encontrado',
            'model': ErrorResponse,
        },
        HTTPStatus.BAD_GATEWAY.value: {
            'description': 'Falha na comunicação com o servidor remoto',
            'model': ErrorResponse,
        },
    },
    tags=["pedidos"],
    summary='Itens de um pedido',
    description='Retorna todos os itens de um determinado pedido',
    response_model=list[Item],
)
def list_items(items: list[Item] = Depends(get_order_items)):
    return items
