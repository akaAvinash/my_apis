from sqlalchemy import table
from sqlmodel import SQLModel, Field, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherData(SQLModel, table=True):
    area: str = Field(primary_key=True)
    temp: float
    unit: str

class User(SQLModel, table=True):
    username: str = Field(primary_key=True)
    hashed_password: str

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session