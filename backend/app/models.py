from pydantic import BaseModel, ConfigDict, Field


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1)
    date_of_birth: str = Field(..., alias="dateOfBirth", min_length=1)
    time_of_birth: str = Field(..., alias="timeOfBirth", min_length=1)
    birth_place: str = Field(..., alias="birthPlace", min_length=1)
    country: str = Field(..., min_length=1)
    question_category: str = Field(..., alias="questionCategory", min_length=1)
    question: str = Field(..., min_length=1)


class BirthSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    date_of_birth: str = Field(..., alias="dateOfBirth")
    time_of_birth: str = Field(..., alias="timeOfBirth")
    birth_place: str = Field(..., alias="birthPlace")
    country: str
    question_category: str = Field(..., alias="questionCategory")
    question: str
    summary_line: str = Field(..., alias="summaryLine")


class PlanetaryPosition(BaseModel):
    planet: str
    sign: str
    degree: str
    status: str
    note: str


class HouseCusp(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    house: int
    sign: str
    cusp_degree: str = Field(..., alias="cuspDegree")
    note: str


class RulingFactor(BaseModel):
    area: str
    ruler: str
    note: str


class ConfidenceLevel(BaseModel):
    level: str
    reason: str


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    birth_summary: BirthSummary = Field(..., alias="birthSummary")
    planetary_positions: list[PlanetaryPosition] = Field(..., alias="planetaryPositions")
    house_cusps: list[HouseCusp] = Field(..., alias="houseCusps")
    star_lord: RulingFactor = Field(..., alias="starLord")
    sub_lord: RulingFactor = Field(..., alias="subLord")
    interpretation: list[str]
    confidence_level: ConfidenceLevel = Field(..., alias="confidenceLevel")
    disclaimer: str

