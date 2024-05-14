"""
dals.py

This module provides Data Access Layer (DAL) classes for interacting with the database
in a business context.
"""
from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import PortalRole
from db.models import User


class UserDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the UserDAL instance.

        Args:
            db_session (AsyncSession): AsyncSession instance for interacting with the database.
        """
        self.db_session = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        hashed_password: str,
        roles: list[PortalRole],
    ) -> User:
        """
        Create a new user.

        Args:
            name (str): The user's name.
            surname (str): The user's surname.
            email (str): The user's email address.
            hashed_password (str): The hashed password for the user.
            roles (list[PortalRole]): The roles assigned to the user.

        Returns:
            User: The newly created user object.
        """
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        """
        Delete a user.

        Args:
            user_id (UUID): The ID of the user to delete.

        Returns:
            Union[UUID, None]: The ID of the deleted user, or None if the user was not found.
        """
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        """
        Get a user by ID.

        Args:
            user_id (UUID): The ID of the user to retrieve.

        Returns:
            Union[User, None]: The user object if found, otherwise None.
        """
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        """
        Get a user by email.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            Union[User, None]: The user object if found, otherwise None.
        """
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        """
        Update a user.

        Args:
            user_id (UUID): The ID of the user to update.
            **kwargs: Keyword arguments representing the fields to update and their new values.

        Returns:
            Union[UUID, None]: The ID of the updated user, or None if the user was not found.
        """
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]
