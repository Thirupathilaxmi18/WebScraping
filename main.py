from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///./courses.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Course model
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class CourseCreate(BaseModel):
    title: str
    description: str
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Software Courses API! Use /docs for API documentation."}


@app.post("/courses/")
def create_course(course: CourseCreate):
    db = SessionLocal()
    db_course = Course(title=course.title, description=course.description)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    db.close()
    return db_course

@app.get("/courses/")
def get_courses():
    db = SessionLocal()
    courses = db.query(Course).all()
    db.close()
    return courses
