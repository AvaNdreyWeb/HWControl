from sqlalchemy.orm import Session
import datetime
import uuid
from . import models, schemas
from typing import Dict
from datetime import date

# Lesson
def create_lesson(db: Session, lesson: schemas.LessonCreate):
    ''' ... '''
    students = get_students_by_group(db, lesson.group_id)
    control = dict()
    for student in students:
        control[str(student.id)] = [False, False]
    db_lesson_schema = schemas.LessonDB(**lesson.dict(), id=f'{lesson.date}', is_active=True, status=control)
    db_lesson = models.Lesson(**db_lesson_schema.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


def get_lesson(db: Session, date: datetime.date):
    ''' Function return Lesson by date or None '''
    return db.query(models.Lesson).filter(models.Lesson.date == date).first()


def deactivate_lesson(db: Session, date: datetime.date, control: Dict[str, list[bool]]):
    ''' ... '''
    db_lesson = get_lesson(db, date)
    if db_lesson:
        db_lesson.is_active = False
        db_lesson.status = control
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson

# Student
def create_student(db: Session, student: schemas.StudentCreate):
    ''' ... '''
    db_student_schema = schemas.StudentDB(**student.dict(), id=uuid.uuid4())
    db_student = models.Student(
        id=db_student_schema.id,
        firstname=db_student_schema.firstname,
        lastname=db_student_schema.lastname
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    for group_id in student.groups:
        db_student_group = models.StudentGroup(student_id=db_student.id, group_id=group_id)
        db.add(db_student_group)
        db.commit()
        db.refresh(db_student_group)
    return db_student


def get_students(db: Session, page: int = 1, limit: int = 10):
    filter_field = models.Student.lastname
    return db.query(models.Student).order_by(filter_field).offset((page-1)*limit).limit(limit).all()


def get_students_by_group(db: Session, group_id: str):
    group_db = db.query(models.Group).filter(models.Group.id == group_id).first()
    if group_db:
        return students
    return []

# Group
def create_group(db: Session, group: schemas.GroupCreate):
    ''' ... '''
    db_group_schema = schemas.GroupDB(**group.dict())
    db_group = models.Group(**db_group_schema.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def get_groups(db: Session, page: int = 1, limit: int = 10, filter: str = 'title'):
    filter_field = models.Group.title
    if filter == 'group_id':
        filter_field = models.Group.id
    return db.query(models.Group).order_by(filter_field).offset((page-1)*limit).limit(limit).all()


def get_group_by_id(db: Session, group_id: str):
    return db.query(models.Group).filter(models.Group.id == group_id).first()


def get_current_month(db: Session, y: int, m: int):
    last = (date(y, m, 1) - date(y, m+1, 1)).days
    db_lessons = db.query(models.Lesson).filter(models.Lesson.date >= f'{y}-{m}-01', models.Lesson.date <= f'{y}-{m}-{last}').all()
    return [{x.id: x.is_active} for x in db_lessons]
