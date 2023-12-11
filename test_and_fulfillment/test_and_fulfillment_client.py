import requests


DOC_TYPES = {
    "txt": "text/plain",
    "html": "text/html",
    "xml": "text/xml",
    "csv": "text/csv",
    "json": "application/json",
    "pdf": "application/pdf",
    "crt": "application/pkix-cert",
    "p7s": "application/pkcs7-signature",
    "docx": "application/wps-office.docx",
    "xlsx": "application/wps-office.xlsx",
    "pptx": "application/wps-office.pptx",
    "jpg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "svg": "image/svg+xml",
    "webp": "image/webp",
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    "mpg": "video/mpeg",
    "mpeg": "video/mpeg",
    "mov": "video/quicktime",
    "wmv": "video/x-ms-wmv",
    "flv": "video/x-flv",
    "ogg": "video/ogg",
    "webm": "video/webm",
    "mkv": "video/x-matroska",
}


class Client:

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

    def __init__(self, domen: str, port: int, protocol: str = "http"):
        self.url = f"{protocol}://{domen}:{port}/"
        self.AUTH_HEADERS = self.HEADERS
        self.FILE_UPLOAD_HEADERS = self.BASE_HEADERS

    def login(self, username: str, password: str) -> str:
        credentials = {
            "username": username,
            "password": password,
        }
        response = requests.post(
            url=f"{self.url}login/",
            headers=self.FORM_DATA_HEADERS,
            data=credentials,
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        self.AUTH_HEADERS = {
            **self.HEADERS,
            "Authorization": f"Bearer {token}",
        }
        self.FILE_UPLOAD_HEADERS = {
            **self.BASE_HEADERS,
            "Authorization": f"Bearer {token}",
        }

    def logout(self):
        self.AUTH_HEADERS = self.HEADERS
        self.FILE_UPLOAD_HEADERS = self.BASE_HEADERS

    def create_user(self, user: dict) -> dict:
        response = requests.post(
            url=f"{self.url}users/",
            headers=self.AUTH_HEADERS,
            json=user,
        )
        assert response.status_code == 201
        self.login(user["email"], user["password"])

    def get_user(self, user_id: int) -> dict:
        response = requests.get(
            url=f"{self.url}users/{user_id}/",
            headers=self.HEADERS,
        )
        assert response.status_code == 200
        return response.json()
    
    def get_self(self) -> dict:
        response = requests.get(
            url=f"{self.url}users/me/",
            headers=self.AUTH_HEADERS,
        )
        assert response.status_code == 200
        return response.json()
    
    def update_self(self, user: dict) -> dict:
        response = requests.put(
            url=f"{self.url}users/me/",
            headers=self.AUTH_HEADERS,
            json=user,
        )
        assert response.status_code == 202
        return response.json()
    
    def _add_organization_contacts(self, inn: str, contacts: dict) -> dict:
        response = requests.put(
            url=f"{self.url}organizations/{inn}/contacts/",
            headers=self.HEADERS,
            json=contacts,
        )
        assert response.status_code == 202
        return response.json()

    def create_organization(self, organization: dict, contacts: dict = None) -> dict:
        response = requests.post(
            url=f"{self.url}organizations/",
            headers=self.HEADERS,
            json=organization,
        )
        assert response.status_code == 200
        response = response.json()

        if contacts is None:
            return response
        
        inn = response["inn"]
        return self._add_organization_contacts(inn, contacts)

    def update_organization_requisites(self, requisites: dict) -> dict:
        response = requests.put(
            url=f"{self.url}organizations/requisites/",
            headers=self.AUTH_HEADERS,
            json=requisites,
        )
        assert response.status_code == 202
        return response.json()
    
    def _verify_my_organization(self) -> dict:
        me = self.get_self()
        response = requests.patch(
            url=f"{self.url}users/{me['id']}/verify/",
            headers=self.HEADERS,
        )
        assert response.status_code == 202
        return response.json()

    def post_equipment(self, equipment: dict) -> dict:

        documents_ids = []
        for doc_path in equipment.pop("documents"):
            with open(doc_path, "rb") as file:
                files = {'document': (doc_path, file, DOC_TYPES[doc_path.split(".")[-1]] if "." in doc_path else "application/")}
                response = requests.post(
                    url=f"{self.url}equipment/document/",
                    files=files,
                    headers=self.FILE_UPLOAD_HEADERS,
                )
                assert response.status_code == 200
                documents_ids.append(response.json()["id"])

        photo_and_video_ids = []
        for media_path in equipment.pop("photo_and_video"):
            with open(media_path, "rb") as file:
                files = {'media': (media_path, file, DOC_TYPES[media_path.split(".")[-1]] if "." in media_path else "application/")}
                response = requests.post(
                    url=f"{self.url}equipment/media/",
                    files=files,
                    headers=self.FILE_UPLOAD_HEADERS,
                )
                assert response.status_code == 200
                photo_and_video_ids.append(response.json()["id"])

        equipment["documents_ids"] = documents_ids
        equipment["photo_and_video_ids"] = photo_and_video_ids

        response = requests.post(
            url=f"{self.url}equipment/",
            headers=self.AUTH_HEADERS,
            json=equipment,
        )
        assert response.status_code == 200
        return response.json()
