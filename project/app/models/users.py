from tortoise import fields, models


class User(models.Model):
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=150)
    phone = fields.CharField(max_length=100, unique=True)
    full_name = fields.CharField(max_length=150, unique=True)
    disabled = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)

    def __str__(self):
        return self.email
