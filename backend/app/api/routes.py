from fastapi import APIRouter, HTTPException, Query

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
from app.schemas.places import (
    LocationSearchResult,
    LocationValidationRequest,
    LocationValidationResponse,
    TimezoneResolutionRequest,
    TimezoneResolutionResponse,
)
from app.services.chart_sessions import chart_session_store
from app.services.geocoding import resolve_timezone, search_locations, validate_location
from app.services.kp_engine import (
    build_chart,
    build_question_answer,
    get_supported_question_topics,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="kp-astro-backend")


@router.get("/api/locations/search", response_model=list[LocationSearchResult])
async def get_location_suggestions(
    q: str = Query(..., min_length=2),
    state: str | None = Query(default=None),
    country: str | None = Query(default=None),
) -> list[LocationSearchResult]:
    try:
        suggestions = search_locations(q, state=state, country=country)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Place lookup is temporarily unavailable.") from exc

    return [
        LocationSearchResult(
            displayName=item.display_name,
            city=item.city,
            stateOrProvince=item.state_or_province,
            country=item.country,
            latitude=item.latitude,
            longitude=item.longitude,
            timezone=item.timezone,
            confidence=item.confidence,
        )
        for item in suggestions
    ]


@router.get("/api/places/search", response_model=list[LocationSearchResult])
async def get_place_suggestions_legacy(
    q: str = Query(..., min_length=2),
    state: str | None = Query(default=None),
    country: str | None = Query(default=None),
) -> list[LocationSearchResult]:
    return await get_location_suggestions(q=q, state=state, country=country)


@router.post("/api/locations/resolve-timezone", response_model=TimezoneResolutionResponse)
async def resolve_location_timezone(payload: TimezoneResolutionRequest) -> TimezoneResolutionResponse:
    timezone = resolve_timezone(payload.latitude, payload.longitude)
    return TimezoneResolutionResponse(
        timezone=timezone,
        confidence=0.88 if timezone else 0.45,
        note=(
            "Timezone was resolved from the selected latitude and longitude."
            if timezone
            else "Timezone could not be resolved for the selected coordinates."
        ),
    )


@router.post("/api/locations/validate", response_model=LocationValidationResponse)
async def validate_selected_location(payload: LocationValidationRequest) -> LocationValidationResponse:
    try:
        result = validate_location(
            birth_place=payload.birth_place,
            state=payload.state,
            country=payload.country,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone=payload.timezone,
            date_of_birth=payload.date_of_birth,
            time_of_birth=payload.time_of_birth,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail="The selected location could not be validated.") from exc

    return LocationValidationResponse(
        birthPlace=payload.birth_place,
        state=payload.state,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone=resolve_timezone(payload.latitude, payload.longitude) or payload.timezone,
        normalizedUtcTime=result.normalized_utc_time,
        confidence=result.confidence,
        warnings=result.warnings,
    )


@router.post("/api/charts/calculate", response_model=ChartCalculationResponse)
async def calculate_chart(payload: ChartCalculationRequest) -> ChartCalculationResponse:
    try:
        chart = build_chart(payload)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="The chart could not be calculated from the provided birth details.") from exc
    session = chart_session_store.create(chart)
    return ChartCalculationResponse(chartId=session.chart_id, chart=session.chart_data)


@router.get("/api/charts/{chart_id}", response_model=ChartSessionResponse)
async def get_chart(chart_id: str) -> ChartSessionResponse:
    session = chart_session_store.get(chart_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chart session not found or expired.")

    return session


@router.delete("/api/charts/{chart_id}")
async def delete_chart(chart_id: str) -> dict[str, str]:
    deleted = chart_session_store.delete(chart_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chart session not found or expired.")

    return {"status": "deleted"}


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

    answer = build_question_answer(session.chart_data, payload.question, payload.optional_date_range)
    chart_session_store.add_question_answer(payload.chart_id, answer)
    return answer


@router.get("/api/questions/topics", response_model=QuestionTopicCatalog)
async def get_question_topics() -> QuestionTopicCatalog:
    return QuestionTopicCatalog(topics=get_supported_question_topics())

