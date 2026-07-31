from pydantic import BaseModel
from pydantic import EmailStr


class Register(BaseModel):

    name: str

    email: EmailStr

    password: str


class Login(BaseModel):

    email: EmailStr

    password: str