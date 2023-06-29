import requests


HEADERS = {
    "Content-Type": "application/json",
    "accept": "application/json",
}

URL = "http://localhost:8004/"


users = [
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

# Init Activities table
res = requests.get(f"{URL}init_activities_db/", headers=HEADERS)
assert res.status_code == 200

# Create users
for user in users:
    res = requests.post(f"{URL}users/create/", headers=HEADERS, json=user)
    if res.status_code != 200:
        print(res.text)
        
    assert res.status_code == 200
