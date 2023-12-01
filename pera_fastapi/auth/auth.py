from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy,BearerTransport
from fastapi_users import FastAPIUsers
from .database import User
from pera_fastapi.settings import settings
from .manager import get_user_manager

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret_auth, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_name="PeraUser",cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()