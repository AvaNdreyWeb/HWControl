from pydantic import BaseModel
from datetime import date
from uuid import UUID

class GroupBase(BaseModel):
    id: str 
    title: str


class GroupCreate(GroupBase):
    ...


class GroupDB(GroupBase):
    ...

    class Config:
        orm_mode = True


class Group(GroupDB):
    ...



class StudentBase(BaseModel):
    firstname: str
    lastname: str
    


class StudentCreate(StudentBase):
    groups: list[str]


class StudentDB(StudentBase):
    id: UUID

    class Config:
        orm_mode = True


class Student(StudentDB):
    ...


class LessonBase(BaseModel):
    title: str
    group_id: str
    date: date
    homework: str | None = None


class LessonCreate(LessonBase):
    ...


class LessonDB(LessonBase):
    id: str
    is_active: bool

    class Config:
        orm_mode = True


class Lesson(LessonDB):
    students: list[Student]
