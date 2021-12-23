from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse


async def not_authorised_handler(_: Request, __: HTTPException) -> RedirectResponse:
    return RedirectResponse("/sign_in", status_code=status.HTTP_302_FOUND)
