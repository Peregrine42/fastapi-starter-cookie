import os
from typing import Optional

from fastapi import APIRouter, Form, status, Request
from fastapi.param_functions import Cookie, Depends
from starlette.responses import HTMLResponse, RedirectResponse
from helpers.not_authorised_exception import NotAuthorisedException
from itsdangerous import URLSafeSerializer

from model.user import User, User_Pydantic

router = APIRouter()


def sign_in_form(request, username=None):
    return f"""
        <html>
            <head>
                <title>Starter</title>
            </head>

            <body>
                <form method="post" action="/sign_in">
                    <input type="hidden" name="csrftoken" value="{request.scope["csrftoken"]()}"/>
                    <input id="username" name="username" type="text" value="{username or ""}"/>
                    <input name="password" type="password"/>
                    <input type="submit" value="Sign in"/>
                </form>
                <script>
                    document.getElementById("username").focus()
                    document.getElementById("username").select()
                </script>
            </body>
        </html>
    """


@router.get("/sign_in", response_class=HTMLResponse)
async def get_sign_in(request: Request):
    print(dict(request.scope))

    response = HTMLResponse(sign_in_form(request))
    return response


@router.post("/sign_in", response_class=HTMLResponse or RedirectResponse)
async def post_sign_in(
    request: Request,
    username: str = Form(None),
    password: str = Form(None),
):
    if not username or not password:
        return sign_in_form(request, username)

    user = None
    try:
        user = await User.get(username=username)
    except Exception as e:
        print(e)

    if not user:
        return sign_in_form(request, username)

    try:
        if not user.verify_password(password):
            return sign_in_form(request, username)
    except Exception as e:
        print(e)
        return sign_in_form(request, username)

    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    cookie_value = URLSafeSerializer(
        os.getenv("SESSION_SECRET", "supersecret"), "auth"
    ).dumps({"id": user.id})
    response.set_cookie(
        key="cookie_sign_in",
        value=cookie_value,
        max_age=15 * 60,
        httponly=True,
        samesite="strict",
    )
    return response


@router.post("/sign_out")
async def post_sign_out(
    cookie_sign_in: Optional[str] = Cookie(None),
):
    if cookie_sign_in:
        response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("cookie_sign_in")
        return response
    else:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


async def get_current_user(cookie_sign_in: Optional[str] = Cookie(None)):
    user = None
    try:
        id = URLSafeSerializer(
            os.getenv("SESSION_SECRET", "supersecret"), "auth"
        ).loads(cookie_sign_in)["id"]
        user = await User.get(id=id)
        if not user:
            raise NotAuthorisedException()
    except Exception as e:
        print(e)
        raise NotAuthorisedException()
    return await User_Pydantic.from_tortoise_orm(user)


@router.get("/bookings", response_class=HTMLResponse)
async def bookings(
    request: Request,
    current_user: User_Pydantic = Depends(get_current_user),
):
    return f"""
        <html>
            <body>
                <form method="post" action="/sign_out"><input type="hidden" name="csrftoken" value="{request.scope["csrftoken"]()}"/><input type="submit" value="Sign out"/></form>
                <a href="/">Home</a>
                <h1>Hello, from bookings!</h1>
            </body>
        </html>
    """


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: User_Pydantic = Depends(get_current_user),
):
    return f"""
        <html>
            <head>
                <title>Starter</title>
            </head>

            <body>
                <form method="post" action="/sign_out"><input type="hidden" name="csrftoken" value="{request.scope["csrftoken"]()}"/><input type="submit" value="Sign out"/></form>
                <a href="/bookings">Bookings</a>
                <h1>Hello, {current_user.username}!!!</h1>
            </body>
        </html>
    """
