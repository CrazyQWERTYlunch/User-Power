"""
handlers.py

This module provides API handlers for user-related endpoints in the Education-app API.
"""
from logging import getLogger
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.actions.user import _create_new_user
from api.actions.user import _delete_user
from api.actions.user import _get_user_by_id
from api.actions.user import _update_user
from api.actions.user import check_user_permissions
from api.schemas import DeletedUserResponse
from api.schemas import ShowUser
from api.schemas import UpdatedUserRequest
from api.schemas import UpdatedUserResponse
from api.schemas import UserCreate
from db.models import User
from db.session import get_async_session

logger = getLogger(__name__)

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(
    body: UserCreate, session: AsyncSession = Depends(get_async_session)
) -> ShowUser:
    """
    Create a new user.

    Args:
        body (UserCreate): The data of the user to be created.
        session (AsyncSession): The async database session.

    Returns:
        ShowUser: The created user data.

    Raises:
        HTTPException: If a database error occurs.
    """
    try:
        return await _create_new_user(body, session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/", response_model=DeletedUserResponse)
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
) -> DeletedUserResponse:
    """
    Delete a user.

    Args:
        user_id (UUID): The ID of the user to be deleted.
        session (AsyncSession): The async database session.
        current_user (User): The current authenticated user.

    Returns:
        DeletedUserResponse: The response indicating the deleted user ID.

    Raises:
        HTTPException: If the user to be deleted is not found or if the current user doesn't have permissions.
    """
    user_for_deletion = await _get_user_by_id(user_id, session)
    if user_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if not check_user_permissions(
        target_user=user_for_deletion,
        current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")
    deleted_user_id = await _delete_user(user_id, session)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return DeletedUserResponse(deleted_user_id=deleted_user_id)


@user_router.patch("/admin_privilege", response_model=UpdatedUserResponse)
async def grant_admin_privilege(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Grant admin privilege to a user.

    Parameters:
        user_id (UUID): The ID of the user to grant admin privilege.
        db (AsyncSession, optional): The async database session.
        current_user (User, optional): The current authenticated user.

    Returns:
        UpdatedUserResponse: The response indicating the updated user ID.

    Raises:
        HTTPException: If the current user is not a superadmin, if trying to manage its own privileges,
                       if the user to be promoted already has admin or superadmin privileges,
                       if the user to be promoted is not found, or if a database error occurs.
    """
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_promotion = await _get_user_by_id(user_id, db)
    if user_for_promotion.is_admin or user_for_promotion.is_superadmin:
        raise HTTPException(
            status_code=409,
            detail=f"User with id {user_id} already promoted to admin / superadmin.",
        )
    if user_for_promotion is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    updated_user_params = {
        "roles": user_for_promotion.enrich_admin_roles_by_admin_role()
    }
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, session=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.delete("/admin_privilege", response_model=UpdatedUserResponse)
async def revoke_admin_privilege(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Revoke admin privilege from a user.

    Parameters:
        user_id (UUID): The ID of the user to revoke admin privilege.
        session (AsyncSession, optional): The async database session.
        current_user (User, optional): The current authenticated user.

    Returns:
        UpdatedUserResponse: The response indicating the updated user ID.

    Raises:
        HTTPException: If the current user is not a superadmin, if trying to manage its own privileges,
                       if the user to revoke admin privileges from is not an admin,
                       if the user to revoke admin privileges from is not found, or if a database error occurs.
    """
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_revoke_admin_privileges = await _get_user_by_id(user_id, session)
    if not user_for_revoke_admin_privileges.is_admin:
        raise HTTPException(
            status_code=409, detail=f"User with id {user_id} has no admin privileges."
        )
    if user_for_revoke_admin_privileges is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    updated_user_params = {
        "roles": user_for_revoke_admin_privileges.remove_admin_privileges_from_model()
    }
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, session=session, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    # current_user: User = Depends(get_current_user_from_token)
) -> ShowUser:
    """
    Retrieve user information by user ID.

    Parameters:
        user_id (UUID): The ID of the user to retrieve information.
        session (AsyncSession, optional): The async database session.

    Returns:
        ShowUser: The user information.

    Raises:
        HTTPException: If the user with the provided ID is not found.
    """
    user = await _get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
    user_id: UUID,
    body: UpdatedUserRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
) -> UpdatedUserResponse:
    """
    Update user information by user ID.

    Parameters:
        user_id (UUID): The ID of the user to update information.
        body (UpdatedUserRequest): The updated user information.
        session (AsyncSession, optional): The async database session.
        current_user (User, optional): The current authenticated user.

    Returns:
        UpdatedUserResponse: The response indicating the updated user ID.

    Raises:
        HTTPException: If no parameter for user update info is provided, if the user with the provided ID is not found,
                       if the current user doesn't have permissions, or if a database error occurs.
    """
    updated_users_params = body.model_dump(exclude_none=True)
    if updated_users_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user_for_update = await _get_user_by_id(user_id, session)
    if user_for_update is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    if not check_user_permissions(
        target_user=user_for_update, current_user=current_user
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")

    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_users_params, user_id=user_id, session=session
        )
    except IntegrityError as err:
        logger.error(err)
    return UpdatedUserResponse(updated_user_id=updated_user_id)
