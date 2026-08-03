from pydantic import BaseModel, ConfigDict, Field


class EnrollmentCreate(BaseModel):
    student_id: str
    course_code: str


class ScoreUpdate(BaseModel):
    score: float = Field(ge=0, le=100)


class EnrollmentResponse(EnrollmentCreate):
    model_config = ConfigDict(from_attributes=True)

    score: float | None
    grade: str | None = None
    gpa: float | None = None
