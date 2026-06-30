from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from itertools import cycle, islice
from zoneinfo import ZoneInfo

import swisseph as swe

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
    ayanamsa = swe.get_ayanamsa_ut(julian_day)
    ascendant = house_cusps[0]
    moon = _find_computed_planet(planets, "Moon")

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
    interpretation = [
            f"Lagna rises in {ascendant.sign} while the janma rasi is {moon.sign} in {moon.nakshatra} pada {moon.pada}.",
        (
            f"The active dasha chain as of {date.today().isoformat()} is "
            f"{dasha_summary.maha_dasha} / {dasha_summary.bhukti} / {dasha_summary.antara}."
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
        planetaryPositions=[_planet_to_model(planet) for planet in planets],
        houseCusps=house_cusps,
        starLord=star_lord,
        subLord=sub_lord,
        dashaSummary=dasha_summary,
        interpretation=interpretation,
        confidenceLevel=confidence,
        disclaimer=disclaimer,
    )


def build_question_answer(chart: ChartData, question: str, optional_date_range: str | None) -> ChartQuestionResponse:
    topic = _infer_topic(question, chart.birth_summary.question_category)
    lagna_cusp = chart.house_cusps[0]
    relevant_cusps = [chart.house_cusps[house - 1] for house in topic.house_focus]
    dominant_cusp = relevant_cusps[0]
    moon = _find_planet_model(chart.planetary_positions, "Moon")
    antara_planet = _find_planet_model(chart.planetary_positions, chart.dasha_summary.antara)
    linked_planets = _select_linked_planets(chart.planetary_positions, relevant_cusps)
    current_week = _current_week_window()

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
    ]
    significator_analysis = [
        (
            f"{planet.planet} becomes relevant through computed placement in {planet.sign}, "
            f"{planet.nakshatra}, and sub lord {planet.sub_lord}."
        )
        for planet in linked_planets[:2]
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
    supporting_factors = [
        (
            f"Relevant house lords cluster around {', '.join(sorted({cusp.star_lord for cusp in relevant_cusps}))} "
            "at the star-lord layer."
        ),
        (
            f"The ascendant ruling pair {chart.star_lord.ruler} / {chart.sub_lord.ruler} keeps the question tied "
            "to the computed birth profile rather than a generic template."
        ),
    ]
    blocking_factors = [
        "Automated event-promise ranking is still lighter than a full human KP consultation with rectification.",
        "Narrow timing beyond the active dasha chain should still be reviewed carefully against exact birth-time confidence.",
    ]

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
            f"The computed timing layer relies on the active dasha chain "
            f"{chart.dasha_summary.maha_dasha} / {chart.dasha_summary.bhukti} / {chart.dasha_summary.antara}."
        ),
        "The automated answer should be read as a structured KP-style briefing, not as a substitute for a fully audited consultation.",
    ]
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
        status="Computed",
        note=(
            f"Computed from Moon longitude in {NAKSHATRAS[int((moon_longitude % 360) // NAKSHATRA_SPAN)]}. "
            "The active window shown here is the current antara period."
        ),
    )


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
