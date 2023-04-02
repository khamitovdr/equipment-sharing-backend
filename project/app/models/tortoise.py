from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class User(models.Model):
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=150)
    full_name = fields.CharField(max_length=150, unique=True)
    disabled = fields.BooleanField(default=False)

    def __str__(self):
        return self.email


# Порядок важен! Это супер странно! Если сперва вызвать строку UserSchema,
# то исключенные поля будут исключены и у UserInDBSchema...
UserInDBSchema = pydantic_model_creator(User)
# UserSchema = pydantic_model_creator(User, exclude=["hashed_password", "id"])    # temporary not in use
