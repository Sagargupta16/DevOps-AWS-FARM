from fastapi import APIRouter, status
from typing import List
from models.user_models import UserIn, UserOut
from services.user_services import (
    create_user,
    get_users,
    get_user,
    delete_user,
    update_user,
)

router = APIRouter()


@router.post("/user", status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user_route(user: UserIn):
    return create_user(user)


@router.get(
    "/user",
    response_model=List[UserOut],
    status_code=status.HTTP_200_OK,
    tags=["users"],
)
def get_users_route():
    return get_users()


@router.get(
    "/user/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    tags=["users"],
)
def get_user_route(user_id: str):
    return get_user(user_id)


@router.delete("/user/{user_id}", status_code=status.HTTP_202_ACCEPTED, tags=["users"])
def delete_user_route(user_id: str):
    return delete_user(user_id)


@router.put("/user/{user_id}", status_code=status.HTTP_200_OK, tags=["users"])
def update_user_route(user_id: str, user: UserIn):
    return update_user(user_id, user)
