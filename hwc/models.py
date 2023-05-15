from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from .database import Base, engine
import uuid

class StudentGroup(Base):
    __tablename__ = 'student_group'

    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'), primary_key=True)
    group_id = Column(String, ForeignKey('groups.id'), primary_key=True)


class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    

    students = relationship("Student", secondary="student_group", back_populates="groups")
    lessons = relationship("Lesson", back_populates="group")

class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = Column(String)
    lastname = Column(String)

    groups = relationship("Group", secondary="student_group", back_populates="students")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    date = Column(Date)
    title = Column(String)
    homework = Column(String)
    group_id = Column(String, ForeignKey("groups.id"))

    status = Column(JSON)

    group = relationship("Group", back_populates="lessons")


class Subscription(Base):
    __tablename__ = 'subscription'

    student_id = Column(UUID(as_uuid=True))
    chat_id = Column(String, primary_key=True)


Base.metadata.create_all(engine)
