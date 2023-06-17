from app.models.users import User
from app.schemas.users import UserInDBSchema


async def get_user_by_email(email: str) -> UserInDBSchema | None:
    user = await User.filter(email=email).first().values()
    if user:
        return UserInDBSchema(**user)
    return None


async def create_user(payload: dict) -> int:
    new_user = User(**payload)
    await new_user.save()
    return new_user.id
