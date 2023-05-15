import datetime
import re
from fastapi import Depends, FastAPI, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Annotated, Union

from . import crud, models, schemas
from .database import SessionLocal, engine

from aiogram import types, Dispatcher, Bot
from .bot import dp, bot, TOKEN, send_message_to_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HWControl")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# groups
@app.post(
    "/groups/create",
    response_model=schemas.SuccessPostResponse,
    tags=["groups"],
    summary="Create a group",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"detail": "Group successfully created"}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"detail": "Group already exists"}
                }
            }
        },
        422: {
            "content": {
                "application/json": {
                    "example": {"detail": "Group id must contain only latin "
                                          "letters, numbers and dashes"}
                }
            }
        }
    }
)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    group.id = group.id.lower()
    slug = re.search("^[a-z0-9\-]+$", group.id)
    if not slug:
        raise HTTPException(
            status_code=422,
            detail="Group id must contain only "
                   "latin letters, numbers and dashes"
        )
    db_group = crud.get_group_by_id(db, group.id)
    if db_group:
        raise HTTPException(status_code=409, detail="Group already exists")
    new_group = crud.create_group(db, group)
    if new_group:
        return {"detail": "Group successfully created"}

@app.get(
    "/groups",
    response_model=list[schemas.Group],
    tags=["groups"],
    summary="Get list of created groups",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "eng-1",
                            "title": "English (Base)" 
                        },
                        {
                            "id": "eng-2",
                            "title": "English (Advanced)" 
                        },
                        {
                            "id": "eng-3",
                            "title": "English (Pro)" 
                        }
                    ]
                }
            }
        }
    }
)
def get_groups(
    page: Annotated[Union[int, None], Query(gt=0)] = 1,
    limit: Union[int, None] = 10,
    filter: Union[str, None] = "title",
    db: Session = Depends(get_db)
):
    """
    The **page** must be greater than **0**

    Avalible **filter** values:
    - title
    - group_id
    """
    return crud.get_groups(db, page, limit, filter)


# lessons
@app.post(
    "/lessons/create",
    response_model=schemas.SuccessPostResponse,
    tags=["lessons"],
    summary="Create a lesson",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"detail": "Lesson successfully created"}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"detail": "Lesson already exists"}
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "Matching group does not exist"}
                }
            }
        }
    }
)
def create_lesson(lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    db_lesson = crud.get_lesson(db, date=lesson.date)
    if db_lesson:
        raise HTTPException(status_code=409, detail="Lesson already exists")
    lesson.group_id = lesson.group_id.lower()
    db_group = crud.get_group_by_id(db, lesson.group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Matching group does not exist")
    new_lesson = crud.create_lesson(db, lesson)
    if new_lesson:
        return {"detail": "Lesson successfully created"}


@app.get(
    "/lessons/{date}",
    response_model=schemas.Lesson,
    tags=["lessons"],
    summary="Get current lesson",
    responses={
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "Lesson not found"}
                }
            }
        }
    }
)
def get_lesson(date: datetime.date, db: Session = Depends(get_db)):
    """
    The **control** field structure:
    |Student`s id (UUID)                     |present (bool)|hw_done (bool)|
    |----------------------------------------|--------------|--------------|
    |**d0a3df51-1c67-4daf-a883-9f5fbae071dd**|true          |false         |
    |**8fff91df-303a-4b04-8d52-6986f8d7ebc0**|false         |true          |
    """
    db_lesson = crud.get_lesson(db, date)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_students = crud.get_students_by_group(db, db_lesson.group_id)
    lesson = schemas.Lesson(
        id=db_lesson.id,
        date=db_lesson.date,
        title=db_lesson.title,
        group_id=db_lesson.group_id,
        homework=db_lesson.homework,
        is_active=db_lesson.is_active,
        control=db_lesson.status,
        students = db_students
    )
    return lesson

@app.put(
    "/lessons/{date}",
    #response_model=schemas.SuccessPostResponse,
    tags=["lessons"],
    summary="Finish current lesson",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"detail": "Lesson successfully finished"}
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "Lesson not found"}
                }
            }
        },
    }
)
async def finish_lesson(
    date: datetime.date,
    control: Annotated[Dict[str, list[bool]], Body(example={
                "UUID_1": [
                    True,
                    False
                    ],
                "UUID_2": [
                    False,
                    True
                    ]
            })],
    db: Session = Depends(get_db)
):
    """
    The **control** field structure:
    |Student`s id (UUID)                     |present (bool)|hw_done (bool)|
    |----------------------------------------|--------------|--------------|
    |**d0a3df51-1c67-4daf-a883-9f5fbae071dd**|true          |false         |
    |**8fff91df-303a-4b04-8d52-6986f8d7ebc0**|false         |true          |
    """
    db_lesson = crud.get_lesson(db, date)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    crud.deactivate_lesson(db, date, control)
    subscriptions = crud.get_subscriptions(db)
    chats = []
    #debug = []
    if subscriptions:
        for student_id in control:
            present = control[student_id][0]
            hw_done = control[student_id][1]
            for subscription in subscriptions:
                #debug.append([subscription.student_id, student_id, subscription.student_id==student_id, str(subscription.student_id)==str(student_id)])
                if str(subscription.student_id)==str(student_id):
                    chats.append([subscription.chat_id, present, hw_done])
        for chat in chats:
            msg = f'present: {chat[1]}\nhw_done: {chat[2]}'
            await send_message_to_user(chat[0], msg)
    return {"detail": "Lesson successfully finished", 'debug': chats}

# students
@app.post(
    "/students/create",
    response_model=schemas.SuccessPostResponse,
    tags=["students"],
    summary="Create a student",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"detail": "Student successfully created"}
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "Matching group does not exist"}
                }
            }
        }
    }
)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    for i in range(len(student.groups)):
        student.groups[i] = student.groups[i].lower()
        group = student.groups[i]
        db_group = crud.get_group_by_id(db, group)
        if not db_group:
            raise HTTPException(status_code=404, detail=f"Matching group -> \"{group}\" does not exist")
    new_student = crud.create_student(db, student)
    return {"detail": "Student successfully created"}

@app.get(
    "/students",
    response_model=list[schemas.Student],
    tags=["students"],
    summary="Get list of created students",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "firstname": "Ivan",
                            "lastname": "Ivanov",
                            "id": "UUID_1",
                            "groups": ["eng-2", "inf-1"]
                        },
                        {
                            "firstname": "Jhon",
                            "lastname": "Smith",
                            "id": "UUID_2",
                            "groups": ["inf-3"]
                        },
                    ]
                }
            }
        }
    }
)
def get_students(
    page: Annotated[Union[int, None], Query(gt=0)] = 1,
    limit: Union[int, None] = 10,
    db: Session = Depends(get_db)
):
    """
    The **page** must be greater than **0**
    """
    db_student_list = crud.get_students(db, page, limit)
    request = []
    for db_student in db_student_list:
        student = schemas.Student(
            firstname=db_student.firstname,
            lastname=db_student.lastname,
            id=db_student.id,
            groups=[x.id for x in db_student.groups]
        )
        request.append(student)
    return request

# calendar
@app.get(
    "/api", response_model=list[Dict[str, bool]],
    tags=["calendar"],
    summary="Get list of dates and statuses of created lessons",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {"2023-05-04": False},
                        {"2023-05-11": False},
                        {"2023-05-18": False},
                        {"2023-05-25": True},
                        {"2023-05-30": True},
                    ]
                }
            }
        }
    }
)
def get_month_dates_status(year: int, month: int, db: Session = Depends(get_db)):
    return crud.get_current_month(db, year, month)


SERVER = "https://hw-control-git-tg-bot-avandreyweb.vercel.app"
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = SERVER + WEBHOOK_PATH


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()


@app.post('/bot/subscribe')
def subscribe(data: Dict[str, str], db: Session = Depends(get_db)):
    return crud.update_subscribe(db, data)
