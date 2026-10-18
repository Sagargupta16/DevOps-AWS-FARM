from pydantic import BaseModel, ConfigDict, field_validator

# bcrypt only reads the first 72 bytes of a password and bcrypt>=5 rejects longer input
BCRYPT_MAX_BYTES = 72


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str


class UserIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"password must be at most {BCRYPT_MAX_BYTES} bytes")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
