"""
login_handlers.py

This module provides endpoints related to user authentication, such as generating access tokens.

Endpoints:
    - `/token`: HTTP POST method to generate an access token for user authentication.

"""
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import config
from api.actions.auth import authenticate_user
from api.schemas import Token
from db.session import get_async_session
from security import create_access_token


login_router = APIRouter()


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Endpoint to generate access token for user authentication.

    Parameters:
        form_data (OAuth2PasswordRequestForm): Form data containing username and password.
        session (AsyncSession, optional): The async database session.

    Returns:
        Token: The generated access token.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @login_router.get("/test_auth_endpoint")
# async def sample_endpoint_under_jwt(current_user: User = Depends(get_current_user_from_token)):
#     return {"Success": True, "current_user": current_user}
