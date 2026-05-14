from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str = Field(examples=["Quiz Totem API"])
    database: str = Field(
        description="ok | down | disabled",
        examples=["ok"],
    )
