import json
from test_and_fulfillment_client import Client


# DOMAIN = "77.240.38.191"
# DOMAIN = "10.0.0.7"
DOMAIN = "localhost"
PORT = 8004


with open("test_and_fulfillment/users.json", "r") as f:
    USERS = json.load(f)

with open("test_and_fulfillment/organizations.json", "r") as f:
    ORGANIZATIONS = json.load(f)

with open("test_and_fulfillment/equipment.json", "r") as f:
    EQUIPMENT = json.load(f)


# John - owner with verified organization
john_data = USERS["John"]
john_organization_inn = john_data["organization_inn"]
john_organization = ORGANIZATIONS[john_organization_inn]
john = Client(DOMAIN, PORT)

john.create_organization(john_organization["dadata_response"], john_organization["contact_data"])
john.create_user(john_data)
john._verify_my_organization()
john.update_organization_requisites(john_organization["requisites"])

# Update John's organization
john_data["organization_inn"] = "9729311480"
john_organization_inn = john_data["organization_inn"]
john_organization = ORGANIZATIONS[john_organization_inn]
john.create_organization(john_organization["dadata_response"], john_organization["contact_data"])
john.update_self({
    "organization_inn": john_organization_inn,
})
john._verify_my_organization()
john.update_organization_requisites(john_organization["requisites"])


# john.login(USERS["John"]["email"], USERS["John"]["password"])

for equipment in EQUIPMENT[john_organization_inn]:
    john.post_equipment(equipment)
