from .models import (
    AnalysisRequest,
    AnalysisResponse,
    BirthSummary,
    ConfidenceLevel,
    HouseCusp,
    PlanetaryPosition,
    RulingFactor,
)


def build_placeholder_analysis(payload: AnalysisRequest) -> AnalysisResponse:
    summary = BirthSummary(
        name=payload.name,
        dateOfBirth=payload.date_of_birth,
        timeOfBirth=payload.time_of_birth,
        birthPlace=payload.birth_place,
        country=payload.country,
        questionCategory=payload.question_category,
        question=payload.question,
        summaryLine=(
            f"{payload.name} asked a {payload.question_category.lower()} question for "
            f"{payload.birth_place}, {payload.country} using the recorded birth time "
            f"of {payload.time_of_birth} on {payload.date_of_birth}."
        ),
    )

    # TODO: Replace this static list with real KP planetary calculations.
    planetary_positions = [
        PlanetaryPosition(
            planet="Sun",
            sign="Scorpio",
            degree="23deg 10min",
            status="Placeholder",
            note="Estimated placeholder placement for MVP wiring only.",
        ),
        PlanetaryPosition(
            planet="Moon",
            sign="Aquarius",
            degree="11deg 42min",
            status="Placeholder",
            note="Real Moon longitude will come from the KP ephemeris engine.",
        ),
        PlanetaryPosition(
            planet="Mercury",
            sign="Sagittarius",
            degree="04deg 28min",
            status="Placeholder",
            note="Will later be computed from precise birth coordinates and time zone.",
        ),
        PlanetaryPosition(
            planet="Jupiter",
            sign="Taurus",
            degree="17deg 05min",
            status="Placeholder",
            note="Included to show the structured output shape for the frontend.",
        ),
    ]

    # TODO: Replace placeholder cusps with actual KP house cusp calculations.
    house_cusps = [
        HouseCusp(house=1, sign="Gemini", cuspDegree="09deg 15min", note="Ascendant placeholder."),
        HouseCusp(house=4, sign="Virgo", cuspDegree="08deg 51min", note="Domestic foundation placeholder."),
        HouseCusp(house=7, sign="Sagittarius", cuspDegree="09deg 15min", note="Relationship axis placeholder."),
        HouseCusp(house=10, sign="Pisces", cuspDegree="08deg 51min", note="Career axis placeholder."),
    ]

    # TODO: Map the correct nakshatra star lord from true KP planetary positions.
    star_lord = RulingFactor(
        area="Current query focus",
        ruler="Saturn",
        note="Placeholder star lord selected to demonstrate the KP response format.",
    )

    # TODO: Map the correct sub lord from the final KP house and planetary model.
    sub_lord = RulingFactor(
        area="Outcome refinement",
        ruler="Mercury",
        note="Placeholder sub lord selected to demonstrate the KP response format.",
    )

    # TODO: Generate a genuine KP interpretation using real house significations and ruling planets.
    interpretation = [
        f"This MVP gives a placeholder KP-style reading for the {payload.question_category.lower()} question: {payload.question}",
        "The response format is ready for future rule-based or calculated KP interpretation layers.",
        "Career-oriented questions will later weigh the 2nd, 6th, 10th, and 11th houses with true significators.",
    ]

    confidence = ConfidenceLevel(
        level="medium",
        reason="Confidence is intentionally capped because this MVP uses structured placeholder astrology data.",
    )

    disclaimer = (
        "This is a placeholder KP astrology analysis for product development only. "
        "It does not yet use final astrological calculations and should not be treated as authoritative guidance."
    )

    return AnalysisResponse(
        birthSummary=summary,
        planetaryPositions=planetary_positions,
        houseCusps=house_cusps,
        starLord=star_lord,
        subLord=sub_lord,
        interpretation=interpretation,
        confidenceLevel=confidence,
        disclaimer=disclaimer,
    )

