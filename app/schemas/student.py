from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    year: int = Field(ge=1, le=8)


class StudentCreate(StudentBase):
    student_id: str = Field(min_length=1, max_length=20)


class StudentUpdate(StudentBase):
    pass


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    department: str
