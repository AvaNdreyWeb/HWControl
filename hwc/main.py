import datetime
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# lessons
@app.post("/lessons/create", response_model=schemas.LessonDB, tags=['lessons'])
def create_lesson(lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    db_lesson = crud.get_lesson(db, date=lesson.date)
    if db_lesson:
        raise HTTPException(status_code=400, detail="Lesson already exists")
    return crud.create_lesson(db, lesson)


@app.get("/lessons/{date}", response_model=schemas.Lesson, tags=['lessons'])
def get_lesson(date: datetime.date, db: Session = Depends(get_db)):
    db_lesson = crud.get_lesson(db, date)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_students = crud.get_students_by_group(db, db_lesson.group_id)
    db_lesson.students = db_students
    return db_lesson

# students
@app.post("/students/create", response_model=schemas.StudentDB, tags=['students'])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, student)

@app.get("/students", response_model=list[schemas.Student], tags=['students'])
def get_students(page: int | None = 1, limit: int | None = 10, filter: str | None = 'bio', db: Session = Depends(get_db)):
    return crud.get_students(db, page, limit, filter)

# groups
@app.post("/groups/create", response_model=schemas.GroupDB, tags=['groups'])
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    db_group = crud.get_group_by_id(db, group.id)
    if db_group:
        raise HTTPException(status_code=400, detail="Group already exists")
    return crud.create_group(db, group)

@app.get("/groups", response_model=list[schemas.Group], tags=['groups'])
def get_groups(page: int | None = 1, limit: int | None = 10, filter: str | None = 'title', db: Session = Depends(get_db)):
    return crud.get_groups(db, page, limit, filter)
