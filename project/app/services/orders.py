import hashlib


def get_user_secret(order_id: int, user_id: int, user_password_hash: str) -> str:
    return hashlib.sha1(f"{order_id}_{user_id}_{user_password_hash}".encode('utf-8')).hexdigest()
