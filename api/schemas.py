"""
schemas.py

This module provides Pydantic models for data validation and serialization in the Education-app API.
"""
import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import field_validator

#########################
# BLOCK WITH API MODELS #
#########################

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """Configurations for Pydantic models."""

        from_attribures = True


class ShowUser(TunedModel):
    """
    Pydantic model for showing user information.
    """

    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    """
    Pydantic model for creating a new user.
    """

    name: str
    surname: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """
        Validate the name field to contain only letters.
        """
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @field_validator("surname")
    @classmethod
    def validate_surname(cls, value):
        """
        Validate the surname field to contain only letters.
        """
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class DeletedUserResponse(BaseModel):
    """
    Pydantic model for the response after deleting a user.
    """

    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    """
    Pydantic model for the response after updating a user.
    """

    updated_user_id: uuid.UUID


class UpdatedUserRequest(BaseModel):
    """
    Pydantic model for the request to update a user.
    """

    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """
        Validate the name field to contain only letters.
        """
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @field_validator("surname")
    @classmethod
    def validate_surname(cls, value):
        """
        Validate the surname field to contain only letters.
        """
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class Token(BaseModel):
    """
    Pydantic model for JWT token.
    """

    access_token: str
    token_type: str
