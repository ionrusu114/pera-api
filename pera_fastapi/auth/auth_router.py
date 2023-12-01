from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from pera_fastapi.auth.auth import auth_backend, fastapi_users, get_user_manager
from .schemas import UserRead

router = APIRouter()

@router.post("/loginUser")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), user_manager=Depends(get_user_manager)):
    user = await user_manager.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return await auth_backend.get_login_response(user, response)