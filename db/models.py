from beanie import Document, Link
from pydantic import EmailStr
from passlib.context import CryptContext
from routes.WEB.utils import hash_password, verify_password

 # Import from auth.py


class User(Document):
    username: str
    email: EmailStr
    password: str

    class Settings:
        name = "users"

    def set_password(self, plain_password: str):
        self.password = hash_password(plain_password)

    def verify_password(self, raw_password: str) -> bool:
        return verify_password(raw_password, self.password)


class Applications(Document):
    app_name: str
    user_id: Link[User]

    class Settings:
        name = "applications"


class AppContainers(Document):
    app_id: Link[Applications]
    container_id: str
    container_name: str
    image: str
    status: str
    uptime: str
    restart_count: int
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    network_io: dict
    ports: dict
    health: str

    class Settings:
        name = "container_stats"
        extra = "allow"

class SharedResourcesModel(Document):
    app_id : Link[Applications]
    accessed_user_id:Link[User]
    class Settings:
        name = "shared_resources"