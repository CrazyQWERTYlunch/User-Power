from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UpdateUserRequest
from api.models import UpdateUserResponse
from api.models import UserCreate
from db.dals import UserDAL
from db.session import get_async_session


user_router = APIRouter()


async def _create_new_user(body: UserCreate, session: AsyncSession) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id, session: AsyncSession) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(user_id=user_id)
        return deleted_user_id


async def _update_user(
    updated_user_params: dict, user_id: UUID, session
) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params
        )
        return updated_user_id


async def _get_user_by_id(user_id, session: AsyncSession) -> Union[ShowUser, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(user_id=user_id)
        if user is not None:
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


@user_router.post("/", response_model=ShowUser)
async def create_user(
    body: UserCreate, db: AsyncSession = Depends(get_async_session)
) -> ShowUser:
    return await _create_new_user(body, db)


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> DeleteUserResponse:
    delete_user_id = await _delete_user(user_id, session)
    if delete_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return DeleteUserResponse(deleted_user_id=delete_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> ShowUser:
    user = await _get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user_by_id(
    user_id: UUID,
    body: UpdateUserRequest,
    session: AsyncSession = Depends(get_async_session),
) -> UpdateUserResponse:
    updated_users_params = body.model_dump(exclude_none=True)
    if updated_users_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user = await _get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    updated_user_id = await _update_user(
        updated_user_params=updated_users_params, user_id=user_id, session=session
    )
    return UpdateUserResponse(updated_user_id=updated_user_id)
