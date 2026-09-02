from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from starlette import status
from database import engine, get_session, WeatherData, User
from auth import hash_password, verify_password, create_access_token, get_current_user
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm

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

class RegisterUser(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

@app.get("/weather/{area}")
def get_weather(area: str, session: Session = Depends(get_session),
                 current_user: User = Depends(get_current_user)):
    weather = session.get(WeatherData, area)
    if weather:
        return weather
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Weather not found for {area}")

@app.get("/weather/")
def get_weather_dump(session: Session = Depends(get_session),
                      current_user: User = Depends(get_current_user)):
    weather = session.exec(select(WeatherData)).all()
    return weather

@app.post("/weather")
def post_weather(data: AddWeatherData, session: Session = Depends(get_session),
                  current_user: User = Depends(get_current_user)):
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
def delete_weather(area: str, session: Session = Depends(get_session),
                    current_user: User = Depends(get_current_user)):
    weather = session.get(WeatherData, area)
    if weather:
        session.delete(weather)
        session.commit()
        return {"message": f"Weather {area} deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Weather not found for {area}")

@app.put("/weather/{area}")
def put_weather(area: str, data: UpdateWeatherData, session: Session = Depends(get_session),
                 current_user: User = Depends(get_current_user)):
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

@app.post("/register")
def register_user(data: RegisterUser, session: Session = Depends(get_session)):
    existing = session.get(User, data.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User {data.username} already exists.")

    user = User(username=data.username, hashed_password=hash_password(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": f"User {data.username} registered successfully."}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.get(User, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}