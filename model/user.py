from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from argon2 import PasswordHasher

ph = PasswordHasher()


class User(Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=100, unique=True)
    password = fields.TextField(source_field="password_hash")

    def verify_password(self, password):
        return ph.verify(self.password, password)


User_Pydantic = pydantic_model_creator(User, name="User", exclude=("password",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
