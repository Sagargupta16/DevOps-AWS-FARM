from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str


class UserIn(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        orm_mode = True
