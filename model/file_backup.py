from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator


class FileBackup(Model):
    id = fields.UUIDField(pk=True)
    content = fields.BinaryField()
    key = fields.CharField(max_length=1000)
    content_type = fields.CharField(max_length=1000)


FileBackup_Pydantic = pydantic_model_creator(FileBackup, name="FileBackup")
FileBackupIn_Pydantic = pydantic_model_creator(
    FileBackup, name="FileBackupIn", exclude_readonly=True
)
