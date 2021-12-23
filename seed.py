import os
from tortoise import Tortoise, run_async
from model.user import User
from argon2 import PasswordHasher

ph = PasswordHasher()


async def seed():
    user_obj = User(
        username="admin", password=ph.hash(os.getenv("ADMIN_PASSWORD") or "admin")
    )
    try:
        await user_obj.save()
    except Exception as e:
        print(e)


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["model"]})
    # Generate the schema
    await Tortoise.generate_schemas()
    await seed()


# run_async is a helper function to run simple async Tortoise scripts.
run_async(init())
