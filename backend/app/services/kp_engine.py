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

    summary = BirthSummary(
        name=payload.name,
        dateOfBirth=payload.date_of_birth,
        timeOfBirth=payload.time_of_birth,
        birthPlace=payload.birth_place,
        state=payload.state,
        country=payload.country,
        timezone=payload.manual_timezone_override or payload.timezone,
        latitude=latitude,
        longitude=longitude,
        questionCategory=payload.question_category,
        question=payload.question,
        summaryLine=(
            f"{payload.name}'s temporary KP chart session was prepared for {payload.birth_place}, "
            f"{payload.country} with the current MVP placeholder pipeline."
        ),
        birthTimeAccuracyNote=(
            "Birth time accuracy strongly affects cusp sub lords and timing in KP. "
            "This MVP stores the entered time but does not yet perform full rectification."
        ),
    )

    # TODO: Replace these placeholders with real geocoding, timezone resolution, and KP ephemeris results.
    planetary_positions = [
        PlanetaryPosition(
            planet="Sun",
            sign="Scorpio",
            degree="23deg 10min",
            nakshatra="Jyeshtha",
            pada=2,
            starLord="Mercury",
            subLord="Saturn",
            status="Placeholder",
            note="Placeholder placement for the chart session flow.",
        ),
        PlanetaryPosition(
            planet="Moon",
            sign="Aquarius",
            degree="11deg 42min",
            nakshatra="Shatabhisha",
            pada=2,
            starLord="Rahu",
            subLord="Venus",
            status="Placeholder",
            note="Will later be computed from precise historical timezone and longitude data.",
        ),
        PlanetaryPosition(
            planet="Mercury",
            sign="Sagittarius",
            degree="04deg 28min",
            nakshatra="Mula",
            pada=2,
            starLord="Ketu",
            subLord="Mercury",
            status="Placeholder",
            note="Included to preserve the future KP table shape.",
        ),
        PlanetaryPosition(
            planet="Jupiter",
            sign="Taurus",
            degree="17deg 05min",
            nakshatra="Rohini",
            pada=3,
            starLord="Moon",
            subLord="Jupiter",
            status="Placeholder",
            note="Represents the future ephemeris provider contract.",
        ),
    ]

    # TODO: Replace cusp placeholders with Placidus/KP cusp calculations.
    house_cusps = [
        HouseCusp(
            house=1,
            sign="Gemini",
            cuspDegree="09deg 15min",
            signLord="Mercury",
            starLord="Rahu",
            subLord="Mercury",
            note="Ascendant placeholder for current MVP.",
        ),
        HouseCusp(
            house=4,
            sign="Virgo",
            cuspDegree="08deg 51min",
            signLord="Mercury",
            starLord="Moon",
            subLord="Saturn",
            note="Domestic foundation placeholder.",
        ),
        HouseCusp(
            house=7,
            sign="Sagittarius",
            cuspDegree="09deg 15min",
            signLord="Jupiter",
            starLord="Ketu",
            subLord="Venus",
            note="Relationship axis placeholder.",
        ),
        HouseCusp(
            house=10,
            sign="Pisces",
            cuspDegree="08deg 51min",
            signLord="Jupiter",
            starLord="Saturn",
            subLord="Mercury",
            note="Career axis placeholder.",
        ),
    ]

    star_lord = RulingFactor(
        area="Chart orientation",
        ruler="Saturn",
        note="Placeholder ruling factor used to keep the API explainable while calculations are pending.",
    )
    sub_lord = RulingFactor(
        area="Query refinement",
        ruler="Mercury",
        note="Placeholder sub lord used to model future KP decision logic.",
    )
    dasha_summary = DashaPeriod(
        mahaDasha="Saturn",
        bhukti="Mercury",
        antara="Moon",
        window="2026 Q2 to 2026 Q4",
        status="Placeholder",
        note="TODO: Implement real Vimshottari dasha, bhukti, and antara calculations.",
    )
    interpretation = [
        "A short-lived chart session is now available for question-based KP exploration.",
        "The current chart output is structural and intentionally placeholder-driven until the real KP engine is integrated.",
        "The 10th cusp, supporting houses, and dasha chain will later drive more reliable career readings.",
    ]
    confidence = ConfidenceLevel(
        level="medium",
        reason="Confidence is limited because this phase focuses on product structure and placeholder KP data.",
    )
    disclaimer = (
        "This chart is generated for software development and demonstrates a traditional interpretive KP workflow. "
        "It is not a final astrological calculation and should not be treated as guaranteed guidance."
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

    # TODO: Replace placeholder house support with rule-based house mapping and significator ranking.
    cusp_sub_lord_analysis = [
        f"House focus for {topic.name.lower()} questions is modeled with houses {', '.join(str(house) for house in topic.house_focus)}.",
        f"The placeholder 10th cusp sub lord is {chart.house_cusps[-1].sub_lord}, which is currently used as a sample support signal.",
    ]
    significator_analysis = [
        "Mercury is acting as a placeholder significator for growth, movement, and analysis in this MVP.",
        "Saturn is acting as a placeholder significator for discipline, delay, and long-cycle progress.",
    ]
    dasha_support = [
        f"The placeholder dasha chain is {chart.dasha_summary.maha_dasha} / {chart.dasha_summary.bhukti} / {chart.dasha_summary.antara}.",
        "Future versions will align timing support with true KP significators and event promise logic.",
    ]
    supporting_factors = [
        "Repeated Mercury/Saturn placeholders suggest effort-driven growth rather than sudden outcomes.",
        "The modeled house set includes achievement and gain houses that fit developmental questions.",
    ]
    blocking_factors = [
        "Exact timing remains tentative because the birth time has not been rectified and the dasha model is placeholder-only.",
        "No real cusp sub lord computation is running yet, so this cannot confirm promise versus denial.",
    ]

    caution_disclaimer = (
        "This response is interpretive and for product development only. It does not guarantee future events."
    )
    if topic.caution_level == "medical-disclaimer":
        caution_disclaimer = (
            "This is an interpretive placeholder reading only and not medical advice. "
            "Please use qualified healthcare guidance for health decisions."
        )
    if topic.caution_level == "legal-disclaimer":
        caution_disclaimer = (
            "This is an interpretive placeholder reading only and not legal advice. "
            "Please consult a qualified legal professional for legal decisions."
        )
    if topic.caution_level == "high-disclaimer":
        caution_disclaimer = (
            "This is an interpretive placeholder reading only and not financial advice or trading guidance."
        )

    interpretation = [
        f"The question was classified under {topic.name}.",
        f"Using placeholder KP structure, the app is emphasizing houses {', '.join(str(house) for house in topic.house_focus)} for this topic.",
        "The modeled reading suggests gradual progress supported by sustained effort, review, and timing awareness rather than instant certainty.",
    ]
    timing_window = optional_date_range or chart.dasha_summary.window
    confidence = ConfidenceLevel(
        level="medium",
        reason="Confidence is moderate because the answer uses a future-ready KP shape with placeholder calculation inputs.",
    )
    calculation_trail = [
        CalculationTrailEntry(step="Question classification", detail=f"Mapped the question to topic {topic.name}."),
        CalculationTrailEntry(
            step="House mapping",
            detail=f"Selected houses {', '.join(str(house) for house in topic.house_focus)} as the relevant placeholder KP houses.",
        ),
        CalculationTrailEntry(
            step="Cusp review",
            detail=f"Referenced the placeholder 10th cusp sub lord {chart.house_cusps[-1].sub_lord}.",
        ),
        CalculationTrailEntry(
            step="Timing review",
            detail=f"Referenced placeholder dasha window {chart.dasha_summary.window}.",
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

