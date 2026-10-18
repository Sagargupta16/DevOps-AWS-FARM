from pydantic import BaseModel, ConfigDict


class Blog(BaseModel):
    id: str
    title: str
    content: str
    creator: str


class BlogIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    content: str
    creator: str


class BlogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    creator: str
