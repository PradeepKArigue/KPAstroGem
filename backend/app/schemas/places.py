from pydantic import BaseModel, ConfigDict, Field


class LocationSearchResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_name: str = Field(..., alias="displayName")
    city: str
    state_or_province: str | None = Field(default=None, alias="stateOrProvince")
    country: str | None = None
    latitude: float
    longitude: float
    timezone: str | None = None
    confidence: float


class TimezoneResolutionRequest(BaseModel):
    latitude: float
    longitude: float
    birth_date: str | None = Field(default=None, alias="birthDate")


class TimezoneResolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    timezone: str | None = None
    confidence: float
    note: str


class LocationValidationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    birth_place: str = Field(..., alias="birthPlace", min_length=1)
    state: str | None = None
    country: str = Field(..., min_length=1)
    latitude: float
    longitude: float
    timezone: str = Field(..., min_length=1)
    date_of_birth: str = Field(..., alias="dateOfBirth", min_length=1)
    time_of_birth: str = Field(..., alias="timeOfBirth", min_length=1)


class LocationValidationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    birth_place: str = Field(..., alias="birthPlace")
    state: str | None = None
    country: str
    latitude: float
    longitude: float
    timezone: str
    normalized_utc_time: str = Field(..., alias="normalizedUtcTime")
    confidence: float
    warnings: list[str]
