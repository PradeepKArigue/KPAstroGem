from fastapi import APIRouter, HTTPException

from app.schemas.chart import (
    ChartCalculationRequest,
    ChartCalculationResponse,
    ChartQuestionRequest,
    ChartQuestionResponse,
    ChartSessionResponse,
    HealthResponse,
    HouseCusp,
    PlanetaryPosition,
    QuestionTopicCatalog,
)
from app.services.chart_sessions import chart_session_store
from app.services.kp_engine import (
    build_placeholder_chart,
    build_placeholder_question_answer,
    get_supported_question_topics,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="kp-astro-backend")


@router.post("/api/charts/calculate", response_model=ChartCalculationResponse)
async def calculate_chart(payload: ChartCalculationRequest) -> ChartCalculationResponse:
    chart = build_placeholder_chart(payload)
    session = chart_session_store.create(chart)
    return ChartCalculationResponse(chartId=session.chart_id, chart=session.chart_data)


@router.get("/api/charts/{chart_id}", response_model=ChartSessionResponse)
async def get_chart(chart_id: str) -> ChartSessionResponse:
    session = chart_session_store.get(chart_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chart session not found or expired.")

    return session


@router.get("/api/charts/{chart_id}/planets", response_model=list[PlanetaryPosition])
async def get_chart_planets(chart_id: str) -> list[PlanetaryPosition]:
    session = chart_session_store.get(chart_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chart session not found or expired.")

    return session.chart_data.planetary_positions


@router.get("/api/charts/{chart_id}/cusps", response_model=list[HouseCusp])
async def get_chart_cusps(chart_id: str) -> list[HouseCusp]:
    session = chart_session_store.get(chart_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chart session not found or expired.")

    return session.chart_data.house_cusps


@router.post("/api/questions/ask", response_model=ChartQuestionResponse)
async def ask_question(payload: ChartQuestionRequest) -> ChartQuestionResponse:
    session = chart_session_store.get(payload.chart_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chart session not found or expired.")

    answer = build_placeholder_question_answer(session.chart_data, payload.question, payload.optional_date_range)
    chart_session_store.add_question_answer(payload.chart_id, answer)
    return answer


@router.get("/api/questions/topics", response_model=QuestionTopicCatalog)
async def get_question_topics() -> QuestionTopicCatalog:
    return QuestionTopicCatalog(topics=get_supported_question_topics())

