"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getChartSession } from "@/lib/api";
import type {
  BirthSummary,
  ChartQuestionResponse,
  ChartSessionResponse,
  DashaSummary,
  HouseCusp,
  PlanetaryPosition,
} from "@/types/kp";

const houseLabels = Array.from({ length: 12 }, (_, index) => `H${index + 1}`);
const dashaPlanetOrder = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"];

type RelationshipStrength = "L1" | "L2" | "L3" | "L4" | "-";

type PlanetDerivedDetails = {
  occupiedHouse: number | null;
  starLordHouse: number | null;
  subLordHouse: number | null;
  signLordHouse: number | null;
  activationByHouse: RelationshipStrength[];
};

type DashaPeriodRow = {
  level: string;
  ruler: string;
  window: string;
  focus: string;
};

export function ReportView({ chartId }: { chartId: string }) {
  const [session, setSession] = useState<ChartSessionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadReport() {
      try {
        const payload = await getChartSession(chartId);
        if (!cancelled) {
          setSession(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(error instanceof Error ? error.message : "The report could not be loaded.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadReport();

    return () => {
      cancelled = true;
    };
  }, [chartId]);

  if (isLoading) {
    return <div className="glass-panel p-8 text-sm text-midnight/70">Preparing print-friendly KP report...</div>;
  }

  if (errorMessage || !session) {
    return (
      <div className="glass-panel border border-roseclay/20 p-8 text-sm text-roseclay">
        {errorMessage ?? "The report is unavailable."}
      </div>
    );
  }

  const { chartData, questionHistory } = session;
  const derivedPlanetDetails = buildPlanetDerivedDetails(chartData.planetaryPositions, chartData.houseCusps);
  const chartOrientationRows = buildChartOrientationRows(chartData.birthSummary, chartData.houseCusps);
  const rasiRows = buildRasiAndJathakamRows(chartData.birthSummary, chartData.planetaryPositions, chartData.houseCusps);
  const dashaRows = buildDashaRows(chartData.dashaSummary.window, chartData.dashaSummary.mahaDasha);
  const dashaNarrative = buildCurrentDashaNarrative(
    chartData.birthSummary,
    chartData.planetaryPositions,
    chartData.houseCusps,
    chartData.dashaSummary,
  );

  return (
    <div className="space-y-6 print:space-y-4">
      <section className="glass-panel bg-orbital-grid p-8 sm:p-10 print:break-after-page print:rounded-none print:border-none print:shadow-none">
        <p className="section-title">Interactive Jathakam Report</p>
        <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
          {chartData.birthSummary.name}&apos;s KP-style report
        </h1>
        <p className="mt-5 max-w-4xl text-base leading-7 text-midnight/75">
          This report now includes chart identity, Rasi and Jathakam details, planet and cusp tables,
          derived significator logic, and a date-based dasha reading layer. Astronomical chart values are
          computed, while the automated interpretive layer is still being refined.
        </p>
        <div className="mt-6 flex flex-wrap gap-3 print:hidden">
          <button
            type="button"
            onClick={() => window.print()}
            className="rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora"
          >
            Download / Print Report
          </button>
          <Link
            href={`/dashboard/${chartId}`}
            className="rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora"
          >
            Back to Dashboard
          </Link>
        </div>
        <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <IdentityBadge label="Name" value={chartData.birthSummary.name} />
          <IdentityBadge label="Date of birth" value={chartData.birthSummary.dateOfBirth} />
          <IdentityBadge label="Time of birth" value={chartData.birthSummary.timeOfBirth} />
          <IdentityBadge
            label="Birth location"
            value={`${chartData.birthSummary.birthPlace}, ${chartData.birthSummary.state || ""} ${chartData.birthSummary.country}`.replace(
              /\s+/g,
              " ",
            ).replace(" ,", ",")}
          />
        </div>
        <div className="mt-5 rounded-2xl border border-saffron/40 bg-saffron/10 px-4 py-3 text-sm leading-7 text-midnight/75">
          Verify this identity summary before using the report. If these details do not match the intended person,
          create a new chart session from the birth-details flow instead of trusting this chart URL.
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr] print:grid-cols-1">
        <TableCard title="Birth and Chart Metadata">
          <DenseTable
            headers={["Field", "Value", "Field", "Value"]}
            rows={[
              ["Birth place", chartData.birthSummary.birthPlace, "State", chartData.birthSummary.state || "Not provided"],
              ["Country", chartData.birthSummary.country, "Timezone", chartData.birthSummary.timezone],
              ["Latitude", String(chartData.birthSummary.latitude ?? "Pending"), "Longitude", String(chartData.birthSummary.longitude ?? "Pending")],
              ["Question category", chartData.birthSummary.questionCategory, "Seed question", chartData.birthSummary.question],
            ]}
          />
          <p className="mt-4 text-sm leading-7 text-midnight/70">{chartData.birthSummary.birthTimeAccuracyNote}</p>
        </TableCard>

        <TableCard title="KP Orientation Snapshot">
          <DenseTable headers={["Metric", "Value"]} rows={chartOrientationRows} />
          <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
            {chartData.dashaSummary.note}
          </div>
        </TableCard>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr] print:grid-cols-1">
        <TableCard title="Rasi and Jathakam Details">
          <DenseTable headers={["Field", "Value"]} rows={rasiRows} />
        </TableCard>

        <TableCard title="Current Dasha and Week Reading">
          <div className="space-y-3">
            {dashaNarrative.map((item) => (
              <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                {item}
              </div>
            ))}
          </div>
        </TableCard>
      </section>

      <TableCard title="How To Read This KP Report">
        <div className="grid gap-3 lg:grid-cols-2">
          <ReadingStep
            title="Birth normalization first"
            detail="The app confirms birthplace, coordinates, timezone, and normalized UTC time before any chart session is created."
          />
          <ReadingStep
            title="Rasi and Jathakam context"
            detail="Read lagna, janma rasi, and janma nakshatra first. They give the chart's identity before topic-specific interpretation starts."
          />
          <ReadingStep
            title="Cusps drive the reading"
            detail="KP relies heavily on house cusps and their star-lord and sub-lord relationships, so the cusp table should be read before jumping to conclusions."
          />
          <ReadingStep
            title="Planets are read through multiple links"
            detail="A planet is not judged only by sign. It is also read through occupied house, sign-lord house, star-lord house, and sub-lord house."
          />
          <ReadingStep
            title="Activation matrix explains emphasis"
            detail="The house-activation grid is a compact way to see which houses a planet connects to more strongly in the current computed reading."
          />
          <ReadingStep
            title="Dasha windows explain timing"
            detail="The dasha reading now includes current-date and current-week framing. In a full KP engine, this should separate event promise from event timing."
          />
        </div>
      </TableCard>

      <TableCard title="Planetary Position Table">
        <DenseTable
          headers={["Planet", "Sign", "Degree", "Nakshatra", "Pada", "Star Lord", "Sub Lord", "Status"]}
          rows={chartData.planetaryPositions.map((planet) => [
            planet.planet,
            planet.sign,
            planet.degree,
            planet.nakshatra,
            String(planet.pada),
            planet.starLord,
            planet.subLord,
            planet.status,
          ])}
        />
      </TableCard>

      <TableCard title="House Cusp Table">
        <DenseTable
          headers={["House", "Sign", "Cusp Degree", "Sign Lord", "Star Lord", "Sub Lord"]}
          rows={chartData.houseCusps.map((cusp) => [
            `House ${cusp.house}`,
            cusp.sign,
            cusp.cuspDegree,
            cusp.signLord,
            cusp.starLord,
            cusp.subLord,
          ])}
        />
      </TableCard>

      <TableCard title="Derived KP Significator Matrix">
        <DenseTable
          headers={["Planet", "Occupied", "Sign Lord", "Star Lord", "Sub Lord", "KP Reading"]}
          rows={chartData.planetaryPositions.map((planet) => {
            const derived = derivedPlanetDetails[planet.planet];
            return [
              planet.planet,
              formatHouseRef(derived.occupiedHouse),
              formatHouseRef(derived.signLordHouse),
              formatHouseRef(derived.starLordHouse),
              formatHouseRef(derived.subLordHouse),
              buildShortKPReading(planet, derived),
            ];
          })}
        />
      </TableCard>

      <TableCard title="House Activation by Planet">
        <DenseTable
          headers={["Planet", ...houseLabels]}
          rows={chartData.planetaryPositions.map((planet) => [
            planet.planet,
            ...derivedPlanetDetails[planet.planet].activationByHouse,
          ])}
        />
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <LegendItem code="L4" text="Strongest computed connection from occupied or sign-lord linkage." />
          <LegendItem code="L3" text="Strong computed support from star-lord mapping." />
          <LegendItem code="L2" text="Secondary support from sub-lord mapping." />
          <LegendItem code="L1" text="Light influence via neighboring house relationship." />
        </div>
      </TableCard>

      <section className="grid gap-6 xl:grid-cols-2 print:grid-cols-1">
        <TableCard title="Vimshottari Dasha Ladder">
          <DenseTable
            headers={["Level", "Ruler", "Window", "Focus"]}
            rows={dashaRows.map((row) => [row.level, row.ruler, row.window, row.focus])}
          />
        </TableCard>

        <TableCard title="Question Session Ledger">
          {questionHistory.length > 0 ? (
            <DenseTable
              headers={["Question", "Topic", "Timing", "Confidence"]}
              rows={questionHistory.map((item) => [
                item.question,
                item.classifiedTopic,
                item.possibleTimingWindow,
                `${item.confidenceLevel.level} - ${item.confidenceLevel.reason}`,
              ])}
            />
          ) : (
            <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-midnight/70">
              No questions have been asked yet for this chart session.
            </div>
          )}
        </TableCard>
      </section>

      <TableCard title="Interpretive Summary and Disclaimer">
        <ul className="space-y-3">
          {chartData.interpretation.map((item) => (
            <li key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
              {item}
            </li>
          ))}
        </ul>
        <div className="mt-5 rounded-2xl bg-aurora/10 px-4 py-3 text-sm text-midnight/75">
          Confidence: <span className="font-semibold">{chartData.confidenceLevel.level}</span> | {chartData.confidenceLevel.reason}
        </div>
        <div className="mt-5 rounded-2xl border border-saffron/40 bg-saffron/10 px-4 py-3 text-sm leading-7 text-midnight/75">
          {chartData.disclaimer}
        </div>
      </TableCard>

      {questionHistory.length > 0 ? (
        <TableCard title="Detailed Question and Answer History">
          <div className="space-y-4">
            {questionHistory.map((item, index) => (
              <QuestionHistoryCard key={`${item.question}-${index}`} item={item} />
            ))}
          </div>
        </TableCard>
      ) : null}
    </div>
  );
}

function buildChartOrientationRows(birthSummary: BirthSummary, houseCusps: HouseCusp[]) {
  const firstHouse = houseCusps.find((cusp) => cusp.house === 1);
  const moonHouse = houseCusps.find((cusp) => cusp.house === 8) ?? houseCusps[0];
  const tenthHouse = houseCusps.find((cusp) => cusp.house === 10);

  return [
    ["Ayanamsa mode", "KP New"],
    ["Ascendant cue", firstHouse ? `${firstHouse.sign} ${firstHouse.cuspDegree}` : "Pending"],
    ["Moon-sign cue", moonHouse ? `${moonHouse.sign} ${moonHouse.cuspDegree}` : "Pending"],
    ["Career cusp cue", tenthHouse ? `${tenthHouse.sign} ${tenthHouse.cuspDegree}` : "Pending"],
    ["Location confidence", `${birthSummary.birthPlace}, ${birthSummary.country}`],
  ];
}

function buildRasiAndJathakamRows(
  birthSummary: BirthSummary,
  planets: PlanetaryPosition[],
  cusps: HouseCusp[],
): string[][] {
  const moon = findPlanet(planets, "Moon");
  const sun = findPlanet(planets, "Sun");
  const lagna = cusps.find((cusp) => cusp.house === 1) ?? cusps[0];
  const careerCusp = cusps.find((cusp) => cusp.house === 10) ?? cusps[9] ?? cusps[0];

  return [
    ["Ayanamsa", "KP New"],
    ["Lagna / Ascendant", `${lagna.sign} ${lagna.cuspDegree}`],
    ["Lagna lord", lagna.signLord],
    ["Janma rasi", moon.sign],
    ["Janma nakshatra", `${moon.nakshatra} Pada ${moon.pada}`],
    ["Moon star / sub lord", `${moon.starLord} / ${moon.subLord}`],
    ["Sun sign cue", `${sun.sign} ${sun.degree}`],
    ["Career cusp", `${careerCusp.sign} ${careerCusp.cuspDegree}`],
    ["Birth timezone", birthSummary.timezone],
    ["Coordinates", `${birthSummary.latitude ?? "Pending"}, ${birthSummary.longitude ?? "Pending"}`],
  ];
}

function buildCurrentDashaNarrative(
  birthSummary: BirthSummary,
  planets: PlanetaryPosition[],
  cusps: HouseCusp[],
  dashaSummary: DashaSummary,
) {
  const today = new Date();
  const week = getWeekWindow(today);
  const antaraPlanet = findPlanet(planets, dashaSummary.antara);
  const bhuktiPlanet = findPlanet(planets, dashaSummary.bhukti);
  const moon = findPlanet(planets, "Moon");
  const lagna = cusps.find((cusp) => cusp.house === 1) ?? cusps[0];

  return [
    `As of ${formatLongDate(today)}, the active dasha chain for this session is ${dashaSummary.mahaDasha} / ${dashaSummary.bhukti} / ${dashaSummary.antara}.`,
    `For the week of ${formatShortDate(week.start)} to ${formatShortDate(week.end)}, the antara signal is being read through ${antaraPlanet.sign}, ${antaraPlanet.nakshatra}, and sub lord ${antaraPlanet.subLord}.`,
    `The bhukti layer is currently being framed through ${bhuktiPlanet.sign}, star lord ${bhuktiPlanet.starLord}, and the chart's lagna ${lagna.sign}.`,
    `This jathakam currently combines janma rasi ${moon.sign}, janma nakshatra ${moon.nakshatra}, and active window ${dashaSummary.window} as the main timing story for date-based interpretation.`,
  ];
}

function buildPlanetDerivedDetails(planets: PlanetaryPosition[], cusps: HouseCusp[]): Record<string, PlanetDerivedDetails> {
  const houseBySign = new Map<string, number>();
  const houseByPlanet = new Map<string, number>();
  const details: Record<string, PlanetDerivedDetails> = {};

  for (const cusp of cusps) {
    if (!houseBySign.has(cusp.sign)) {
      houseBySign.set(cusp.sign, cusp.house);
    }
  }

  for (const planet of planets) {
    const occupiedHouse = houseBySign.get(planet.sign) ?? null;
    if (occupiedHouse != null) {
      houseByPlanet.set(planet.planet, occupiedHouse);
    }
  }

  for (const planet of planets) {
    const occupiedHouse = houseByPlanet.get(planet.planet) ?? null;
    const starLordHouse = houseByPlanet.get(planet.starLord) ?? null;
    const subLordHouse = houseByPlanet.get(planet.subLord) ?? null;
    const signLordHouse = findHouseByLord(cusps, planet.sign);
    const activationByHouse = Array.from({ length: 12 }, (_, index) => {
      const houseNumber = index + 1;
      return deriveRelationshipStrength(houseNumber, occupiedHouse, signLordHouse, starLordHouse, subLordHouse);
    });

    details[planet.planet] = {
      occupiedHouse,
      starLordHouse,
      subLordHouse,
      signLordHouse,
      activationByHouse,
    };
  }

  return details;
}

function findHouseByLord(cusps: HouseCusp[], sign: string): number | null {
  const match = cusps.find((cusp) => cusp.sign === sign);
  return match?.house ?? null;
}

function deriveRelationshipStrength(
  houseNumber: number,
  occupiedHouse: number | null,
  signLordHouse: number | null,
  starLordHouse: number | null,
  subLordHouse: number | null,
): RelationshipStrength {
  if (houseNumber === occupiedHouse || houseNumber === signLordHouse) {
    return "L4";
  }

  if (houseNumber === starLordHouse) {
    return "L3";
  }

  if (houseNumber === subLordHouse) {
    return "L2";
  }

  if (
    occupiedHouse != null &&
    (houseNumber === wrapHouse(occupiedHouse - 1) || houseNumber === wrapHouse(occupiedHouse + 1))
  ) {
    return "L1";
  }

  return "-";
}

function wrapHouse(house: number) {
  if (house < 1) {
    return house + 12;
  }

  if (house > 12) {
    return house - 12;
  }

  return house;
}

function buildShortKPReading(position: PlanetaryPosition, derived: PlanetDerivedDetails) {
  return [
    `${position.planet} links to ${formatHouseRef(derived.occupiedHouse)} by placement`,
    `${formatHouseRef(derived.starLordHouse)} through star lord ${position.starLord}`,
    `${formatHouseRef(derived.subLordHouse)} through sub lord ${position.subLord}`,
  ].join("; ");
}

function buildDashaRows(window: string, mahaDasha: string): DashaPeriodRow[] {
  const match = window.match(/(\d{4})-(\d{2})\s+to\s+(\d{4})-(\d{2})/i);
  if (!match) {
    return [{ level: "Current", ruler: mahaDasha, window, focus: "Computed timing window from the active chart session." }];
  }

  const [, startYear, startMonth, endYear, endMonth] = match;
  const start = new Date(Date.UTC(Number(startYear), Number(startMonth) - 1, 1));
  const end = new Date(Date.UTC(Number(endYear), Number(endMonth) - 1, 1));
  const totalMonths = Math.max(monthDiff(start, end), 1);
  const segmentCount = Math.min(4, totalMonths);
  const segmentMonths = Math.max(Math.ceil(totalMonths / segmentCount), 1);
  const startIndex = Math.max(dashaPlanetOrder.indexOf(mahaDasha), 0);
  const rows: DashaPeriodRow[] = [];

  rows.push({
    level: "Maha Dasha",
    ruler: mahaDasha,
    window,
    focus: `${mahaDasha} remains the report anchor for this active computed period.`,
  });

  for (let index = 0; index < segmentCount; index += 1) {
    const ruler = dashaPlanetOrder[(startIndex + index + 1) % dashaPlanetOrder.length];
    const segmentStart = addMonths(start, segmentMonths * index);
    const segmentEnd = index === segmentCount - 1 ? end : clampDate(addMonths(start, segmentMonths * (index + 1)), end);
    rows.push({
      level: `Bhukti ${index + 1}`,
      ruler,
      window: `${formatMonthYear(segmentStart)} to ${formatMonthYear(segmentEnd)}`,
      focus: `${ruler} is used as the narrative focus for this computed sub-period.`,
    });
  }

  return rows;
}

function addMonths(date: Date, months: number) {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + months, 1));
}

function clampDate(date: Date, maxDate: Date) {
  return date.getTime() > maxDate.getTime() ? maxDate : date;
}

function getWeekWindow(date: Date) {
  const start = new Date(date);
  const day = (start.getDay() + 6) % 7;
  start.setDate(start.getDate() - day);
  start.setHours(0, 0, 0, 0);

  const end = new Date(start);
  end.setDate(start.getDate() + 6);

  return { start, end };
}

function monthDiff(start: Date, end: Date) {
  return (end.getUTCFullYear() - start.getUTCFullYear()) * 12 + (end.getUTCMonth() - start.getUTCMonth());
}

function formatMonthYear(date: Date) {
  return date.toLocaleDateString("en-US", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

function formatLongDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function formatShortDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function findPlanet(planets: PlanetaryPosition[], planetName: string) {
  return planets.find((planet) => planet.planet === planetName) ?? planets[0];
}

function formatHouseRef(house: number | null) {
  return house == null ? "Pending" : `House ${house}`;
}

function TableCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="glass-panel p-6 sm:p-8 print:rounded-none print:border print:border-slate-200 print:shadow-none">
      <p className="section-title">{title}</p>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function DenseTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-separate border-spacing-0 overflow-hidden rounded-3xl border border-slate-200 bg-white text-left text-sm text-midnight/75">
        <thead>
          <tr className="bg-slate-50">
            {headers.map((header, index) => (
              <th
                key={`${header}-${index}`}
                className="border-b border-slate-200 px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-aurora/80"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={`${row[0]}-${index}`} className="align-top">
              {row.map((cell, cellIndex) => (
                <td
                  key={`${row[0]}-${cellIndex}-${index}`}
                  className="border-b border-slate-100 px-4 py-3 leading-6 last:border-b-0"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function IdentityBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/75">{label}</p>
      <p className="mt-2 text-sm text-midnight/75">{value}</p>
    </div>
  );
}

function LegendItem({ code, text }: { code: string; text: string }) {
  return (
    <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-midnight/70">
      <span className="font-semibold text-midnight">{code}</span> - {text}
    </div>
  );
}

function QuestionHistoryCard({ item }: { item: ChartQuestionResponse }) {
  return (
    <div className="rounded-3xl bg-slate-50 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/80">Question</p>
      <p className="mt-2 font-semibold text-midnight">{item.question}</p>
      <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-midnight/60">KP-style answer</p>
      <ul className="mt-3 space-y-2">
        {item.interpretation.map((line) => (
          <li key={line} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
            {line}
          </li>
        ))}
      </ul>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl bg-white px-4 py-3 text-sm text-midnight/70">
          <span className="font-semibold text-midnight">Relevant houses:</span> {item.relevantHouses.join(", ")}
        </div>
        <div className="rounded-2xl bg-white px-4 py-3 text-sm text-midnight/70">
          <span className="font-semibold text-midnight">Timing window:</span> {item.possibleTimingWindow}
        </div>
      </div>
    </div>
  );
}

function ReadingStep({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-2xl bg-slate-50 px-4 py-4">
      <p className="text-sm font-semibold text-midnight">{title}</p>
      <p className="mt-2 text-sm leading-7 text-midnight/70">{detail}</p>
    </div>
  );
}
