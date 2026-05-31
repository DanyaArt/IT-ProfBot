from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    question_id = Column(Integer)
    answer_value = Column(Integer)
    session_id = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class Specialization(Base):
    __tablename__ = 'specializations'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    tech_score = Column(Float)
    analytic_score = Column(Float)
    creative_score = Column(Float)
    careers = Column(Text)

class University(Base):
    __tablename__ = 'universities'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    specialization_id = Column(Integer)
    score_min = Column(Float)
    score_max = Column(Float)
    location = Column(String(50))
    url = Column(String(200))

class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    session_id = Column(String)
    current_question = Column(Integer, default=1)
    answers = Column(Text)  # JSON string
    is_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    options = Column(Text)  # JSON string with options
    category = Column(String(50))  # tech, analytic, creative
    created_at = Column(DateTime, default=datetime.now) 