"""
user.py

This module provides functions for user management in the Education-app API.
"""
from typing import Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import ShowUser
from api.schemas import UserCreate
from db.dals import UserDAL
from db.models import PortalRole
from db.models import User
from hashing import Hasher


async def _create_new_user(body: UserCreate, session: AsyncSession) -> ShowUser:
    """
    Create a new user.

    Args:
        body (UserCreate): UserCreate schema containing user information.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        ShowUser: ShowUser schema representing the newly created user.
    """
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
            roles=[
                PortalRole.ROLE_PORTAL_USER,
            ],
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id, session: AsyncSession) -> Union[UUID, None]:
    """
    Delete a user.

    Args:
        user_id (UUID): The ID of the user to delete.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        Union[UUID, None]: The ID of the deleted user, or None if the user was not found.
    """
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(user_id=user_id)
        return deleted_user_id


async def _update_user(
    updated_user_params: dict, user_id: UUID, session
) -> Union[UUID, None]:
    """
    Update a user.

    Args:
        updated_user_params (dict): Dictionary containing updated user parameters.
        user_id (UUID): The ID of the user to update.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        Union[UUID, None]: The ID of the updated user, or None if the user was not found.
    """
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params
        )
        return updated_user_id


async def _get_user_by_id(user_id, session) -> Union[User, None]:
    """
    Get a user by ID.

    Args:
        user_id (UUID): The ID of the user to retrieve.
        session (AsyncSession): AsyncSession instance for database interaction.

    Returns:
        Union[User, None]: The user object if found, otherwise None.
    """
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user


def check_user_permissions(target_user: User, current_user: User) -> bool:
    """
    Check user permissions for specific operations.

    Args:
        target_user (User): The user for which permissions are being checked.
        current_user (User): The current user performing the operation.

    Returns:
        bool: True if the current user has permission, False otherwise.
    """
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    if target_user.user_id != current_user.user_id:
        # check admin role
        if not {
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN,
        }.intersection(current_user.roles):
            return False
        # check admin deactivate superadmin attempt
        if (
            PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
        # check admin deactivate admin attempt
        if (
            PortalRole.ROLE_PORTAL_ADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
    return True
