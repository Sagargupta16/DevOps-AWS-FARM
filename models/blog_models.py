from pydantic import BaseModel


class Blog(BaseModel):
    id: str
    title: str
    content: str
    creator: str


class BlogIn(BaseModel):
    title: str
    content: str
    creator: str

    class Config:
        orm_mode = True


class BlogOut(BaseModel):
    id: str
    title: str
    content: str
    creator: str

    class Config:
        orm_mode = True
