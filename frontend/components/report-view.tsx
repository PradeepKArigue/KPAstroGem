"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getChartSession } from "@/lib/api";
import type { ChartSessionResponse } from "@/types/kp";

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
    return <div className="glass-panel border border-roseclay/20 p-8 text-sm text-roseclay">{errorMessage ?? "The report is unavailable."}</div>;
  }

  const { chartData, questionHistory } = session;

  return (
    <div className="space-y-6">
      <section className="glass-panel bg-orbital-grid p-8 sm:p-10">
        <p className="section-title">Interactive Jathakam Report</p>
        <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
          {chartData.birthSummary.name}&apos;s KP-style report
        </h1>
        <p className="mt-5 max-w-4xl text-base leading-7 text-midnight/75">
          Inspired by public KP product patterns such as chart-first analysis, sub-lord tables, dasha navigation,
          and print-ready reporting, this MVP now presents a complete browser-downloadable report for the current session.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
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
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card title="Birth Summary">
          <ReportGrid
            items={[
              ["Date of birth", chartData.birthSummary.dateOfBirth],
              ["Time of birth", chartData.birthSummary.timeOfBirth],
              ["Birth place", chartData.birthSummary.birthPlace],
              ["State", chartData.birthSummary.state || "Not provided"],
              ["Country", chartData.birthSummary.country],
              ["Timezone", chartData.birthSummary.timezone],
              ["Latitude", String(chartData.birthSummary.latitude ?? "Pending")],
              ["Longitude", String(chartData.birthSummary.longitude ?? "Pending")],
            ]}
          />
        </Card>

        <Card title="Dasha Navigator">
          <ReportGrid
            items={[
              ["Maha Dasha", chartData.dashaSummary.mahaDasha],
              ["Bhukti", chartData.dashaSummary.bhukti],
              ["Antara", chartData.dashaSummary.antara],
              ["Window", chartData.dashaSummary.window],
              ["Status", chartData.dashaSummary.status],
            ]}
          />
          <p className="mt-4 text-sm leading-7 text-midnight/70">{chartData.dashaSummary.note}</p>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card title="Planet Table">
          <div className="space-y-3">
            {chartData.planetaryPositions.map((position) => (
              <div key={position.planet} className="rounded-2xl bg-slate-50 p-4">
                <p className="font-semibold text-midnight">{position.planet}</p>
                <p className="mt-2 text-sm text-midnight/70">
                  {position.sign} at {position.degree} | {position.nakshatra} Pada {position.pada}
                </p>
                <p className="mt-2 text-sm text-midnight/70">
                  Star lord: {position.starLord} | Sub lord: {position.subLord} | Status: {position.status}
                </p>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Cusp Table">
          <div className="space-y-3">
            {chartData.houseCusps.map((cusp) => (
              <div key={cusp.house} className="rounded-2xl bg-slate-50 p-4">
                <p className="font-semibold text-midnight">House {cusp.house}</p>
                <p className="mt-2 text-sm text-midnight/70">
                  {cusp.sign} at {cusp.cuspDegree}
                </p>
                <p className="mt-2 text-sm text-midnight/70">
                  Sign lord: {cusp.signLord} | Star lord: {cusp.starLord} | Sub lord: {cusp.subLord}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <Card title="Interpretive Summary">
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
      </Card>

      <Card title="Interactive Q&A History">
        {questionHistory.length > 0 ? (
          <div className="space-y-4">
            {questionHistory.map((item, index) => (
              <div key={`${item.question}-${index}`} className="rounded-2xl bg-slate-50 p-5">
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
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-midnight/70">
            No questions have been asked yet for this chart session.
          </div>
        )}
      </Card>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="glass-panel p-6 sm:p-8">
      <p className="section-title">{title}</p>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function ReportGrid({ items }: { items: [string, string][] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {items.map(([label, value]) => (
        <div key={label} className="rounded-2xl bg-slate-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/75">{label}</p>
          <p className="mt-2 text-sm text-midnight/75">{value}</p>
        </div>
      ))}
    </div>
  );
}
