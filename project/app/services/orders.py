import re
import hashlib

from fastapi import UploadFile

from app.models.orders import Order


def get_user_secret(order_id: int, role: str) -> str:
    assert role in ['owner', 'renter']
    return hashlib.sha1(f"{order_id}_{role}".encode('utf-8')).hexdigest()


async def verify_e_signature(e_sign_data: UploadFile, order: Order, role: str) -> bool:
    assert role in ['owner', 'renter']
    
    e_sign_template = re.compile(r'-+BEGIN CMS-+.+-+END CMS-+', re.MULTILINE | re.DOTALL)
    e_sign_data_content = await e_sign_data.read()
    e_sign_data_content = e_sign_data_content.decode('utf-8')

    if not e_sign_template.match(e_sign_data_content):
        return False
    return True