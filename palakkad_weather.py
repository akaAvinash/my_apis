from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class AddWeatherData(BaseModel):
    area: str = Field(min_length=1)
    temp: float
    unit: str

weather_data = {}

@app.get("/weather/{area}")
def get_weather(area: str):
    return weather_data[area]

@app.post("/weather")
def post_weather(data: AddWeatherData):
    weather_data[data.area] = {
        "temp": data.temp,
        "unit": data.unit
    }