from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(max_length=120)
    
class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    # email will be added later but it will be divided as public and pvt since will be a safety concern in real-world scenario
    image_file: str | None
    image_path: str

# type validation for creating and returning posts
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    # author will come from relationships


# To create posts
class PostCreate(PostBase):
    user_id: int # TEMP


# for post response
class PostResponse(PostBase):
    model_config = ConfigDict(  # it help pydantic to read from sqlalchemy model and it allows read property
        from_attributes=True
    )  # from_attributes allows to read data from dot notations, which will be helpful for pydantic during API calling for data

    # for databases and API id can be used so no need to use uid
    id: int
    user_id: int
    date_posted: datetime # will be automatically converted to ISO 8060 format, so no need to serialize or custom conversion
    author: UserResponse
