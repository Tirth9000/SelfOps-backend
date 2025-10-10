from beanie import Document, Link
from pydantic import EmailStr
from passlib.context import CryptContext
from routes.WEB.auth import hash_password
 # Import from auth.py

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class User(Document):
    username: str
    email: EmailStr
    password: str

    class Settings:
        name = "users"

    def set_password(self, plain_password: str):
        self.password = hash_password(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        # Fallback for plain text passwords (legacy users)
        if not self.password.startswith('$'):  # Plain text check (no hash prefix)
            return self.password == plain_password
        return pwd_context.verify(plain_password, self.password)


class Applications(Document):
    app_name: str
    user_id: Link[User]

    class Settings:
        name = "applications"


class ContainerStats(Document):
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