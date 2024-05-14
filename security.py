"""
security.py

This module provides functions related to JWT token creation.

Functions:
    create_access_token: Generate an access token.

"""
import datetime
from datetime import timedelta
from typing import Optional

from jose import jwt

import config


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generate an access token.

    Parameters:
        data (dict): Data to be encoded into the token.
        expires_delta (timedelta, optional): Expiry time for the token. If not provided,
            a default expiry time is used.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt
