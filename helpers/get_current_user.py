import os
from typing import Optional

from fastapi.param_functions import Cookie
from helpers.not_authorised_exception import NotAuthorisedException
from itsdangerous import URLSafeSerializer

from model.user import User, User_Pydantic


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
