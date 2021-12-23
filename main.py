import os
from json import JSONEncoder
from uuid import UUID
from fastapi import FastAPI, Request, status
from starlette.responses import RedirectResponse
from tortoise.contrib.fastapi import register_tortoise
from asgi_csrf import asgi_csrf

from helpers.not_authorised_exception import NotAuthorisedException
from helpers.not_authorised_handler import not_authorised_handler

from routes.home import router as home_router

app = FastAPI()
app.add_exception_handler(NotAuthorisedException, not_authorised_handler)


register_tortoise(
    app,
    db_url=os.getenv("DATABASE_URL") or "sqlite://db.sqlite3",
    modules={"models": ["model"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

old_json_encoder_default = JSONEncoder.default


def new_json_encoder_default(self, obj):
    if isinstance(obj, UUID):
        return str(obj)
    return old_json_encoder_default(self, obj)


JSONEncoder.default = new_json_encoder_default

app.include_router(home_router)

app = asgi_csrf(app, always_protect={"/sign_in"})
