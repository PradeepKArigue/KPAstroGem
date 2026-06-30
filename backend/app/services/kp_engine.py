from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from itertools import cycle, islice
from zoneinfo import ZoneInfo

import swisseph as swe

from app.schemas.chart import (
    BirthSummary,
    BirthDashaSnapshot,
    CalculationTrailEntry,
    ChartCalculationRequest,
    ChartData,
    ChartQuestionResponse,
    ConfidenceLevel,
    DashaPeriod,
    DashaTimelineEntry,
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

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

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

VIMSHOTTARI_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
NAKSHATRA_LORDS = [VIMSHOTTARI_SEQUENCE[index % len(VIMSHOTTARI_SEQUENCE)] for index in range(len(NAKSHATRAS))]
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}
PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
}
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIDEREAL_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
HOUSE_SYSTEM = b"P"
NAKSHATRA_SPAN = 360 / 27
PADA_SPAN = NAKSHATRA_SPAN / 4
DASHA_YEAR_DAYS = 365.2425
GENERAL_SUPPORTIVE_HOUSES = {1, 2, 4, 5, 7, 9, 10, 11}
GENERAL_CHALLENGING_HOUSES = {6, 8, 12}
HOUSE_THEMES = {
    1: "self, vitality, and personal direction",
    2: "resources, family support, and speech",
    3: "effort, communication, and initiative",
    4: "education, home, and emotional grounding",
    5: "intelligence, creativity, and children",
    6: "competition, debt, illness, and service strain",
    7: "partnership, public engagement, and contracts",
    8: "sudden change, vulnerability, and hidden pressure",
    9: "fortune, teachers, dharma, and long-range support",
    10: "profession, karma, and visible achievement",
    11: "gains, realization, and networks",
    12: "loss, retreat, sleep, and distant separation",
}


@dataclass
class ComputedPlanet:
    name: str
    longitude: float
    speed: float
    house: int
    sign: str
    degree_label: str
    nakshatra: str
    pada: int
    star_lord: str
    sub_lord: str


@dataclass
class DashaSegment:
    level: str
    lord: str
    start: datetime
    end: datetime


@dataclass
class ScoredSignificator:
    planet: PlanetaryPosition
    score: int
    reasons: list[str]


@dataclass
class TopicEvaluation:
    support_score: int
    challenge_score: int
    trend: str
    supportive_cusp_links: list[str]
    caution_cusp_links: list[str]
    dasha_resonance: list[str]
    obstruction_count: int


TOPIC_CONTEXT = {
    "Career": {
        "supporting": {2, 6, 10, 11},
        "challenging": {5, 8, 12},
        "promise": "sustained professional growth, responsibility, and visible gains",
        "challenge": "delay, internal politics, or stop-start professional movement",
    },
    "Marriage": {
        "supporting": {2, 7, 11},
        "challenging": {1, 6, 8, 12},
        "promise": "commitment, alliance, and formal relationship progress",
        "challenge": "delay, mismatch, or emotional distance in commitment matters",
    },
    "Finance": {
        "supporting": {2, 6, 10, 11},
        "challenging": {8, 12},
        "promise": "income stability, accumulation, and steady material growth",
        "challenge": "leakage, debt pressure, or uneven accumulation",
    },
    "Foreign Settlement": {
        "supporting": {3, 9, 12},
        "challenging": {4, 8},
        "promise": "movement, relocation, and overseas opportunity",
        "challenge": "attachment to present circumstances or delay in travel settlement",
    },
    "Property": {
        "supporting": {4, 11, 12},
        "challenging": {6, 8},
        "promise": "property progress, acquisition, or domestic stabilization",
        "challenge": "procedural delay, dispute, or financing strain",
    },
    "Children": {
        "supporting": {2, 5, 11},
        "challenging": {1, 6, 8, 12},
        "promise": "family growth, support, and fulfillment in child-related matters",
        "challenge": "delay, caution, or additional patience around family growth",
    },
    "Business": {
        "supporting": {2, 7, 10, 11},
        "challenging": {6, 8, 12},
        "promise": "commercial growth, partnership support, and business traction",
        "challenge": "risk, volatility, or partner-side complications",
    },
    "Education": {
        "supporting": {4, 5, 9, 11},
        "challenging": {3, 8, 12},
        "promise": "study continuity, guidance, and academic progress",
        "challenge": "distraction, break, or slow academic consolidation",
    },
    "Health Caution": {
        "supporting": {1, 5, 11},
        "challenging": {6, 8, 12},
        "promise": "recovery support, resilience, and better management",
        "challenge": "fatigue, recurring strain, or the need for careful follow-up",
    },
    "Legal Caution": {
        "supporting": {6, 10, 11},
        "challenging": {7, 8, 12},
        "promise": "structured resolution, compliance support, and procedural progress",
        "challenge": "dispute extension, complication, or negotiation pressure",
    },
}


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


def build_chart(payload: ChartCalculationRequest) -> ChartData:
    if payload.latitude is None or payload.longitude is None:
        raise ValueError("Latitude and longitude are required for KP calculations.")

    timezone_name = payload.manual_timezone_override or payload.timezone
    birth_local, birth_utc = _resolve_birth_datetimes(payload.date_of_birth, payload.time_of_birth, timezone_name)
    julian_day = _to_julian_day_ut(birth_utc)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)

    house_longitudes = _compute_house_longitudes(julian_day, payload.latitude, payload.longitude)
    planets = _compute_planets(julian_day, house_longitudes)
    house_cusps = _build_house_cusps(house_longitudes)
    dasha_summary = _build_dasha_summary(birth_utc, _find_computed_planet(planets, "Moon").longitude)
    birth_dasha = _build_birth_dasha_snapshot(birth_utc, _find_computed_planet(planets, "Moon").longitude)
    lifetime_dasha_timeline = _build_lifetime_dasha_timeline(
        birth_utc,
        _find_computed_planet(planets, "Moon").longitude,
        [_planet_to_model(planet) for planet in planets],
        house_cusps,
        years=100,
    )
    ayanamsa = swe.get_ayanamsa_ut(julian_day)
    ascendant = house_cusps[0]
    moon = _find_computed_planet(planets, "Moon")
    planet_models = [_planet_to_model(planet) for planet in planets]

    summary = BirthSummary(
        name=payload.name,
        dateOfBirth=payload.date_of_birth,
        timeOfBirth=payload.time_of_birth,
        birthPlace=payload.birth_place,
        state=payload.state,
        country=payload.country,
        timezone=timezone_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        questionCategory=payload.question_category,
        question=payload.question,
        summaryLine=(
            f"{payload.name}'s KP chart was computed for {payload.birth_place}, {payload.country} "
            f"using sidereal Krishnamurti ayanamsa at {ayanamsa:.4f} degrees."
        ),
        birthTimeAccuracyNote=(
            "Birth time precision is critical in KP because cusp sub lords and timing can shift with even small "
            "changes in recorded time or birthplace coordinates."
        ),
    )

    star_lord = RulingFactor(
        area="Ascendant star lord",
        ruler=ascendant.star_lord,
        note="Derived from the computed first-house cusp in sidereal KP mode.",
    )
    sub_lord = RulingFactor(
        area="Ascendant sub lord",
        ruler=ascendant.sub_lord,
        note="Derived from the computed first-house cusp subdivision used in KP reading.",
    )
    tenth_cusp = house_cusps[9]
    strongest_career = _rank_significators(planet_models, house_cusps, [2, 6, 10, 11])[:2]
    kp_strengths = _build_general_kp_strengths(planet_models, house_cusps, dasha_summary)
    kp_cautions = _build_general_kp_cautions(planet_models, house_cusps, dasha_summary)
    remedies = _build_general_remedies(house_cusps, dasha_summary, planet_models)
    interpretation = [
        f"Lagna rises in {ascendant.sign} while the janma rasi is {moon.sign} in {moon.nakshatra} pada {moon.pada}.",
        (
            f"The 10th cusp falls in {tenth_cusp.sign} with star lord {tenth_cusp.star_lord} and sub lord {tenth_cusp.sub_lord}, "
            "so professional matters are read through that chain in this chart."
        ),
        (
            f"At birth the dasha opened under {birth_dasha.maha_dasha} / {birth_dasha.bhukti} / {birth_dasha.antara}, "
            f"with a balance of {birth_dasha.balance_at_birth} remaining in the opening maha dasha."
        ),
        (
            f"The active dasha chain as of {date.today().isoformat()} is "
            f"{dasha_summary.maha_dasha} / {dasha_summary.bhukti} / {dasha_summary.antara}."
        ),
        (
            f"Current chart emphasis is strongest through {', '.join(item.planet.planet for item in strongest_career)} "
            "for practical life-direction and visible results."
        ),
        "Astronomical positions, nakshatras, cusps, and Vimshottari sequencing are computed from the entered birth profile.",
    ]
    confidence = ConfidenceLevel(
        level="medium-high",
        reason="Astronomical chart values are computed from Swiss Ephemeris, while the automated interpretation layer is still evolving.",
    )
    disclaimer = (
        "Astronomical positions, nakshatras, cusps, and dasha sequencing are computed from Swiss Ephemeris in sidereal "
        "Krishnamurti mode. Interpretive statements and automated Q&A still require further KP rule-depth validation."
    )

    return ChartData(
        birthSummary=summary,
        planetaryPositions=planet_models,
        houseCusps=house_cusps,
        starLord=star_lord,
        subLord=sub_lord,
        dashaSummary=dasha_summary,
        birthDasha=birth_dasha,
        lifetimeDashaTimeline=lifetime_dasha_timeline,
        kpStrengths=kp_strengths,
        kpCautions=kp_cautions,
        remedies=remedies,
        interpretation=interpretation,
        confidenceLevel=confidence,
        disclaimer=disclaimer,
    )


def build_question_answer(chart: ChartData, question: str, optional_date_range: str | None) -> ChartQuestionResponse:
    topic = _infer_topic(question, chart.birth_summary.question_category)
    topic_context = TOPIC_CONTEXT.get(topic.name, TOPIC_CONTEXT["Career"])
    current_age = _current_age(chart.birth_summary.date_of_birth)
    lagna_cusp = chart.house_cusps[0]
    relevant_cusps = [chart.house_cusps[house - 1] for house in topic.house_focus]
    dominant_cusp = relevant_cusps[0]
    moon = _find_planet_model(chart.planetary_positions, "Moon")
    antara_planet = _find_planet_model(chart.planetary_positions, chart.dasha_summary.antara)
    scored_significators = _rank_significators(chart.planetary_positions, chart.house_cusps, topic.house_focus)
    obstructing_significators = _rank_significators(
        chart.planetary_positions,
        chart.house_cusps,
        sorted(topic_context["challenging"]),
    )
    linked_planets = [item.planet for item in scored_significators[:3]]
    active_dasha_lords = {
        chart.dasha_summary.maha_dasha,
        chart.dasha_summary.bhukti,
        chart.dasha_summary.antara,
    }
    current_week = _current_week_window()
    support_score = sum(item.score for item in scored_significators[:3])
    challenge_score = sum(item.score for item in obstructing_significators[:3])
    active_obstructions = [
        cusp for cusp in chart.house_cusps if cusp.house in topic_context["challenging"] and cusp.sub_lord in active_dasha_lords
    ]
    evaluation = _evaluate_topic_rules(
        chart.house_cusps,
        relevant_cusps,
        topic_context,
        active_dasha_lords,
        support_score,
        challenge_score,
        len(active_obstructions),
    )
    trend = evaluation.trend
    profession_signature = _describe_topic_signature(topic.name, linked_planets, dominant_cusp)
    age_context = _build_age_context(
        topic_name=topic.name,
        current_age=current_age,
        profession_signature=profession_signature,
    )
    minor_projection = _build_minor_projection(
        chart=chart,
        topic_name=topic.name,
        current_age=current_age,
        dominant_cusp=dominant_cusp,
        linked_planets=linked_planets,
        profession_signature=profession_signature,
    )

    cusp_sub_lord_analysis = [
        (
            f"Jathakam context begins with lagna {lagna_cusp.sign}, janma rasi {moon.sign}, "
            f"and janma nakshatra {moon.nakshatra} pada {moon.pada}."
        ),
        f"The main KP house group for {topic.name.lower()} is {', '.join(str(house) for house in topic.house_focus)}.",
        (
            f"The leading cusp review starts from house {dominant_cusp.house}, where sign lord is {dominant_cusp.sign_lord}, "
            f"star lord is {dominant_cusp.star_lord}, and sub lord is {dominant_cusp.sub_lord}."
        ),
        (
            f"Within the running dasha chain, {chart.dasha_summary.maha_dasha}, {chart.dasha_summary.bhukti}, and "
            f"{chart.dasha_summary.antara} are checked against these houses for event support or delay."
        ),
    ]
    significator_analysis = [
        (
            f"{item.planet.planet} ranks strongly because it connects through {build_house_connection_summary(item.planet, chart.house_cusps)}. "
            f"Its star lord is {item.planet.star_lord}, sub lord is {item.planet.sub_lord}, and KP weight score is {item.score}."
        )
        for item in scored_significators[:2]
    ]
    if len(significator_analysis) < 2:
        significator_analysis.append(
            f"Moon remains a timing reference through {moon.sign}, {moon.nakshatra}, and sub lord {moon.sub_lord}."
        )

    dasha_support = [
        (
            f"As of {current_week['today']}, the active computed dasha chain is "
            f"{chart.dasha_summary.maha_dasha} / {chart.dasha_summary.bhukti} / {chart.dasha_summary.antara}."
        ),
        (
            f"For the week of {current_week['start']} to {current_week['end']}, the antara focus is read through "
            f"{antara_planet.sign}, {antara_planet.nakshatra}, and sub lord {antara_planet.sub_lord}."
        ),
        f"Timing emphasis is being framed around {optional_date_range or chart.dasha_summary.window}.",
    ]
    if age_context["is_minor"]:
        dasha_support = list(minor_projection["dasha_lines"] if minor_projection else [])
        if not dasha_support:
            dasha_support = [
                str(age_context["timing_intro"]),
                str(age_context["direction_line"]).format(house=dominant_cusp.house, profession=profession_signature),
                *_build_minor_topic_yearly_outlook(topic.name, current_age),
            ]
    supporting_factors = [
        (
            f"The computed trend for this topic is {trend}, because the chart keeps returning the supporting houses "
            f"{', '.join(str(house) for house in sorted(topic_context['supporting']))} with support score {support_score} "
            f"against challenge score {challenge_score}."
        ),
        (
            f"KP support is strongest through {', '.join(evaluation.supportive_cusp_links[:3])}."
            if evaluation.supportive_cusp_links
            else "No unusually strong cusp-support chain dominated this question, so the reading is leaning more on general significator strength."
        ),
        (
            f"Relevant house lords cluster around {', '.join(sorted({cusp.star_lord for cusp in relevant_cusps}))} "
            "at the star-lord layer."
        ),
        (
            f"Current dasha resonance is visible through {', '.join(evaluation.dasha_resonance[:3])}."
            if evaluation.dasha_resonance
            else "The running dasha chain is only partially resonating with the main topic cusps, so timing should be treated with more caution."
        ),
        (
            f"The ascendant ruling pair {chart.star_lord.ruler} / {chart.sub_lord.ruler} keeps the question tied "
            "to the computed birth profile rather than a generic template."
        ),
    ]
    if age_context["is_minor"]:
        supporting_factors.insert(
            0,
            str(age_context["support_line"]),
        )
    if minor_projection and minor_projection["support_line"]:
        supporting_factors.insert(1, str(minor_projection["support_line"]))
    blocking_factors = [
        (
            f"Challenging houses {', '.join(str(house) for house in sorted(topic_context['challenging']))} still need "
            f"to be watched because they can convert promise into delay if they dominate the sub-lord layer. "
            f"Current active obstruction count is {len(active_obstructions)}."
        ),
        (
            f"Cautionary cusp chains are presently showing through {', '.join(evaluation.caution_cusp_links[:3])}."
            if evaluation.caution_cusp_links
            else "No single cautionary cusp chain is dominating strongly, but the obstructing houses still need monitoring."
        ),
        "Automated event-promise ranking is stronger now, but still lighter than a full human KP consultation with rectification.",
        "Narrow timing beyond the active dasha chain should still be reviewed carefully against exact birth-time confidence.",
    ]
    plain_explanation = _build_plain_explanation(
        chart=chart,
        question=question,
        topic_name=topic.name,
        trend=trend,
        dominant_cusp=dominant_cusp,
        moon=moon,
        topic_context=topic_context,
        linked_planets=linked_planets,
        timing_window=optional_date_range or chart.dasha_summary.window,
        current_age=current_age,
        profession_signature=profession_signature,
        age_context=age_context,
        minor_projection=minor_projection,
    )

    caution_disclaimer = (
        "This response is an automated KP-style interpretation and should be treated as decision support, not certainty."
    )
    if topic.caution_level == "medical-disclaimer":
        caution_disclaimer = (
            "This is an automated KP-style interpretation only and not medical advice. Please use qualified healthcare guidance for health decisions."
        )
    if topic.caution_level == "legal-disclaimer":
        caution_disclaimer = (
            "This is an automated KP-style interpretation only and not legal advice. Please consult a qualified legal professional for legal decisions."
        )
    if topic.caution_level == "high-disclaimer":
        caution_disclaimer = (
            "This is an automated KP-style interpretation only and not financial advice, business advice, or trading guidance."
        )

    interpretation = [
        f"The question was classified under {topic.name}.",
        (
            f"The chart currently reads through lagna {lagna_cusp.sign}, janma rasi {moon.sign}, "
            f"and janma nakshatra {moon.nakshatra} pada {moon.pada}."
        ),
        (
            f"For this topic, house {dominant_cusp.house} is leading through sign lord {dominant_cusp.sign_lord}, "
            f"star lord {dominant_cusp.star_lord}, and sub lord {dominant_cusp.sub_lord}."
        ),
        (
            f"The stronger promise side of the chart points toward {topic_context['promise']}, while the caution side points toward "
            f"{topic_context['challenge']} if obstructing houses gain control."
        ),
        (
            f"Topic-rule review shows supportive cusp resonance through {', '.join(evaluation.supportive_cusp_links[:2]) or 'limited direct cusp resonance'}, "
            f"while caution rises through {', '.join(evaluation.caution_cusp_links[:2]) or 'general obstructing-house pressure'}."
        ),
        (
            f"The computed timing layer relies on the active dasha chain "
            f"{chart.dasha_summary.maha_dasha} / {chart.dasha_summary.bhukti} / {chart.dasha_summary.antara}."
        ),
        (
            f"At present the reading leans {trend}, with {linked_planets[0].planet if linked_planets else moon.planet} carrying a strong part "
            "of the active significator burden."
        ),
        "The automated answer should be read as a structured KP-style briefing, not as a substitute for a fully audited consultation.",
    ]
    if age_context["is_minor"]:
        interpretation.insert(
            2,
            str(age_context["interpretation_intro"]),
        )
        interpretation.insert(
            3,
            str(age_context["interpretation_direction"]).format(profession=profession_signature),
        )
    if minor_projection and minor_projection["interpretation_line"]:
        interpretation.insert(4 if age_context["is_minor"] else 2, str(minor_projection["interpretation_line"]))
    confidence = ConfidenceLevel(
        level="medium",
        reason="The astronomical chart and dasha timing are computed, but the automated interpretive rule base is still being deepened.",
    )
    calculation_trail = [
        CalculationTrailEntry(step="Question classification", detail=f"Mapped the question to topic {topic.name}."),
        CalculationTrailEntry(
            step="Jathakam context",
            detail=f"Referenced lagna {lagna_cusp.sign}, janma rasi {moon.sign}, and nakshatra {moon.nakshatra} pada {moon.pada}.",
        ),
        CalculationTrailEntry(
            step="House mapping",
            detail=f"Selected houses {', '.join(str(house) for house in topic.house_focus)} for this topic.",
        ),
        CalculationTrailEntry(
            step="Age context",
            detail=f"Computed current age as {current_age}. {age_context['trail_note']}",
        ),
        CalculationTrailEntry(
            step="Life-stage projection",
            detail=str(minor_projection["trail_note"]) if minor_projection else "No extra life-stage projection was needed.",
        ),
        CalculationTrailEntry(
            step="Rule evaluation",
            detail=(
                f"Support score {evaluation.support_score}, challenge score {evaluation.challenge_score}, "
                f"trend {evaluation.trend}, obstruction count {evaluation.obstruction_count}."
            ),
        ),
        CalculationTrailEntry(
            step="Cusp review",
            detail=(
                f"Referenced house {dominant_cusp.house} with sign lord {dominant_cusp.sign_lord}, "
                f"star lord {dominant_cusp.star_lord}, and sub lord {dominant_cusp.sub_lord}."
            ),
        ),
        CalculationTrailEntry(step="Timing review", detail=f"Referenced dasha window {chart.dasha_summary.window}."),
    ]

    return ChartQuestionResponse(
        question=question,
        classifiedTopic=topic.name,
        plainExplanation=plain_explanation,
        relevantHouses=topic.house_focus,
        cuspSubLordAnalysis=cusp_sub_lord_analysis,
        significatorAnalysis=significator_analysis,
        dashaSupport=dasha_support,
        supportingFactors=supporting_factors,
        blockingFactors=blocking_factors,
        interpretation=interpretation,
        possibleTimingWindow=optional_date_range or chart.dasha_summary.window,
        confidenceLevel=confidence,
        calculationTrail=calculation_trail,
        disclaimer=caution_disclaimer,
    )


def _infer_topic(question: str, fallback: str) -> QuestionTopic:
    normalized = question.lower()
    topic_map = get_supported_question_topics()

    keyword_groups = {
        "Career": ["career", "job", "promotion", "work", "profession", "professionally", "occupation", "employment"],
        "Marriage": ["marriage", "married", "partner", "relationship", "spouse", "marital", "wedding"],
        "Finance": ["finance", "financial", "money", "wealth", "income", "earning", "earnings", "savings", "rich", "prosperity"],
        "Foreign Settlement": ["foreign", "abroad", "relocation", "settlement", "overseas", "onsite", "country", "travel abroad", "move abroad"],
        "Property": ["property", "house", "home", "real estate", "land", "flat", "apartment", "buy house"],
        "Children": ["children", "child", "pregnancy", "family expansion", "baby", "conceive", "kids"],
        "Business": ["business", "startup", "partnership", "entrepreneur", "company", "trade", "self employment"],
        "Education": ["study", "studies", "education", "school", "college", "exam", "subject", "stream", "learning", "academic"],
        "Health Caution": ["health", "recovery", "stress", "illness", "medical", "disease", "eye", "vision", "sight", "eyesight"],
        "Legal Caution": ["legal", "court", "case", "litigation", "dispute", "lawsuit", "law", "settlement case"],
    }

    scores: dict[str, int] = {topic.name: 0 for topic in topic_map}
    for topic_name, keywords in keyword_groups.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[topic_name] += max(1, len(keyword.split()))

    best_topic = max(scores.items(), key=lambda item: item[1])
    if best_topic[1] > 0:
        return next(topic for topic in topic_map if topic.name == best_topic[0])

    for topic in topic_map:
        for keyword in keyword_groups.get(topic.name, []):
            if keyword in normalized:
                return topic

    for topic in topic_map:
        if topic.name.lower() == fallback.lower():
            return topic

    return topic_map[0]


def _resolve_birth_datetimes(date_of_birth: str, time_of_birth: str, timezone_name: str) -> tuple[datetime, datetime]:
    birth_local = datetime.fromisoformat(f"{date_of_birth}T{time_of_birth}").replace(tzinfo=ZoneInfo(timezone_name))
    return birth_local, birth_local.astimezone(UTC)


def _to_julian_day_ut(moment: datetime) -> float:
    hour = moment.hour + (moment.minute / 60) + (moment.second / 3600) + (moment.microsecond / 3_600_000_000)
    return swe.julday(moment.year, moment.month, moment.day, hour)


def _compute_house_longitudes(julian_day: float, latitude: float, longitude: float) -> list[float]:
    cusps, _ = swe.houses_ex(julian_day, latitude, longitude, HOUSE_SYSTEM, swe.FLG_SIDEREAL)
    return [float(value % 360) for value in cusps]


def _compute_planets(julian_day: float, house_longitudes: list[float]) -> list[ComputedPlanet]:
    planets: list[ComputedPlanet] = []

    for name in PLANET_ORDER:
        if name == "Ketu":
            rahu = next(planet for planet in planets if planet.name == "Rahu")
            longitude = (rahu.longitude + 180) % 360
            speed = rahu.speed
        else:
            xx, _ = swe.calc_ut(julian_day, PLANET_IDS[name], SIDEREAL_FLAGS)
            longitude = float(xx[0] % 360)
            speed = float(xx[3])

        sign, degree_label = _sign_and_degree(longitude)
        nakshatra, pada, star_lord, sub_lord = _nakshatra_details(longitude)
        house = _find_house_for_longitude(longitude, house_longitudes)

        planets.append(
            ComputedPlanet(
                name=name,
                longitude=longitude,
                speed=speed,
                house=house,
                sign=sign,
                degree_label=degree_label,
                nakshatra=nakshatra,
                pada=pada,
                star_lord=star_lord,
                sub_lord=sub_lord,
            )
        )

    return planets


def _planet_to_model(planet: ComputedPlanet) -> PlanetaryPosition:
    motion = "Retrograde" if planet.speed < 0 else "Direct"
    return PlanetaryPosition(
        planet=planet.name,
        sign=planet.sign,
        degree=planet.degree_label,
        nakshatra=planet.nakshatra,
        pada=planet.pada,
        starLord=planet.star_lord,
        subLord=planet.sub_lord,
        status=motion,
        note=(
            f"Computed in sidereal KP mode at house {planet.house}. "
            f"{planet.name} is moving {motion.lower()} at the sampled birth moment."
        ),
    )


def _build_house_cusps(house_longitudes: list[float]) -> list[HouseCusp]:
    cusps: list[HouseCusp] = []

    for house, longitude in enumerate(house_longitudes, start=1):
        sign, degree_label = _sign_and_degree(longitude)
        nakshatra, _, star_lord, sub_lord = _nakshatra_details(longitude)
        cusps.append(
            HouseCusp(
                house=house,
                sign=sign,
                cuspDegree=degree_label,
                signLord=SIGN_LORDS[sign],
                starLord=star_lord,
                subLord=sub_lord,
                note=(
                    f"Computed from sidereal Placidus/KP cusps. "
                    f"House {house} falls in {nakshatra} with sub lord {sub_lord}."
                ),
            )
        )

    return cusps


def _sign_and_degree(longitude: float) -> tuple[str, str]:
    sign_index = int(longitude // 30) % len(SIGNS)
    degrees_within_sign = longitude % 30
    return SIGNS[sign_index], _format_degree(degrees_within_sign)


def _nakshatra_details(longitude: float) -> tuple[str, int, str, str]:
    normalized = longitude % 360
    nakshatra_index = int(normalized // NAKSHATRA_SPAN)
    offset = normalized - (nakshatra_index * NAKSHATRA_SPAN)
    pada = int(offset // PADA_SPAN) + 1
    star_lord = NAKSHATRA_LORDS[nakshatra_index]
    sub_lord = _sub_lord_from_offset(offset, star_lord)
    return NAKSHATRAS[nakshatra_index], pada, star_lord, sub_lord


def _sub_lord_from_offset(offset: float, star_lord: str) -> str:
    start_index = VIMSHOTTARI_SEQUENCE.index(star_lord)
    running = 0.0

    for lord in islice(cycle(VIMSHOTTARI_SEQUENCE), start_index, start_index + len(VIMSHOTTARI_SEQUENCE)):
        running += NAKSHATRA_SPAN * (DASHA_YEARS[lord] / 120)
        if offset <= running + 1e-9:
            return lord

    return star_lord


def _find_house_for_longitude(longitude: float, house_longitudes: list[float]) -> int:
    for index, start in enumerate(house_longitudes):
        end = house_longitudes[(index + 1) % len(house_longitudes)]
        if _longitude_in_arc(longitude, start, end):
            return index + 1

    return 12


def _longitude_in_arc(value: float, start: float, end: float) -> bool:
    adjusted_value = value
    adjusted_end = end
    if adjusted_end <= start:
        adjusted_end += 360
    if adjusted_value < start:
        adjusted_value += 360
    return start <= adjusted_value < adjusted_end


def _build_dasha_summary(birth_utc: datetime, moon_longitude: float) -> DashaPeriod:
    maha, balance_fraction = _moon_maha_balance(moon_longitude)
    maha_duration = _years_to_timedelta(DASHA_YEARS[maha])
    maha_start = birth_utc - (maha_duration * (1 - balance_fraction))
    target = datetime.combine(date.today(), time.min, tzinfo=UTC)
    current_maha = _locate_dasha_segment("Maha Dasha", maha_start, maha, target)
    current_bhukti = _locate_child_dasha("Bhukti", current_maha, target)
    current_antara = _locate_child_dasha("Antara", current_bhukti, target)

    return DashaPeriod(
        mahaDasha=current_maha.lord,
        bhukti=current_bhukti.lord,
        antara=current_antara.lord,
        window=f"{current_antara.start.date().isoformat()} to {current_antara.end.date().isoformat()}",
        mahaWindow=f"{current_maha.start.date().isoformat()} to {current_maha.end.date().isoformat()}",
        bhuktiWindow=f"{current_bhukti.start.date().isoformat()} to {current_bhukti.end.date().isoformat()}",
        antaraWindow=f"{current_antara.start.date().isoformat()} to {current_antara.end.date().isoformat()}",
        status="Computed",
        note=(
            f"Computed from Moon longitude in {NAKSHATRAS[int((moon_longitude % 360) // NAKSHATRA_SPAN)]}. "
            "The active window shown here is the current antara period."
        ),
    )


def _build_birth_dasha_snapshot(birth_utc: datetime, moon_longitude: float) -> BirthDashaSnapshot:
    maha, balance_fraction = _moon_maha_balance(moon_longitude)
    maha_duration = _years_to_timedelta(DASHA_YEARS[maha])
    maha_start = birth_utc - (maha_duration * (1 - balance_fraction))
    birth_maha = _locate_dasha_segment("Maha Dasha", maha_start, maha, birth_utc)
    birth_bhukti = _locate_child_dasha("Bhukti", birth_maha, birth_utc)
    birth_antara = _locate_child_dasha("Antara", birth_bhukti, birth_utc)

    return BirthDashaSnapshot(
        mahaDasha=birth_maha.lord,
        bhukti=birth_bhukti.lord,
        antara=birth_antara.lord,
        balanceAtBirth=_format_duration_years_months(birth_maha.end - birth_utc),
        note=(
            f"At birth the native entered life under {birth_maha.lord} maha dasha, "
            f"{birth_bhukti.lord} bhukti, and {birth_antara.lord} antara."
        ),
    )


def _build_lifetime_dasha_timeline(
    birth_utc: datetime,
    moon_longitude: float,
    planetary_positions: list[PlanetaryPosition],
    house_cusps: list[HouseCusp],
    *,
    years: int,
) -> list[DashaTimelineEntry]:
    maha, balance_fraction = _moon_maha_balance(moon_longitude)
    maha_duration = _years_to_timedelta(DASHA_YEARS[maha])
    maha_start = birth_utc - (maha_duration * (1 - balance_fraction))
    horizon = birth_utc + _years_to_timedelta(years)
    current_start = maha_start
    current_index = VIMSHOTTARI_SEQUENCE.index(maha)
    entries: list[DashaTimelineEntry] = []

    while current_start < horizon:
        lord = VIMSHOTTARI_SEQUENCE[current_index % len(VIMSHOTTARI_SEQUENCE)]
        end = current_start + _years_to_timedelta(DASHA_YEARS[lord])
        if end <= birth_utc:
            current_start = end
            current_index += 1
            continue

        clipped_start = max(current_start, birth_utc)
        clipped_end = min(end, horizon)
        assessment = _assess_period_ruler(lord, planetary_positions, house_cusps)
        entries.append(
            DashaTimelineEntry(
                level="Maha Dasha",
                ruler=lord,
                startDate=clipped_start.date().isoformat(),
                endDate=clipped_end.date().isoformat(),
                startAge=_years_between(birth_utc, clipped_start),
                endAge=_years_between(birth_utc, clipped_end),
                quality=assessment["quality"],
                focus=assessment["focus"],
                goodIndicators=assessment["good_indicators"],
                cautionIndicators=assessment["caution_indicators"],
                remedies=assessment["remedies"],
            )
        )
        current_start = end
        current_index += 1

    return entries


def _moon_maha_balance(moon_longitude: float) -> tuple[str, float]:
    normalized = moon_longitude % 360
    nakshatra_index = int(normalized // NAKSHATRA_SPAN)
    star_lord = NAKSHATRA_LORDS[nakshatra_index]
    offset = normalized - (nakshatra_index * NAKSHATRA_SPAN)
    traversed_fraction = offset / NAKSHATRA_SPAN
    balance_fraction = 1 - traversed_fraction
    return star_lord, balance_fraction


def _locate_dasha_segment(level: str, start: datetime, start_lord: str, target: datetime) -> DashaSegment:
    current_start = start
    current_index = VIMSHOTTARI_SEQUENCE.index(start_lord)

    while True:
        lord = VIMSHOTTARI_SEQUENCE[current_index % len(VIMSHOTTARI_SEQUENCE)]
        duration = _years_to_timedelta(DASHA_YEARS[lord])
        end = current_start + duration
        if target < end:
            return DashaSegment(level=level, lord=lord, start=current_start, end=end)
        current_start = end
        current_index += 1


def _locate_child_dasha(level: str, parent: DashaSegment, target: datetime) -> DashaSegment:
    parent_days = (parent.end - parent.start).total_seconds() / 86400
    start_index = VIMSHOTTARI_SEQUENCE.index(parent.lord)
    current_start = parent.start

    for lord in islice(cycle(VIMSHOTTARI_SEQUENCE), start_index, start_index + len(VIMSHOTTARI_SEQUENCE)):
        duration = timedelta(days=parent_days * (DASHA_YEARS[lord] / 120))
        end = current_start + duration
        if target < end:
            return DashaSegment(level=level, lord=lord, start=current_start, end=end)
        current_start = end

    return DashaSegment(level=level, lord=parent.lord, start=parent.start, end=parent.end)


def _years_to_timedelta(years: float) -> timedelta:
    return timedelta(days=years * DASHA_YEAR_DAYS)


def _years_between(start: datetime, end: datetime) -> float:
    return round((end - start).total_seconds() / 86400 / DASHA_YEAR_DAYS, 1)


def _format_duration_years_months(delta: timedelta) -> str:
    total_days = max(delta.total_seconds(), 0) / 86400
    total_months = int(round(total_days / 30.436875))
    years = total_months // 12
    months = total_months % 12
    year_label = "year" if years == 1 else "years"
    month_label = "month" if months == 1 else "months"
    if years and months:
        return f"{years} {year_label} {months} {month_label}"
    if years:
        return f"{years} {year_label}"
    return f"{months} {month_label}"


def _select_linked_planets(
    planetary_positions: list[PlanetaryPosition], relevant_cusps: list[HouseCusp]
) -> list[PlanetaryPosition]:
    lord_pool = {
        cusp.sign_lord
        for cusp in relevant_cusps
    } | {
        cusp.star_lord
        for cusp in relevant_cusps
    } | {
        cusp.sub_lord
        for cusp in relevant_cusps
    }
    linked = [planet for planet in planetary_positions if planet.planet in lord_pool]
    if linked:
        return linked
    return planetary_positions[:2]


def _derive_trend(support_score: int, challenge_score: int, active_obstruction_count: int) -> str:
    adjusted_challenge = challenge_score + (active_obstruction_count * 2)
    if support_score >= adjusted_challenge + 4:
        return "supportive"
    if adjusted_challenge > support_score:
        return "challenging"
    return "mixed"


def _evaluate_topic_rules(
    house_cusps: list[HouseCusp],
    relevant_cusps: list[HouseCusp],
    topic_context: dict[str, object],
    active_dasha_lords: set[str],
    support_score: int,
    challenge_score: int,
    obstruction_count: int,
) -> TopicEvaluation:
    supportive_houses = set(topic_context["supporting"])
    challenging_houses = set(topic_context["challenging"])
    supportive_cusp_links: list[str] = []
    caution_cusp_links: list[str] = []
    dasha_resonance: list[str] = []

    for cusp in relevant_cusps:
        chain = f"H{cusp.house} {cusp.sign_lord}/{cusp.star_lord}/{cusp.sub_lord}"
        if cusp.house in supportive_houses:
            supportive_cusp_links.append(chain)
        if cusp.house in challenging_houses:
            caution_cusp_links.append(chain)
        if {cusp.sign_lord, cusp.star_lord, cusp.sub_lord} & active_dasha_lords:
            dasha_resonance.append(chain)

    for cusp in house_cusps:
        chain = f"H{cusp.house} {cusp.sign_lord}/{cusp.star_lord}/{cusp.sub_lord}"
        if cusp.house in challenging_houses and cusp.sub_lord in active_dasha_lords:
            caution_cusp_links.append(chain)

    trend = _derive_trend(support_score, challenge_score, obstruction_count)
    return TopicEvaluation(
        support_score=support_score,
        challenge_score=challenge_score,
        trend=trend,
        supportive_cusp_links=_dedupe_preserve_order(supportive_cusp_links),
        caution_cusp_links=_dedupe_preserve_order(caution_cusp_links),
        dasha_resonance=_dedupe_preserve_order(dasha_resonance),
        obstruction_count=obstruction_count,
    )


def _build_plain_explanation(
    *,
    chart: ChartData,
    question: str,
    topic_name: str,
    trend: str,
    dominant_cusp: HouseCusp,
    moon: PlanetaryPosition,
    topic_context: dict[str, object],
    linked_planets: list[PlanetaryPosition],
    timing_window: str,
    current_age: int,
    profession_signature: str,
    age_context: dict[str, str | bool],
    minor_projection: dict[str, str | list[str]] | None,
) -> str:
    concern = _describe_concern(question, topic_name)
    lead_planet = linked_planets[0].planet if linked_planets else moon.planet
    trend_phrase = _describe_trend_phrase(topic_name, trend, topic_context)
    if age_context["is_minor"]:
        timing_phrase = (
            f"{age_context['plain_timing_intro']} "
            f"The strongest immediate timing focus stays at {timing_window}, but for {topic_name.lower()} matters it should be treated as a formative or preparatory period rather than a literal adult-event window."
        )
    else:
        timing_phrase = (
            f"The strongest timing focus in this answer is {timing_window}, under the active dasha chain "
            f"{chart.dasha_summary.maha_dasha} / {chart.dasha_summary.bhukti} / {chart.dasha_summary.antara}."
        )
    chart_phrase = (
        f"This reading is being anchored through {chart.house_cusps[0].sign} lagna, {moon.sign} janma rasi, "
        f"and {moon.nakshatra} nakshatra, with house {dominant_cusp.house} currently leading the topic through "
        f"{dominant_cusp.sign_lord}, {dominant_cusp.star_lord}, and {dominant_cusp.sub_lord}."
    )
    emphasis_phrase = (
        f"Right now, {lead_planet} is carrying an important part of the active significator load for this question."
    )
    profession_phrase = (
        str(age_context["plain_direction"]).format(profession=profession_signature)
        if age_context["is_minor"]
        else ""
    )
    projection_phrase = str(minor_projection["plain_line"]) if minor_projection else ""

    return " ".join(
        part
        for part in [concern, trend_phrase, timing_phrase, profession_phrase, projection_phrase, chart_phrase, emphasis_phrase]
        if part
    )


def _describe_concern(question: str, topic_name: str) -> str:
    normalized = question.lower()
    if any(keyword in normalized for keyword in ["eye", "eyes", "vision", "sight", "eyesight"]):
        return "For the specific concern of eye health, the chart does not currently read like a severe danger signal."
    if "education" in normalized or "study" in normalized or "school" in normalized:
        return "For this education question, the app is reading the chart through learning growth, aptitude formation, and subject-direction signals."
    if any(keyword in normalized for keyword in ["marriage", "partner", "relationship"]):
        return "For this relationship question, the app is reading the chart as a question of commitment timing and emotional stability."
    if any(keyword in normalized for keyword in ["job", "career", "promotion", "work"]):
        return "For this career question, the app is reading the chart in KP style through houses 2, 6, 10, and 11, with special attention to profession promise, development stage, and realistic timing."
    if any(keyword in normalized for keyword in ["business", "finance", "money", "wealth"]):
        return "For this practical-life question, the app is reading the chart through future responsibility, skill-use, and the kind of life pattern the native may grow into."
    if any(keyword in normalized for keyword in ["foreign", "abroad", "overseas", "relocation", "settlement"]):
        return "For this foreign-settlement question, the app is reading the chart through movement houses, adaptability, and the longer-term possibility of living away from the birth environment."
    if topic_name == "Health Caution":
        return "For this health-related question, the chart should be read more as an early caution and management signal than as certainty."
    return f"For this {topic_name.lower()} question, the app is trying to summarize the chart in a more practical plain-language way."


def _describe_trend_phrase(topic_name: str, trend: str, topic_context: dict[str, object]) -> str:
    promise = str(topic_context["promise"])
    challenge = str(topic_context["challenge"])

    if trend == "supportive":
        return (
            f"The current reading leans supportive, which means the stronger side of the chart points more toward "
            f"{promise} than toward {challenge}."
        )
    if trend == "challenging":
        return (
            f"The current reading is more cautionary, which means the chart is showing more risk of "
            f"{challenge} than of {promise} right now."
        )
    return (
        f"The current reading is mixed, so the chart shows both the possibility of {promise} and the need to watch "
        f"for {challenge} before making a strong conclusion."
    )


def _current_age(date_of_birth: str, as_of: date | None = None) -> int:
    today = as_of or date.today()
    birth_date = date.fromisoformat(date_of_birth)
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(years, 0)


def _build_age_context(topic_name: str, current_age: int, profession_signature: str) -> dict[str, str | bool]:
    if current_age >= 18:
        return {
            "is_minor": False,
            "timing_intro": "",
            "direction_line": "",
            "support_line": "",
            "interpretation_intro": "",
            "interpretation_direction": "",
            "trail_note": "No child-age reframing was needed.",
            "plain_timing_intro": "",
            "plain_direction": "",
        }

    if topic_name == "Career":
        return {
            "is_minor": True,
            "timing_intro": f"The native is currently {current_age} years old, so this career question is being read as a future profession and development question, not as immediate job-entry timing.",
            "direction_line": "Professional inclination currently leans toward {profession} when the chart is read through house {house} and the stronger significators.",
            "support_line": "Age-aware chart reading is active here, so the app is prioritizing aptitude, stream formation, and future career direction over present-day employment events.",
            "interpretation_intro": f"Because the native is currently {current_age} years old, this should be read for future profession direction rather than immediate job timing.",
            "interpretation_direction": "The chart's present profession signature leans toward {profession}.",
            "trail_note": "Applied child-career reframing logic.",
            "plain_timing_intro": f"Because the native is currently {current_age} years old, this should not be read as current job timing. Instead, the chart is being read for future profession direction, development years, and eventual entry into working life.",
            "plain_direction": "The longer-term professional signature currently leans toward {profession}.",
        }

    if topic_name == "Education":
        return {
            "is_minor": True,
            "timing_intro": f"The native is currently {current_age} years old, so this education question is being read through school growth, learning style, and future stream direction.",
            "direction_line": "Educational inclination currently leans toward {profession} when the chart is read through house {house} and the stronger significators.",
            "support_line": "Age-aware chart reading is active here, so the app is prioritizing learning pattern, subject affinity, discipline, and stream choice over adult outcome language.",
            "interpretation_intro": f"Because the native is currently {current_age} years old, this should be read for academic development, subject direction, and later stream selection.",
            "interpretation_direction": "The present educational signature leans toward {profession}.",
            "trail_note": "Applied child-education reframing logic.",
            "plain_timing_intro": f"Because the native is currently {current_age} years old, this should be read as an education-development question rather than as a final adult-result question.",
            "plain_direction": "The longer-term educational and aptitude signature currently leans toward {profession}.",
        }

    if topic_name in {"Marriage", "Business", "Finance", "Legal Caution"}:
        label = {
            "Marriage": "future relationship and maturity",
            "Business": "future commercial aptitude and independence",
            "Finance": "future money-management and earning pattern",
            "Legal Caution": "future responsibility and conflict-handling pattern",
        }[topic_name]
        return {
            "is_minor": True,
            "timing_intro": f"The native is currently {current_age} years old, so this {topic_name.lower()} question is being reframed through {label} rather than immediate adult-event timing.",
            "direction_line": "The chart is being read through house {house} for future pattern-building, with a longer-term inclination toward {profession}.",
            "support_line": f"Age-aware chart reading is active here, so the app is avoiding literal adult-event timing and instead focusing on future life-pattern indicators for {topic_name.lower()}.",
            "interpretation_intro": f"Because the native is currently {current_age} years old, this should be read for future pattern and maturity rather than present adult-event timing.",
            "interpretation_direction": "The longer-term directional signature currently leans toward {profession}.",
            "trail_note": f"Applied child-{topic_name.lower().replace(' ', '-') } reframing logic.",
            "plain_timing_intro": f"Because the native is currently {current_age} years old, this should not be read as an immediate adult-event question. Instead, the chart is being read for future tendency, maturity pattern, and later-life expression.",
            "plain_direction": "The longer-term life-pattern signature currently leans toward {profession}.",
        }

    if topic_name == "Health Caution":
        return {
            "is_minor": True,
            "timing_intro": f"The native is currently {current_age} years old, so this health question is being read with child-development and care context, not adult health-burden language.",
            "direction_line": "The chart is being read through house {house} for recovery support, sensitivity points, and the kind of care pattern that may help, with a supporting signature around {profession}.",
            "support_line": "Age-aware chart reading is active here, so the app is prioritizing resilience, care, monitoring, and developmental sensitivity over adult-disease framing.",
            "interpretation_intro": f"Because the native is currently {current_age} years old, this should be read with child-health caution, monitoring, and recovery context.",
            "interpretation_direction": "The longer-term support signature currently leans toward {profession}.",
            "trail_note": "Applied child-health reframing logic.",
            "plain_timing_intro": f"Because the native is currently {current_age} years old, this should be read through monitoring, care, resilience, and developmental sensitivity rather than heavy adult health language.",
            "plain_direction": "",
        }

    return {
        "is_minor": False,
        "timing_intro": "",
        "direction_line": "",
        "support_line": "",
        "interpretation_intro": "",
        "interpretation_direction": "",
        "trail_note": "No child-age reframing was needed.",
        "plain_timing_intro": "",
        "plain_direction": "",
    }


def _build_minor_projection(
    *,
    chart: ChartData,
    topic_name: str,
    current_age: int,
    dominant_cusp: HouseCusp,
    linked_planets: list[PlanetaryPosition],
    profession_signature: str,
) -> dict[str, str | list[str]] | None:
    if current_age >= 18:
        return None

    if topic_name == "Career":
        return _build_minor_career_projection(chart, current_age, dominant_cusp, linked_planets, profession_signature)
    if topic_name == "Education":
        return _build_minor_education_projection(chart, current_age, dominant_cusp, profession_signature)
    return _build_general_minor_projection(chart, topic_name, current_age, dominant_cusp, profession_signature)


def _build_minor_career_projection(
    chart: ChartData,
    current_age: int,
    dominant_cusp: HouseCusp,
    linked_planets: list[PlanetaryPosition],
    profession_signature: str,
) -> dict[str, str | list[str]]:
    school_end_age = max(17, min(18, current_age + max(18 - current_age, 0)))
    stream_start_age = min(max(current_age + 2, 14), 16)
    stream_end_age = max(stream_start_age + 1, 17)
    training_start_age = max(stream_end_age, 17)
    training_end_age = training_start_age + _training_year_span(profession_signature)
    entry_start_age, entry_end_age = _profession_entry_age_band(profession_signature)
    school_years_left = max(school_end_age - current_age, 1)
    study_to_entry_years = max(entry_start_age - current_age, 1)
    source_planets = [planet.planet for planet in linked_planets[:2]] or [dominant_cusp.sign_lord, dominant_cusp.star_lord]
    role_examples = _profession_role_examples(source_planets, profession_signature)
    stream_window = _age_year_window(chart.birth_summary.date_of_birth, stream_start_age, stream_end_age)
    training_window = _age_year_window(chart.birth_summary.date_of_birth, training_start_age, training_end_age)
    entry_window = _age_year_window(chart.birth_summary.date_of_birth, entry_start_age, entry_end_age)
    entry_dasha = _timeline_window_for_age_band(chart.lifetime_dasha_timeline, entry_start_age, entry_end_age)

    plain_line = (
        f"In practical life terms, the native is likely to stay in structured study for about another {school_years_left} year"
        f"{'' if school_years_left == 1 else 's'}, with stronger stream-selection years around age {stream_start_age} to {stream_end_age} "
        f"({stream_window}). Higher-study or professional training is more likely around age {training_start_age} to {training_end_age} "
        f"({training_window}), and actual job-entry promise should be judged more seriously around age {entry_start_age} to {entry_end_age} "
        f"({entry_window}), not in the present child-age window. The profession pattern currently points most strongly toward {profession_signature}, "
        f"which can show up later as roles such as {role_examples}."
    )
    interpretation_line = (
        f"KP life-stage judgment: age {current_age} is still a preparation phase; age {stream_start_age}-{stream_end_age} is better for stream sorting, "
        f"age {training_start_age}-{training_end_age} for training, and age {entry_start_age}-{entry_end_age} for clearer profession-entry signals. "
        f"The house {dominant_cusp.house} chain {dominant_cusp.sign_lord}/{dominant_cusp.star_lord}/{dominant_cusp.sub_lord} currently favors {profession_signature}."
    )
    support_line = (
        f"The answer is now being framed through human life-stage logic as well as KP logic: about {study_to_entry_years} more years remain before the chart should be tested for literal job-entry timing, "
        f"so the current period is better for aptitude, stream, and training analysis."
    )
    dasha_lines = [
        f"The native is currently {current_age} years old, so the present chart period is not being treated as literal employment timing.",
        f"Age {stream_start_age} to {stream_end_age} ({stream_window}) is the stronger window for stream selection, interest sorting, and noticing whether the chart leans more toward {profession_signature}.",
        f"Age {training_start_age} to {training_end_age} ({training_window}) is better for higher study, coaching, professional preparation, and skill consolidation.",
        f"Age {entry_start_age} to {entry_end_age} ({entry_window}) is the first more realistic band for job-entry judgment. {entry_dasha}",
        *_build_minor_topic_yearly_outlook("Career", current_age),
    ]
    return {
        "plain_line": plain_line,
        "interpretation_line": interpretation_line,
        "support_line": support_line,
        "dasha_lines": dasha_lines,
        "trail_note": (
            f"Projected school years left={school_years_left}, stream window age {stream_start_age}-{stream_end_age}, "
            f"training window age {training_start_age}-{training_end_age}, and entry window age {entry_start_age}-{entry_end_age}."
        ),
    }


def _build_minor_education_projection(
    chart: ChartData,
    current_age: int,
    dominant_cusp: HouseCusp,
    profession_signature: str,
) -> dict[str, str | list[str]]:
    stream_start_age = min(max(current_age + 2, 14), 16)
    stream_end_age = max(stream_start_age + 1, 17)
    stream_window = _age_year_window(chart.birth_summary.date_of_birth, stream_start_age, stream_end_age)
    plain_line = (
        f"The chart should be read with present schooling in mind. The stronger sorting years for subject preference and later stream clarity are around age "
        f"{stream_start_age} to {stream_end_age} ({stream_window}), and the current educational signature leans toward {profession_signature}."
    )
    interpretation_line = (
        f"KP education judgment: house {dominant_cusp.house} with {dominant_cusp.sign_lord}/{dominant_cusp.star_lord}/{dominant_cusp.sub_lord} should be used to watch memory, discipline, "
        f"subject affinity, and eventual stream choice rather than forcing an adult profession promise too early."
    )
    return {
        "plain_line": plain_line,
        "interpretation_line": interpretation_line,
        "support_line": "The answer is being adjusted for school-age reality, so current years are read more for subject direction than for final-life outcome.",
        "dasha_lines": [
            f"The native is currently {current_age} years old, so the present educational reading is about growth, subject comfort, and future stream clarity.",
            f"Age {stream_start_age} to {stream_end_age} ({stream_window}) should be watched more carefully for clearer academic direction and stronger specialization signals.",
            *_build_minor_topic_yearly_outlook("Education", current_age),
        ],
        "trail_note": f"Projected education-stream window at age {stream_start_age}-{stream_end_age}.",
    }


def _build_general_minor_projection(
    chart: ChartData,
    topic_name: str,
    current_age: int,
    dominant_cusp: HouseCusp,
    topic_signature: str,
) -> dict[str, str | list[str]]:
    maturity_start_age, maturity_end_age = _minor_topic_maturity_window(topic_name)
    maturity_window = _age_year_window(chart.birth_summary.date_of_birth, maturity_start_age, maturity_end_age)
    topic_label = _minor_topic_label(topic_name)

    if topic_name == "Health Caution":
        plain_line = (
            f"At this age the chart should be used mainly for monitoring, routine, resilience, and parental awareness. "
            f"More independent self-management years begin around age {maturity_start_age} to {maturity_end_age} ({maturity_window}), "
            f"and the present health-support signature leans toward {topic_signature}."
        )
        interpretation_line = (
            f"KP child-health judgment: house {dominant_cusp.house} with {dominant_cusp.sign_lord}/{dominant_cusp.star_lord}/{dominant_cusp.sub_lord} "
            f"should be used to track sensitivity, recovery support, and manageable caution points rather than adult-disease language."
        )
        support_line = (
            "The answer is being reframed with child-health logic, so the chart is being read for resilience, care pattern, and follow-up discipline."
        )
        dasha_lines = [
            f"The native is currently {current_age} years old, so health timing is being read for routine, monitoring, and developmental care rather than adult burden.",
            f"Age {maturity_start_age} to {maturity_end_age} ({maturity_window}) is a better window for judging how strongly self-management habits and resilience develop.",
            *_build_minor_topic_yearly_outlook(topic_name, current_age),
        ]
        trail_note = f"Projected child-health self-management window at age {maturity_start_age}-{maturity_end_age}."
    else:
        plain_line = (
            f"Because the native is still a minor, this question should be read first through {topic_label}, family environment, and gradual maturity. "
            f"The stronger years for literal {topic_name.lower()} judgment are around age {maturity_start_age} to {maturity_end_age} ({maturity_window}), "
            f"and the current long-range signature leans toward {topic_signature}."
        )
        interpretation_line = (
            f"KP age-stage judgment for {topic_name.lower()}: house {dominant_cusp.house} with {dominant_cusp.sign_lord}/{dominant_cusp.star_lord}/{dominant_cusp.sub_lord} "
            f"should first be read for pattern-building and later maturity. More literal event judgment becomes meaningful around age {maturity_start_age}-{maturity_end_age}."
        )
        support_line = (
            f"The answer is being adjusted for age reality, so current years are being read for {topic_label} rather than literal adult-event timing."
        )
        dasha_lines = [
            f"The native is currently {current_age} years old, so this {topic_name.lower()} question is being read through child-to-young-adult development rather than immediate adult timing.",
            f"Age {maturity_start_age} to {maturity_end_age} ({maturity_window}) is the stronger band for more literal {topic_name.lower()} judgment in this chart.",
            *_build_minor_topic_yearly_outlook(topic_name, current_age),
        ]
        trail_note = f"Projected maturity window for {topic_name.lower()} at age {maturity_start_age}-{maturity_end_age}."

    return {
        "plain_line": plain_line,
        "interpretation_line": interpretation_line,
        "support_line": support_line,
        "dasha_lines": dasha_lines,
        "trail_note": trail_note,
    }


def _minor_topic_maturity_window(topic_name: str) -> tuple[int, int]:
    mapping = {
        "Marriage": (23, 30),
        "Finance": (22, 30),
        "Foreign Settlement": (21, 29),
        "Property": (25, 35),
        "Children": (25, 34),
        "Business": (23, 32),
        "Legal Caution": (18, 25),
        "Health Caution": (15, 20),
    }
    return mapping.get(topic_name, (18, 24))


def _minor_topic_label(topic_name: str) -> str:
    mapping = {
        "Marriage": "emotional maturity and future relationship pattern",
        "Finance": "money habits, resource attitude, and later earning pattern",
        "Foreign Settlement": "adaptability, travel tendency, and later relocation potential",
        "Property": "family stability, domestic support, and future settlement tendency",
        "Children": "nurturing tendency, family values, and future parenting pattern",
        "Business": "initiative, independence, and future enterprise tendency",
        "Legal Caution": "responsibility, discipline, and conflict-handling pattern",
        "Health Caution": "care routine and resilience pattern",
    }
    return mapping.get(topic_name, "future maturity pattern")


def _training_year_span(profession_signature: str) -> int:
    normalized = profession_signature.lower()
    if any(keyword in normalized for keyword in ["teaching", "advisory", "guidance", "research", "diagnostics", "specialist"]):
        return 5
    if any(keyword in normalized for keyword in ["engineering", "analysis", "technology", "digital", "technical"]):
        return 4
    return 3


def _profession_entry_age_band(profession_signature: str) -> tuple[int, int]:
    normalized = profession_signature.lower()
    if any(keyword in normalized for keyword in ["teaching", "advisory", "guidance", "research", "diagnostics", "specialist"]):
        return (23, 26)
    if any(keyword in normalized for keyword in ["engineering", "analysis", "technology", "digital", "technical"]):
        return (21, 24)
    return (20, 23)


def _profession_role_examples(source_planets: list[str], profession_signature: str) -> str:
    role_map = {
        "Sun": ["administration", "leadership-track work", "public-facing responsibility"],
        "Moon": ["teaching support", "care-oriented work", "education-facing roles"],
        "Mars": ["engineering", "operations", "technical execution"],
        "Mercury": ["software", "analytics", "communication-heavy work"],
        "Jupiter": ["teaching", "advisory work", "knowledge-led guidance"],
        "Venus": ["design", "media", "presentation-oriented roles"],
        "Saturn": ["systems work", "compliance", "structured administration"],
        "Rahu": ["digital platforms", "modern technology", "foreign-linked industries"],
        "Ketu": ["research", "diagnostics", "specialist back-end work"],
    }
    roles: list[str] = []
    for planet in source_planets:
        roles.extend(role_map.get(planet, []))

    if not roles:
        normalized = profession_signature.lower()
        if "technology" in normalized or "digital" in normalized:
            roles = ["software", "analytics", "technical platforms"]
        elif "design" in normalized or "creative" in normalized:
            roles = ["design", "content", "presentation-oriented work"]
        else:
            roles = ["knowledge-based work", "structured service roles", "professional support work"]

    unique_roles: list[str] = []
    for role in roles:
        if role not in unique_roles:
            unique_roles.append(role)
    return ", ".join(unique_roles[:3])


def _age_year_window(date_of_birth: str, start_age: int, end_age: int) -> str:
    birth = date.fromisoformat(date_of_birth)
    start_year = birth.year + start_age
    end_year = birth.year + end_age
    return f"{start_year}-{end_year}"


def _timeline_window_for_age_band(
    timeline: list[DashaTimelineEntry],
    start_age: int,
    end_age: int,
) -> str:
    matching = [
        entry
        for entry in timeline
        if not (entry.end_age < start_age or entry.start_age > end_age)
    ]
    if not matching:
        return "The lifetime dasha ladder should be checked again near that age band for exact entry timing."

    rulers = ", ".join(dict.fromkeys(entry.ruler for entry in matching[:2]))
    return f"That future profession-entry band falls mainly under {rulers} maha-dasha influence in the current computed lifetime ladder."


def _assess_period_ruler(
    lord: str,
    planetary_positions: list[PlanetaryPosition],
    house_cusps: list[HouseCusp],
) -> dict[str, str | list[str]]:
    links = _collect_house_links_for_lord(lord, planetary_positions, house_cusps)
    supportive = [house for house in links if house in GENERAL_SUPPORTIVE_HOUSES]
    cautionary = [house for house in links if house in GENERAL_CHALLENGING_HOUSES]
    quality = "supportive"
    if len(cautionary) > len(supportive):
        quality = "challenging"
    elif cautionary and len(cautionary) == len(supportive):
        quality = "mixed"

    unique_supportive = _unique_house_list(supportive)
    unique_cautionary = _unique_house_list(cautionary)
    focus_domains = _planet_career_domains(lord)
    focus = (
        f"{lord} period emphasizes {focus_domains[0]} while activating "
        f"{_format_house_theme_list(unique_supportive or _unique_house_list(links[:3]))}."
    )
    good_indicators = (
        [f"Supports {HOUSE_THEMES[house]} through house {house} linkage." for house in unique_supportive[:3]]
        or ["Provides general chart support through its ruler connections."]
    )
    caution_indicators = (
        [f"Needs caution around {HOUSE_THEMES[house]} through house {house} linkage." for house in unique_cautionary[:3]]
        or ["No major cautionary house dominance is standing out in this period."]
    )
    remedies = _build_ruler_remedies(lord, unique_cautionary)

    return {
        "quality": quality,
        "focus": focus,
        "good_indicators": good_indicators,
        "caution_indicators": caution_indicators,
        "remedies": remedies,
    }


def _collect_house_links_for_lord(
    lord: str,
    planetary_positions: list[PlanetaryPosition],
    house_cusps: list[HouseCusp],
) -> list[int]:
    houses: list[int] = []
    planet = next((item for item in planetary_positions if item.planet == lord), None)
    if planet:
        occupied = _extract_house_from_note(planet.note)
        if occupied is not None:
            houses.append(occupied)
        houses.extend(_houses_with_lord(house_cusps, lord, "sign"))
        houses.extend(_houses_with_lord(house_cusps, lord, "star"))
        houses.extend(_houses_with_lord(house_cusps, lord, "sub"))
        houses.extend(_houses_with_lord(house_cusps, SIGN_LORDS[planet.sign], "sign"))
    else:
        houses.extend(_houses_with_lord(house_cusps, lord, "sign"))
        houses.extend(_houses_with_lord(house_cusps, lord, "star"))
        houses.extend(_houses_with_lord(house_cusps, lord, "sub"))
    return houses


def _unique_house_list(houses: list[int]) -> list[int]:
    return sorted(set(house for house in houses if 1 <= house <= 12))


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _format_house_theme_list(houses: list[int]) -> str:
    if not houses:
        return "general chart themes"
    labels = [HOUSE_THEMES[house] for house in houses[:3]]
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return f"{labels[0]}, {labels[1]}, and {labels[2]}"


def _build_general_kp_strengths(
    planetary_positions: list[PlanetaryPosition],
    house_cusps: list[HouseCusp],
    dasha_summary: DashaPeriod,
) -> list[str]:
    assessments = [
        _assess_period_ruler(dasha_summary.maha_dasha, planetary_positions, house_cusps),
        _assess_period_ruler(dasha_summary.bhukti, planetary_positions, house_cusps),
        _assess_period_ruler(dasha_summary.antara, planetary_positions, house_cusps),
    ]
    ascendant = house_cusps[0]
    return [
        f"Lagna rises in {ascendant.sign} with star lord {ascendant.star_lord} and sub lord {ascendant.sub_lord}, which becomes the main KP anchor for the whole chart.",
        f"The active dasha chain {dasha_summary.maha_dasha} / {dasha_summary.bhukti} / {dasha_summary.antara} currently shows this period focus: {assessments[0]['focus']}",
        f"Supportive chart houses are presently strongest through {_format_house_theme_list([1, 5, 9])}, together with {_format_house_theme_list([10, 11])}.",
    ]


def _build_general_kp_cautions(
    planetary_positions: list[PlanetaryPosition],
    house_cusps: list[HouseCusp],
    dasha_summary: DashaPeriod,
) -> list[str]:
    current_assessment = _assess_period_ruler(dasha_summary.antara, planetary_positions, house_cusps)
    caution_lines = list(current_assessment["caution_indicators"][:2])
    caution_lines.append(
        "KP judgment should still check whether houses 6, 8, and 12 are overpowering the supportive houses before making final event promises."
    )
    return caution_lines


def _build_general_remedies(
    house_cusps: list[HouseCusp],
    dasha_summary: DashaPeriod,
    planetary_positions: list[PlanetaryPosition],
) -> list[str]:
    remedies: list[str] = []
    for lord in [dasha_summary.maha_dasha, dasha_summary.bhukti, dasha_summary.antara]:
        remedies.extend(_build_ruler_remedies(lord, _unique_house_list(_collect_house_links_for_lord(lord, planetary_positions, house_cusps))))

    deduped: list[str] = []
    seen: set[str] = set()
    for remedy in remedies:
        if remedy not in seen:
            seen.add(remedy)
            deduped.append(remedy)
    return deduped[:6]


def _build_ruler_remedies(lord: str, caution_houses: list[int]) -> list[str]:
    base_map = {
        "Sun": "Strengthen discipline, respect for mentors, and regular sunrise prayer or gratitude practice on Sundays.",
        "Moon": "Stabilize routine, sleep, hydration, and emotional calm; Monday prayer or reflective practice can help.",
        "Mars": "Channel heat into exercise, restraint, and disciplined action; avoid impulsive conflicts.",
        "Mercury": "Use study, journaling, prayer, mantra, and clear speech discipline to stabilize Mercury periods.",
        "Jupiter": "Seek guidance from teachers, charity, spiritual study, and Thursday discipline to strengthen Jupiter.",
        "Venus": "Maintain harmony, cleanliness, beauty, gratitude, and balanced relationships during Venus periods.",
        "Saturn": "Use patience, service, humility, routine, and steady effort to handle Saturn-linked delays well.",
        "Rahu": "Keep boundaries, reduce excess, verify decisions carefully, and use grounding practices during Rahu periods.",
        "Ketu": "Use prayer, detachment, inner discipline, and focused spiritual practice to steady Ketu periods.",
    }
    remedies = [base_map.get(lord, "Maintain discipline, prayer, and careful judgment during this period.")]
    if any(house in {6, 8, 12} for house in caution_houses):
        remedies.append("Because dusthana houses are involved, avoid rushed decisions and keep regular spiritual or reflective discipline.")
    return remedies


def _describe_topic_signature(topic_name: str, linked_planets: list[PlanetaryPosition], dominant_cusp: HouseCusp) -> str:
    domain_scores: dict[str, int] = {}
    source_planets = [planet.planet for planet in linked_planets[:3]]
    source_planets.extend([dominant_cusp.sign_lord, dominant_cusp.star_lord, dominant_cusp.sub_lord])

    for planet_name in source_planets:
        for domain in _planet_topic_domains(topic_name, planet_name):
            domain_scores[domain] = domain_scores.get(domain, 0) + 1

    if not domain_scores:
        return _default_topic_signature(topic_name)

    ranked_domains = sorted(domain_scores.items(), key=lambda item: (-item[1], item[0]))
    top_domains = [domain for domain, _ in ranked_domains[:3]]
    if len(top_domains) == 1:
        return top_domains[0]
    if len(top_domains) == 2:
        return f"{top_domains[0]} and {top_domains[1]}"
    return f"{top_domains[0]}, {top_domains[1]}, and {top_domains[2]}"


def _planet_topic_domains(topic_name: str, planet_name: str) -> list[str]:
    if topic_name in {"Career", "Education"}:
        return _planet_career_domains(planet_name)

    topic_mapping = {
        "Health Caution": {
            "Sun": ["vitality awareness and disciplined routine"],
            "Moon": ["care, nourishment, and emotional steadiness"],
            "Mars": ["heat, inflammation caution, and physical responsiveness"],
            "Mercury": ["nervous-system sensitivity, observation, and practical follow-up"],
            "Jupiter": ["recovery support and guidance-led care"],
            "Venus": ["comfort balance, hormonal harmony, and restorative support"],
            "Saturn": ["chronic-pattern caution, discipline, and structured management"],
            "Rahu": ["allergy-like sensitivity, irregular triggers, and careful monitoring"],
            "Ketu": ["subtle sensitivity, specialist review, and hidden-pattern observation"],
        },
        "Finance": {
            "Sun": ["status-linked earnings and visible responsibility"],
            "Moon": ["family support, flow of resources, and responsive earning pattern"],
            "Mars": ["effort-based income and action-led earning"],
            "Mercury": ["trade, analytics, communication, and flexible money skill"],
            "Jupiter": ["wealth building, guidance, and long-term financial growth"],
            "Venus": ["comfort, luxury, design, and value attraction"],
            "Saturn": ["disciplined saving, structure, and slow accumulation"],
            "Rahu": ["modern markets, unconventional income, and foreign-linked gains"],
            "Ketu": ["selective spending, detachment, and specialist skill income"],
        },
        "Foreign Settlement": {
            "Sun": ["status-linked relocation and purposeful travel"],
            "Moon": ["emotional adaptability and movement with support systems"],
            "Mars": ["migration through effort, initiative, and relocation drive"],
            "Mercury": ["study travel, communication-led movement, and flexible relocation"],
            "Jupiter": ["higher-study travel, guidance, and long-distance opportunity"],
            "Venus": ["comfortable relocation and lifestyle-driven settlement"],
            "Saturn": ["delayed but steady settlement through persistence"],
            "Rahu": ["foreign-linked movement, nontraditional settlement, and cross-border pull"],
            "Ketu": ["detachment from birthplace and specialist travel patterns"],
        },
        "Marriage": {
            "Sun": ["visible commitment and dignity in relationships"],
            "Moon": ["emotional bonding and caring partnership style"],
            "Mars": ["passion, directness, and adjustment lessons in bonding"],
            "Mercury": ["communication-based matching and practical understanding"],
            "Jupiter": ["guidance, dharmic support, and formal alliance"],
            "Venus": ["affection, attraction, harmony, and companionship"],
            "Saturn": ["delayed but serious commitment and long-term responsibility"],
            "Rahu": ["unconventional attraction and karmic intensity in relationships"],
            "Ketu": ["distance, detachment, or inwardness in bonding patterns"],
        },
        "Property": {
            "Sun": ["status-linked property and visible asset building"],
            "Moon": ["home comfort, domestic grounding, and family residence"],
            "Mars": ["land, construction, and physical asset action"],
            "Mercury": ["documentation, transactions, and flexible property decisions"],
            "Jupiter": ["family expansion, blessing, and stable settlement"],
            "Venus": ["beautiful home, comfort, and lifestyle property"],
            "Saturn": ["slow accumulation, durable assets, and structured settlement"],
            "Rahu": ["modern assets, unusual locations, and nontraditional settlement"],
            "Ketu": ["detached or minimalist property pattern"],
        },
        "Children": {
            "Sun": ["guidance, pride, and visible legacy through children"],
            "Moon": ["nurturing, emotional bonding, and caregiving"],
            "Mars": ["active children, effort, and protective instinct"],
            "Mercury": ["learning, communication, and developmental pattern"],
            "Jupiter": ["fertility blessing, growth, and mentoring support"],
            "Venus": ["affection, bonding, and joy through family growth"],
            "Saturn": ["delay, patience, and responsibility in family expansion"],
            "Rahu": ["unusual timing or unconventional family pattern"],
            "Ketu": ["detachment, karmic lessons, or subtle family themes"],
        },
        "Business": {
            "Sun": ["leadership, ownership, and visible authority"],
            "Moon": ["public dealing, customer response, and adaptive trade"],
            "Mars": ["enterprise drive, execution, and commercial risk-taking"],
            "Mercury": ["trade, negotiation, analytics, and commercial intelligence"],
            "Jupiter": ["advisory business, trust, and long-view expansion"],
            "Venus": ["brand value, design, presentation, and customer appeal"],
            "Saturn": ["systems, discipline, and long-cycle business building"],
            "Rahu": ["modern platforms, scaling, and unconventional enterprise"],
            "Ketu": ["specialist niche, back-end focus, and selective enterprise"],
        },
        "Legal Caution": {
            "Sun": ["authority, compliance, and formal process"],
            "Moon": ["emotional response to dispute and need for stability"],
            "Mars": ["conflict drive, argument, and procedural pressure"],
            "Mercury": ["documents, negotiation, and legal communication"],
            "Jupiter": ["fair guidance, counsel, and protective support"],
            "Venus": ["settlement, compromise, and relationship-based resolution"],
            "Saturn": ["delay, structure, and formal burden"],
            "Rahu": ["complexity, unusual entanglement, and procedural uncertainty"],
            "Ketu": ["detached outcome, technicality, and hidden complication"],
        },
    }
    topic_domains = topic_mapping.get(topic_name, {})
    return topic_domains.get(planet_name, [_default_topic_signature(topic_name)])


def _planet_career_domains(planet_name: str) -> list[str]:
    mapping = {
        "Sun": ["leadership, administration, and public-responsibility work"],
        "Moon": ["care, education, and people-facing support work"],
        "Mars": ["engineering, technical execution, and action-oriented work"],
        "Mercury": ["analysis, communication, commerce, and technology-oriented work"],
        "Jupiter": ["teaching, advisory, knowledge, and guidance-based work"],
        "Venus": ["creative, design, presentation, and comfort-industry work"],
        "Saturn": ["systems, discipline, engineering structure, and long-cycle responsibility"],
        "Rahu": ["digital, unconventional, foreign-linked, and modern technical fields"],
        "Ketu": ["research, diagnostics, specialist, and deep-focus work"],
    }
    return mapping.get(planet_name, ["general professional development and skill-building roles"])


def _default_topic_signature(topic_name: str) -> str:
    defaults = {
        "Career": "general professional development and skill-building roles",
        "Education": "general academic growth and aptitude formation",
        "Health Caution": "general resilience, monitoring, and supportive care pattern",
        "Finance": "general resource building and financial maturity",
        "Foreign Settlement": "general relocation potential and adaptability",
        "Marriage": "general relationship maturity and commitment pattern",
        "Property": "general settlement tendency and domestic stability",
        "Children": "general family growth and nurturing pattern",
        "Business": "general enterprise tendency and commercial growth",
        "Legal Caution": "general compliance, negotiation, and conflict-handling pattern",
    }
    return defaults.get(topic_name, "general life-pattern development")


def _build_minor_topic_yearly_outlook(topic_name: str, current_age: int) -> list[str]:
    current_year = date.today().year
    outlook: list[str] = []

    for offset, age in enumerate(range(current_age, min(19, current_age + 7))):
        start_year = current_year + offset
        end_year = start_year + 1
        note = _minor_outlook_note(topic_name, age)
        outlook.append(f"Age {age} ({start_year}-{end_year}): {note}")

    return outlook


def _minor_outlook_note(topic_name: str, age: int) -> str:
    if topic_name == "Education":
        if age <= 11:
            return "This year should be read for learning comfort, foundational confidence, and noticing what subjects naturally attract the child."
        if age <= 13:
            return "This year should be read for skill formation, communication style, memory habits, and early subject preference."
        if age <= 15:
            return "This year should be read for aptitude sorting, study discipline, and clearer stream direction."
        if age <= 17:
            return "This year should be read for stream choice, exam orientation, mentoring, and stronger academic direction."
        return "This year begins to matter for specialization and the academic path that can influence profession later."

    if topic_name == "Health Caution":
        if age <= 11:
            return "This year should be read for monitoring, parental care, routine, recovery support, and noticing recurring sensitivities early."
        if age <= 13:
            return "This year should be read for building healthy habits, regular follow-up, and preventing small recurring issues from becoming patterns."
        if age <= 15:
            return "This year should be read for stronger self-awareness, practical management, and consistent care discipline."
        return "This year should be read for maturing resilience, responsibility, and better self-management of health sensitivities."

    if topic_name in {"Marriage", "Business", "Finance", "Legal Caution"}:
        if age <= 11:
            return "This year should be read for temperament, values, confidence, and the basic personality traits that later influence adult life outcomes."
        if age <= 13:
            return "This year should be read for communication style, responsibility habits, and the way the child responds to structure and guidance."
        if age <= 15:
            return "This year should be read for maturity, judgment, discipline, and early independent decision patterns."
        if age <= 17:
            return "This year should be read for responsibility, social maturity, and the habits that will shape later adult outcomes."
        return "This year begins to matter more directly for later adult pattern formation."

    if age <= 11:
        return "This year should be read for learning foundation, curiosity, confidence, and early interests rather than profession selection."
    if age <= 13:
        return "This year should be read for skill formation, communication patterns, and the subjects or activities that begin to stand out."
    if age <= 15:
        return "This year should be read for stronger aptitude sorting, discipline, and clues about preferred academic or creative direction."
    if age <= 17:
        return "This year should be read for stream choice, exam direction, coaching, and more visible hints about future profession type."
    return "This year begins to matter more seriously for course specialization, preparation, and eventual profession-entry direction."


def _rank_significators(
    planetary_positions: list[PlanetaryPosition], house_cusps: list[HouseCusp], relevant_houses: list[int]
) -> list[ScoredSignificator]:
    sign_lord_lookup = {planet.planet: _houses_with_lord(house_cusps, planet.planet, "sign") for planet in planetary_positions}
    star_lord_lookup = {planet.planet: _houses_with_lord(house_cusps, planet.planet, "star") for planet in planetary_positions}
    sub_lord_lookup = {planet.planet: _houses_with_lord(house_cusps, planet.planet, "sub") for planet in planetary_positions}
    scored: list[ScoredSignificator] = []

    for planet in planetary_positions:
        score = 0
        reasons: list[str] = []

        if _extract_house_from_note(planet.note) in relevant_houses:
            score += 5
            reasons.append("occupies a target house")
        if planet.planet in {house_cusps[house - 1].sign_lord for house in relevant_houses}:
            score += 4
            reasons.append("owns a target cusp")
        if any(house in relevant_houses for house in star_lord_lookup.get(planet.planet, [])):
            score += 3
            reasons.append("connects through target star-lord houses")
        if any(house in relevant_houses for house in sub_lord_lookup.get(planet.planet, [])):
            score += 2
            reasons.append("connects through target sub-lord houses")
        if any(house in relevant_houses for house in sign_lord_lookup.get(planet.planet, [])):
            score += 2
            reasons.append("connects through target sign-lord houses")

        scored.append(ScoredSignificator(planet=planet, score=score, reasons=reasons or ["general chart relevance"]))

    return sorted(scored, key=lambda item: (-item.score, item.planet.planet))


def _houses_with_lord(house_cusps: list[HouseCusp], lord: str, layer: str) -> list[int]:
    results: list[int] = []
    for cusp in house_cusps:
        value = cusp.sign_lord if layer == "sign" else cusp.star_lord if layer == "star" else cusp.sub_lord
        if value == lord:
            results.append(cusp.house)
    return results


def _extract_house_from_note(note: str) -> int | None:
    marker = "house "
    lowered = note.lower()
    if marker not in lowered:
        return None
    suffix = lowered.split(marker, 1)[1]
    digits = "".join(character for character in suffix if character.isdigit())
    return int(digits) if digits else None


def build_house_connection_summary(planet: PlanetaryPosition, house_cusps: list[HouseCusp]) -> str:
    occupied = _extract_house_from_note(planet.note)
    sign_houses = _houses_with_lord(house_cusps, SIGN_LORDS[planet.sign], "sign")
    star_houses = _houses_with_lord(house_cusps, planet.star_lord, "star")
    sub_houses = _houses_with_lord(house_cusps, planet.sub_lord, "sub")
    parts = []
    if occupied is not None:
        parts.append(f"occupation of house {occupied}")
    if sign_houses:
        parts.append(f"sign-lord houses {', '.join(str(house) for house in sign_houses[:2])}")
    if star_houses:
        parts.append(f"star-lord houses {', '.join(str(house) for house in star_houses[:2])}")
    if sub_houses:
        parts.append(f"sub-lord houses {', '.join(str(house) for house in sub_houses[:2])}")
    return ", ".join(parts) if parts else "general planetary involvement"


def _find_computed_planet(planets: list[ComputedPlanet], planet_name: str) -> ComputedPlanet:
    for planet in planets:
        if planet.name == planet_name:
            return planet
    return planets[0]


def _find_planet_model(planets: list[PlanetaryPosition], planet_name: str) -> PlanetaryPosition:
    for planet in planets:
        if planet.planet == planet_name:
            return planet
    return planets[0]


def _current_week_window() -> dict[str, str]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return {
        "today": today.isoformat(),
        "start": week_start.isoformat(),
        "end": week_end.isoformat(),
    }


def _format_degree(value: float) -> str:
    degrees = int(value)
    minutes = int(round((value - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0
    return f"{degrees:02d}deg {minutes:02d}min"
