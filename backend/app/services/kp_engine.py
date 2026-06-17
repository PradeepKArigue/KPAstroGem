from __future__ import annotations

from hashlib import sha256

from app.schemas.chart import (
    BirthSummary,
    CalculationTrailEntry,
    ChartCalculationRequest,
    ChartData,
    ChartQuestionResponse,
    ConfidenceLevel,
    DashaPeriod,
    HouseCusp,
    PlanetaryPosition,
    QuestionTopic,
    RulingFactor,
)

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def get_supported_question_topics() -> list[QuestionTopic]:
    return [
        QuestionTopic(
            name="Career",
            houseFocus=[2, 6, 10, 11],
            sampleQuestions=["Will I get a job change?", "Is promotion supported?", "How is my career growth?"],
            cautionLevel="standard",
        ),
        QuestionTopic(
            name="Marriage",
            houseFocus=[2, 7, 11],
            sampleQuestions=["When is marriage likely?", "Are there delays in marriage?"],
            cautionLevel="standard",
        ),
        QuestionTopic(
            name="Finance",
            houseFocus=[2, 6, 10, 11],
            sampleQuestions=["How is my financial growth?", "Are there obstacles in wealth accumulation?"],
            cautionLevel="high-disclaimer",
        ),
        QuestionTopic(
            name="Foreign Settlement",
            houseFocus=[3, 9, 12],
            sampleQuestions=["Is foreign settlement possible?", "Will I relocate abroad?"],
            cautionLevel="standard",
        ),
        QuestionTopic(
            name="Property",
            houseFocus=[4, 11, 12],
            sampleQuestions=["Will I buy property?", "Is house purchase supported?"],
            cautionLevel="standard",
        ),
        QuestionTopic(
            name="Children",
            houseFocus=[2, 5, 11],
            sampleQuestions=["Are children supported in the chart?", "Is there delay related to children?"],
            cautionLevel="standard",
        ),
        QuestionTopic(
            name="Business",
            houseFocus=[2, 7, 10, 11],
            sampleQuestions=["Is business suitable for me?", "Will business income improve?"],
            cautionLevel="high-disclaimer",
        ),
        QuestionTopic(
            name="Education",
            houseFocus=[4, 5, 9, 11],
            sampleQuestions=["Is higher education supported?", "Are there delays in studies?"],
            cautionLevel="standard",
        ),
        QuestionTopic(
            name="Health Caution",
            houseFocus=[1, 6, 8, 12],
            sampleQuestions=["Are there stressful periods for health?", "Is recovery supported?"],
            cautionLevel="medical-disclaimer",
        ),
        QuestionTopic(
            name="Legal Caution",
            houseFocus=[6, 7, 8, 12],
            sampleQuestions=["Are there legal complications?", "Is settlement supported?"],
            cautionLevel="legal-disclaimer",
        ),
    ]


def _infer_topic(question: str, fallback: str) -> QuestionTopic:
    normalized = question.lower()
    topic_map = get_supported_question_topics()

    keyword_groups = {
        "Career": ["career", "job", "promotion", "work", "profession"],
        "Marriage": ["marriage", "married", "partner", "relationship"],
        "Finance": ["finance", "money", "wealth", "income"],
        "Foreign Settlement": ["foreign", "abroad", "relocation", "settlement", "overseas"],
        "Property": ["property", "house", "real estate", "land"],
        "Children": ["children", "child", "pregnancy", "family expansion"],
        "Business": ["business", "startup", "partnership", "entrepreneur"],
        "Education": ["study", "education", "college", "exam"],
        "Health Caution": ["health", "recovery", "stress", "illness"],
        "Legal Caution": ["legal", "court", "case", "litigation"],
    }

    for topic in topic_map:
        for keyword in keyword_groups.get(topic.name, []):
            if keyword in normalized:
                return topic

    for topic in topic_map:
        if topic.name.lower() == fallback.lower():
            return topic

    return topic_map[0]


def build_placeholder_chart(payload: ChartCalculationRequest) -> ChartData:
    latitude = payload.latitude if payload.latitude is not None else 17.4399
    longitude = payload.longitude if payload.longitude is not None else 78.4983
    timezone = payload.manual_timezone_override or payload.timezone
    base_seed = _seed_from_payload(payload, latitude, longitude, timezone)

    summary = BirthSummary(
        name=payload.name,
        dateOfBirth=payload.date_of_birth,
        timeOfBirth=payload.time_of_birth,
        birthPlace=payload.birth_place,
        state=payload.state,
        country=payload.country,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        questionCategory=payload.question_category,
        question=payload.question,
        summaryLine=(
            f"{payload.name}'s interactive KP chart session was generated for {payload.birth_place}, {payload.country}. "
            "This MVP now adapts the chart tables to the entered birth profile while the full astronomical engine is still pending."
        ),
        birthTimeAccuracyNote=(
            "Birth time accuracy strongly affects cusp sub lords and timing in KP. "
            "This MVP reacts to the entered profile but still needs a true KP ephemeris layer for final-grade charting."
        ),
    )

    planetary_positions = [
        _build_planetary_position(planet, base_seed + index * 137) for index, planet in enumerate(PLANETS)
    ]
    house_cusps = [_build_house_cusp(house, base_seed + house * 73) for house in range(1, 13)]

    star_lord = RulingFactor(
        area="Chart orientation",
        ruler=planetary_positions[0].star_lord,
        note="Modeled from the current profile seed to make the chart feel responsive while true KP ruling-planet logic is pending.",
    )
    sub_lord = RulingFactor(
        area="Query refinement",
        ruler=house_cusps[9].sub_lord,
        note="Modeled from the active chart profile until final cusp-sub-lord calculation is integrated.",
    )
    dasha_summary = _build_dasha_summary(base_seed)
    interpretation = [
        "A short-lived chart session is now available with profile-driven tables, timing windows, and question-ready KP scaffolding.",
        "This chart reacts to the entered birth details, location, and timezone so different profiles no longer produce the exact same static result.",
        "Planet, cusp, significator, and dasha layers are still modeled outputs and remain clearly marked until the full KP calculation engine is integrated.",
    ]
    confidence = ConfidenceLevel(
        level="medium",
        reason="Confidence is improved for the live product experience because the output adapts to the entered birth profile, but full astronomical KP validation is still pending.",
    )
    disclaimer = (
        "This chart is generated for software development and demonstrates a traditional interpretive KP workflow. "
        "It is a modeled MVP experience, not yet a fully verified KP astrological calculation."
    )

    return ChartData(
        birthSummary=summary,
        planetaryPositions=planetary_positions,
        houseCusps=house_cusps,
        starLord=star_lord,
        subLord=sub_lord,
        dashaSummary=dasha_summary,
        interpretation=interpretation,
        confidenceLevel=confidence,
        disclaimer=disclaimer,
    )


def build_placeholder_question_answer(
    chart: ChartData, question: str, optional_date_range: str | None
) -> ChartQuestionResponse:
    topic = _infer_topic(question, chart.birth_summary.question_category)
    dominant_cusp = chart.house_cusps[(topic.house_focus[0] - 1) % len(chart.house_cusps)]
    supporting_planets = [
        chart.planetary_positions[topic.house_focus[0] % len(chart.planetary_positions)],
        chart.planetary_positions[topic.house_focus[-1] % len(chart.planetary_positions)],
    ]

    cusp_sub_lord_analysis = [
        f"House focus for {topic.name.lower()} questions is mapped to houses {', '.join(str(house) for house in topic.house_focus)} in this KP-style engine.",
        f"The leading cusp review starts from house {dominant_cusp.house}, where the star lord is {dominant_cusp.star_lord} and the sub lord is {dominant_cusp.sub_lord}.",
    ]
    significator_analysis = [
        f"{supporting_planets[0].planet} is acting as a modeled significator through {supporting_planets[0].nakshatra} and sub lord {supporting_planets[0].sub_lord}.",
        f"{supporting_planets[1].planet} adds a secondary signal through {supporting_planets[1].sign} and star lord {supporting_planets[1].star_lord}.",
    ]
    dasha_support = [
        f"The current modeled dasha chain is {chart.dasha_summary.maha_dasha} / {chart.dasha_summary.bhukti} / {chart.dasha_summary.antara}.",
        f"Timing focus is being framed around {optional_date_range or chart.dasha_summary.window}.",
    ]
    supporting_factors = [
        f"The active house group {', '.join(str(house) for house in topic.house_focus)} supports a focused reading for {topic.name.lower()}.",
        f"The chart's current ruling emphasis on {chart.star_lord.ruler} and {chart.sub_lord.ruler} adds continuity to the answer narrative.",
    ]
    blocking_factors = [
        "Exact event promise versus denial is still limited because the final KP significator ranking engine is not yet implemented.",
        "Fine timing remains tentative because the birth time has not been rectified and the dasha model is still a guided MVP version.",
    ]

    caution_disclaimer = (
        "This response is interpretive and for product development only. It does not guarantee future events."
    )
    if topic.caution_level == "medical-disclaimer":
        caution_disclaimer = (
            "This is an interpretive KP-style reading only and not medical advice. Please use qualified healthcare guidance for health decisions."
        )
    if topic.caution_level == "legal-disclaimer":
        caution_disclaimer = (
            "This is an interpretive KP-style reading only and not legal advice. Please consult a qualified legal professional for legal decisions."
        )
    if topic.caution_level == "high-disclaimer":
        caution_disclaimer = (
            "This is an interpretive KP-style reading only and not financial advice, business advice, or trading guidance."
        )

    interpretation = [
        f"The question was classified under {topic.name}.",
        f"The chart currently emphasizes houses {', '.join(str(house) for house in topic.house_focus)} with cusp sub lord {dominant_cusp.sub_lord} as a leading signal.",
        f"The modeled reading suggests a {chart.dasha_summary.status.lower()} trend with more value in timing, preparation, and pattern recognition than in absolute certainty.",
    ]
    timing_window = optional_date_range or chart.dasha_summary.window
    confidence = ConfidenceLevel(
        level="medium",
        reason="Confidence is moderate because the answer now reacts to the generated chart profile, but the full KP rule base and ephemeris-driven engine are still pending.",
    )
    calculation_trail = [
        CalculationTrailEntry(step="Question classification", detail=f"Mapped the question to topic {topic.name}."),
        CalculationTrailEntry(
            step="House mapping",
            detail=f"Selected houses {', '.join(str(house) for house in topic.house_focus)} for this topic.",
        ),
        CalculationTrailEntry(
            step="Cusp review",
            detail=f"Referenced house {dominant_cusp.house} with star lord {dominant_cusp.star_lord} and sub lord {dominant_cusp.sub_lord}.",
        ),
        CalculationTrailEntry(
            step="Timing review",
            detail=f"Referenced dasha window {chart.dasha_summary.window}.",
        ),
    ]

    return ChartQuestionResponse(
        question=question,
        classifiedTopic=topic.name,
        relevantHouses=topic.house_focus,
        cuspSubLordAnalysis=cusp_sub_lord_analysis,
        significatorAnalysis=significator_analysis,
        dashaSupport=dasha_support,
        supportingFactors=supporting_factors,
        blockingFactors=blocking_factors,
        interpretation=interpretation,
        possibleTimingWindow=timing_window,
        confidenceLevel=confidence,
        calculationTrail=calculation_trail,
        disclaimer=caution_disclaimer,
    )


def _seed_from_payload(payload: ChartCalculationRequest, latitude: float, longitude: float, timezone: str) -> int:
    raw = "|".join(
        [
            payload.name,
            payload.date_of_birth,
            payload.time_of_birth,
            payload.birth_place,
            payload.state or "",
            payload.country,
            timezone,
            f"{latitude:.4f}",
            f"{longitude:.4f}",
        ]
    )
    return int(sha256(raw.encode("utf-8")).hexdigest()[:12], 16)


def _build_planetary_position(planet: str, seed: int) -> PlanetaryPosition:
    sign_index = seed % len(SIGNS)
    degree_value = ((seed // 7) % 3000) / 100
    nakshatra_index = (seed // 11) % len(NAKSHATRAS)
    pada = ((seed // 17) % 4) + 1
    star_lord = LORDS[(seed // 19) % len(LORDS)]
    sub_lord = LORDS[(seed // 23) % len(LORDS)]

    return PlanetaryPosition(
        planet=planet,
        sign=SIGNS[sign_index],
        degree=_format_degree(degree_value),
        nakshatra=NAKSHATRAS[nakshatra_index],
        pada=pada,
        starLord=star_lord,
        subLord=sub_lord,
        status="Modeled",
        note="Modeled from the entered birth profile to keep the MVP responsive while a full KP ephemeris engine is still pending.",
    )


def _build_house_cusp(house: int, seed: int) -> HouseCusp:
    sign_index = (seed // 5) % len(SIGNS)
    degree_value = ((seed // 13) % 3000) / 100

    return HouseCusp(
        house=house,
        sign=SIGNS[sign_index],
        cuspDegree=_format_degree(degree_value),
        signLord=LORDS[(seed // 7) % len(LORDS)],
        starLord=LORDS[(seed // 11) % len(LORDS)],
        subLord=LORDS[(seed // 17) % len(LORDS)],
        note="Modeled cusp values preserve the future KP table shape while true Placidus/KP cusp calculations are still pending.",
    )


def _build_dasha_summary(seed: int) -> DashaPeriod:
    maha = LORDS[seed % len(LORDS)]
    bhukti = LORDS[(seed // 3) % len(LORDS)]
    antara = LORDS[(seed // 5) % len(LORDS)]
    start_month = (seed % 9) + 1
    end_month = start_month + 2

    return DashaPeriod(
        mahaDasha=maha,
        bhukti=bhukti,
        antara=antara,
        window=f"2026-{start_month:02d} to 2026-{min(end_month,12):02d}",
        status="Modeled",
        note="This is a profile-responsive modeled dasha view for the MVP. A true Vimshottari KP timing engine is still pending.",
    )


def _format_degree(value: float) -> str:
    degrees = int(value)
    minutes = int(round((value - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0
    return f"{degrees:02d}deg {minutes:02d}min"
