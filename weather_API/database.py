from sqlalchemy import table
from sqlmodel import SQLModel, Field, create_engine, Session

class WeatherData(SQLModel, table=True):
    area: str = Field(primary_key=True)
    temp: float
    unit: str

class User(SQLModel, table=True):
    user: str = Field(primary_key=True)
    hashed_password: str

sqlite_filename = "weather.db"
sqlite_url = f"sqlite:///{sqlite_filename}"

engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session