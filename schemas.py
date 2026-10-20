from pydantic import BaseModel, ConfigDict, Field


# type validation for creating and returning posts
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)


# To create posts
class PostCreate(PostBase):
    pass


# for post response
class PostResponse(PostBase):
    model_config = ConfigDict(
        from_attributes=True
    )  # from_attributes allows to read data from dot notations, which will be helpful for pydantic during API calling for data

    # for databases and API id can be used so no need to use uid
    id: int
    date_posted: str
