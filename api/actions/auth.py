"""
auth.py

This module provides functions for user authentication and authorization in the Education-app API.
"""
from typing import Union

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import config
from db.dals import UserDAL
from db.models import User
from db.session import get_async_session
from hashing import Hasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def _get_user_by_email_for_auth(email: str, session: AsyncSession):
    """
    Retrieve a user by email for authentication purposes.

    Args:
        email (str): The email address of the user.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        User: The user object if found, otherwise None.
    """
    async with session.begin():
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_email(
            email=email,
        )


async def authenticate_user(
    email: str, password: str, session: AsyncSession
) -> Union[User, None]:
    """
    Authenticate a user with email and password.

    Args:
        email (str): The email address of the user.
        password (str): The password of the user.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        Union[User, None]: The authenticated user object if successful, otherwise None.
    """
    user = await _get_user_by_email_for_auth(email=email, session=session)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Retrieve the current user from the authentication token.

    Args:
        token (str): The authentication token.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_for_auth(email=email, session=session)
    if user is None:
        raise credentials_exception
    return user
