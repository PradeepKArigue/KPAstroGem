from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BirthInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1)
    date_of_birth: str = Field(..., alias="dateOfBirth", min_length=1)
    time_of_birth: str = Field(..., alias="timeOfBirth", min_length=1)
    birth_place: str = Field(..., alias="birthPlace", min_length=1)
    state: str | None = None
    country: str = Field(..., min_length=1)
    timezone: str = Field(default="Asia/Kolkata", min_length=1)
    latitude: float | None = None
    longitude: float | None = None
    manual_timezone_override: str | None = Field(default=None, alias="manualTimezoneOverride")
    manual_coordinate_override: bool = Field(default=False, alias="manualCoordinateOverride")


class ChartCalculationRequest(BirthInput):
    question_category: str = Field(..., alias="questionCategory", min_length=1)
    question: str = Field(..., min_length=1)


class BirthSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    date_of_birth: str = Field(..., alias="dateOfBirth")
    time_of_birth: str = Field(..., alias="timeOfBirth")
    birth_place: str = Field(..., alias="birthPlace")
    state: str | None = None
    country: str
    timezone: str
    latitude: float | None = None
    longitude: float | None = None
    question_category: str = Field(..., alias="questionCategory")
    question: str
    summary_line: str = Field(..., alias="summaryLine")
    birth_time_accuracy_note: str = Field(..., alias="birthTimeAccuracyNote")


class PlanetaryPosition(BaseModel):
    planet: str
    sign: str
    degree: str
    nakshatra: str
    pada: int
    star_lord: str = Field(..., alias="starLord")
    sub_lord: str = Field(..., alias="subLord")
    status: str
    note: str


class HouseCusp(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    house: int
    sign: str
    cusp_degree: str = Field(..., alias="cuspDegree")
    sign_lord: str = Field(..., alias="signLord")
    star_lord: str = Field(..., alias="starLord")
    sub_lord: str = Field(..., alias="subLord")
    note: str


class DashaPeriod(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    maha_dasha: str = Field(..., alias="mahaDasha")
    bhukti: str
    antara: str
    window: str
    status: str
    note: str


class RulingFactor(BaseModel):
    area: str
    ruler: str
    note: str


class ConfidenceLevel(BaseModel):
    level: str
    reason: str


class CalculationTrailEntry(BaseModel):
    step: str
    detail: str


class ChartData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    birth_summary: BirthSummary = Field(..., alias="birthSummary")
    planetary_positions: list[PlanetaryPosition] = Field(..., alias="planetaryPositions")
    house_cusps: list[HouseCusp] = Field(..., alias="houseCusps")
    star_lord: RulingFactor = Field(..., alias="starLord")
    sub_lord: RulingFactor = Field(..., alias="subLord")
    dasha_summary: DashaPeriod = Field(..., alias="dashaSummary")
    interpretation: list[str]
    confidence_level: ConfidenceLevel = Field(..., alias="confidenceLevel")
    disclaimer: str


class ChartCalculationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: str = Field(..., alias="chartId")
    chart: ChartData


class ChartQuestionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: str = Field(..., alias="chartId", min_length=1)
    question: str = Field(..., min_length=1)
    optional_date_range: str | None = Field(default=None, alias="optionalDateRange")


class QuestionTopic(BaseModel):
    name: str
    house_focus: list[int] = Field(..., alias="houseFocus")
    sample_questions: list[str] = Field(..., alias="sampleQuestions")
    caution_level: str = Field(..., alias="cautionLevel")


class QuestionTopicCatalog(BaseModel):
    topics: list[QuestionTopic]


class ChartQuestionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question: str
    classified_topic: str = Field(..., alias="classifiedTopic")
    relevant_houses: list[int] = Field(..., alias="relevantHouses")
    cusp_sub_lord_analysis: list[str] = Field(..., alias="cuspSubLordAnalysis")
    significator_analysis: list[str] = Field(..., alias="significatorAnalysis")
    dasha_support: list[str] = Field(..., alias="dashaSupport")
    supporting_factors: list[str] = Field(..., alias="supportingFactors")
    blocking_factors: list[str] = Field(..., alias="blockingFactors")
    interpretation: list[str]
    possible_timing_window: str = Field(..., alias="possibleTimingWindow")
    confidence_level: ConfidenceLevel = Field(..., alias="confidenceLevel")
    calculation_trail: list[CalculationTrailEntry] = Field(..., alias="calculationTrail")
    disclaimer: str


class ChartSessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: str = Field(..., alias="chartId")
    created_at: datetime = Field(..., alias="createdAt")
    expires_at: datetime = Field(..., alias="expiresAt")
    chart_data: ChartData = Field(..., alias="chartData")
    question_history: list[ChartQuestionResponse] = Field(default_factory=list, alias="questionHistory")


class HealthResponse(BaseModel):
    status: str
    service: str

