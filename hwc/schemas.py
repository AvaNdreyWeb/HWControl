from pydantic import BaseModel
from datetime import date
from typing import Dict
from uuid import UUID

class GroupBase(BaseModel):
    id: str 
    title: str


class GroupCreate(GroupBase):
    ...
    class Config:
        schema_extra = {
            "example": {
                "id": "eng-1",
                "title": "English (Base)",
            }
        }


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
    class Config:
        schema_extra = {
            "example": {
                "firstname": "Ivan",
                "lastname": "Ivanov",
                "groups": ["eng-1", "inf-2", "js-1"]
            }
        }


class StudentDB(StudentBase):
    id: UUID

    class Config:
        orm_mode = True


class Student(StudentDB):
    groups: list[str]


class LessonBase(BaseModel):
    title: str
    group_id: str
    date: date
    homework: str | None = None


class LessonCreate(LessonBase):
    ...
    class Config:
        schema_extra = {
            "example": {
                "title": "Present Simple",
                "group_id": "eng-1",
                "date": "2023-05-22",
                "homework": "workbook: ex.1, ex.2 (p.23)"
            }
        }


class LessonDB(LessonBase):
    id: str
    is_active: bool
    control: Dict[str, list[bool]]

    class Config:
        orm_mode = True


class Lesson(LessonDB):
    students: list[Student]

    class Config:
        schema_extra = {
            "example": {
                "title": "Present Simple",
                "group_id": "eng-1",
                "date": "2023-05-22",
                "homework": "workbook: ex.1, ex.2 (p.23)",
                "id": "2023-05-22",
                "is_active": True,
                "control": {
                    "UUID_1": [
                    True,
                    False
                    ],
                    "UUID_2": [
                    False,
                    True
                    ]
                },
                "students": [
                    {"firstname": "Ivan", "lastname": "Ivanov", "id": "UUID_1"},
                    {"firstname": "Jhon", "lastname": "Smith", "id": "UUID_2"}
                ]
            }
        }

class SuccessPostResponse(BaseModel):
    detail: str
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Successfully created",
            }
        }
