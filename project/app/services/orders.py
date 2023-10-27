import hashlib


def get_user_secret(order_id: int, role: str) -> str:
    assert role in ['owner', 'renter']
    return hashlib.sha1(f"{order_id}_{role}".encode('utf-8')).hexdigest()
