from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    credits: int = Field(ge=1, le=20)


class CourseCreate(CourseBase):
    code: str = Field(min_length=1, max_length=20)


class CourseUpdate(CourseBase):
    pass


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    code: str
