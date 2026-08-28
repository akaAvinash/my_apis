from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class AddWeatherData(BaseModel):
    area: str = Field(min_length=1)
    temp: float
    unit: str

class UpdateWeatherData(BaseModel):
    temp: float
    unit: str

weather_data = {}

@app.get("/weather/{area}")
def get_weather(area: str):
    if area in weather_data:
        return weather_data[area]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Weather not found for {area}")

@app.get("/weather/")
def get_weather_dump():
    return weather_data

@app.post("/weather")
def post_weather(data: AddWeatherData):
    if data.area not in weather_data:
        weather_data[data.area] = {
            "temp": data.temp,
            "unit": data.unit
        }
        return {"message": f"Weather {data.area} added."}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Weather for {data.area} already exists.")

@app.delete("/weather/{area}")
def delete_weather(area: str):
    if area in weather_data:
        del weather_data[area]
        return {"message": f"Weather {area} deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Weather not found for {area}")
@app.put("/weather/{area}")
def put_weather(area: str, data: UpdateWeatherData):
    if area not in weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather not found for {area}"
        )

    weather_data[area] = {
        "temp": data.temp,
        "unit": data.unit
    }

    return {
        "message": f"Weather for {area} updated successfully."
    }