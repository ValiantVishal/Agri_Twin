from pydantic import BaseModel
from pydantic import EmailStr


class Register(BaseModel):

    name: str

    email: EmailStr

    password: str


class Login(BaseModel):

    email: EmailStr

    password: str


class ProfileCreate(BaseModel):
    phone: str

    state: str

    district: str

    village: str

    language: str

    farmerType: str

    experience: int

    crop: str

    irrigation: str

    soilType: str