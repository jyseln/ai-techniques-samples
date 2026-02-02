from pydantic import BaseModel, ConfigDict, Field


class TemperateResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    city: str = Field(description="City name", min_length=1)
    temperatureInC: float = Field(description="Temperature in Celsius", ge=1)
    temperatureInF: float = Field(description="Temperature in Fahrenheit", ge=33.8)
    temperatureMessage: str = Field(
        description="A short description about the temperature in terms of Human Adaptability",
        min_length=1,
    )
