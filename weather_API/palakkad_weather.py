from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from starlette import status
from database import engine, get_session, WeatherData
from sqlmodel import Session, select

@asynccontextmanager
async def lifespan(app: FastAPI):
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

class AddWeatherData(BaseModel):
    area: str = Field(min_length=1)
    temp: float
    unit: str

class UpdateWeatherData(BaseModel):
    temp: float
    unit: str

weather_data = {}

@app.get("/weather/{area}")
def get_weather(area: str, session: Session = Depends(get_session)):
    weather = session.get(WeatherData, area)
    if weather:
        return weather
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Weather not found for {area}")

@app.get("/weather/")
def get_weather_dump(session: Session = Depends(get_session)):
    weather = session.exec(select(WeatherData)).all()
    return weather

@app.post("/weather")
def post_weather(data: AddWeatherData, session: Session = Depends(get_session)):
    existing = session.get(WeatherData, data.area)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Weather for {data.area} already exists.")
    weather = WeatherData(area=data.area, temp=data.temp, unit=data.unit)
    session.add(weather)
    session.commit()
    session.refresh(weather)

    return {"message": f"Weather {data.area} added."}

@app.delete("/weather/{area}")
def delete_weather(area: str, session: Session = Depends(get_session)):
    weather = session.get(WeatherData, area)
    if weather:
        session.delete(weather)
        session.commit()
        return {"message": f"Weather {area} deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Weather not found for {area}")

@app.put("/weather/{area}")
def put_weather(area: str, data: UpdateWeatherData, session: Session = Depends(get_session)):
    weather = session.get(WeatherData, area)
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather not found for {area}"
        )

    weather.temp = data.temp
    weather.unit = data.unit

    session.add(weather)
    session.commit()
    session.refresh(weather)

    return {
        "message": f"Weather for {area} updated successfully."
    }