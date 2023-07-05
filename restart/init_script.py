import requests


BASE_HEADERS = {
    "accept": "application/json",
}

HEADERS = {
    **BASE_HEADERS,
    "Content-Type": "application/json",
}

FORM_DATA_HEADERS = {
    **BASE_HEADERS,
    "Content-Type": "application/x-www-form-urlencoded",
}

URL = "http://localhost:8004/"


USERS = [
    {
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "+79999999999",
        "password": "secret",
        "organization_inn": "9729311480", # FFF Digital
    },
    {
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "phone": "+78888888888",
        "password": "secret2",
        "organization_inn": "7720876531", # ЦПСИА
    },
    {
        "full_name": "Bob Odenkirk",
        "email": "bob@example.com",
        "phone": "+76666666666",
        "password": "secret3",
    }
]

def print_request_details(res):
    print(f"curl -X {res.request.method}\n\t{res.request.url}")
    for k, v in res.request.headers.items():
        print(f"\t-H '{k}: {v}'")
    
    if res.request.body:
        print(f"\t-d '{res.request.body}'")

    print(f"\nResponse: {res.status_code}")
    print(f"Headers: {res.headers}")
    print(f"Body: {res.text}")


# Init Activities table
res = requests.get(f"{URL}fill_db/", headers=HEADERS)
assert res.status_code == 200

# Create users
for user in USERS:
    res = requests.post(f"{URL}users/create/", headers=HEADERS, json=user)
    if res.status_code != 200:
        print(res.text)
        
    assert res.status_code == 200

# Authenticate
credentials = {
    "username": "johndoe@example.com",
    "password": "secret",
}
res = requests.post(f"{URL}token/", headers=FORM_DATA_HEADERS, data=credentials)
assert res.status_code == 200
token = res.json()["access_token"]
AUTH_HEADERS = {
    **HEADERS,
    "Authorization": f"Bearer {token}",
}

# Check access
res = requests.get(f"{URL}users/me/", headers=HEADERS)
assert res.status_code == 401
res = requests.get(f"{URL}users/me/", headers=AUTH_HEADERS)
assert res.status_code == 200


# Check organization endpoints
res = requests.get(f"{URL}organizations/{USERS[1]['organization_inn']}/", headers=HEADERS)
assert res.status_code == 200
assert res.json()["inn"] == USERS[1]["organization_inn"]


# Check user update

# Simple update
SIMPLE_UPDATE_DATA = {
    "full_name": "John Doe Jr.",
    "phone": "+71234567890",
    "organization_inn": "7721581040", # ДЕЙТА КЬЮ
}
res = requests.put(f"{URL}users/me/", headers=AUTH_HEADERS, json=SIMPLE_UPDATE_DATA)
assert res.status_code == 200

updated_user = res.json()
assert updated_user["full_name"] == SIMPLE_UPDATE_DATA["full_name"]
assert updated_user["phone"] == SIMPLE_UPDATE_DATA["phone"]

res = requests.get(f"{URL}organizations/my-organization/", headers=AUTH_HEADERS)
assert res.status_code == 200
assert res.json()["inn"] == SIMPLE_UPDATE_DATA["organization_inn"]

# Update password
PASSWORD_UPDATE_DATA_FALSE_PASSWORD = {
    "new_password": "new_secret",
    "password": "not_secret",
}
res = requests.put(f"{URL}users/me/", headers=AUTH_HEADERS, json=PASSWORD_UPDATE_DATA_FALSE_PASSWORD)
assert res.status_code == 401

PASSWORD_UPDATE_DATA = {
    "new_password": "new_secret",
    "password": "secret",
}
res = requests.put(f"{URL}users/me/", headers=AUTH_HEADERS, json=PASSWORD_UPDATE_DATA)
assert res.status_code == 200

# Authenticate with new password
credentials = {
    "username": "johndoe@example.com",
    "password": "new_secret",
}
res = requests.post(f"{URL}token/", headers=FORM_DATA_HEADERS, data=credentials)
assert res.status_code == 200
