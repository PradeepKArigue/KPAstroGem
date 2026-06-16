"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { getChartSession } from "@/lib/api";
import type { ChartSessionResponse } from "@/types/kp";

export function ChartDashboard({ chartId }: { chartId: string }) {
  const [session, setSession] = useState<ChartSessionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadChart() {
      try {
        const payload = await getChartSession(chartId);
        if (!cancelled) {
          setSession(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            error instanceof Error ? error.message : "The chart session could not be loaded from the backend.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadChart();

    return () => {
      cancelled = true;
    };
  }, [chartId]);

  if (isLoading) {
    return <LoadingPanel label="Loading temporary chart session..." />;
  }

  if (errorMessage || !session) {
    return <ErrorPanel message={errorMessage ?? "The chart session is unavailable."} />;
  }

  const { chartData, questionHistory, expiresAt } = session;

  return (
    <div className="space-y-6">
      <section className="glass-panel p-6 sm:p-8">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="section-title">Chart Dashboard</p>
            <h1 className="mt-3 font-[family-name:var(--font-heading)] text-4xl font-semibold text-midnight">
              {chartData.birthSummary.name}&apos;s temporary KP chart
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-midnight/70">
              {chartData.birthSummary.summaryLine}
            </p>
          </div>
          <div className="rounded-3xl bg-slate-50 px-5 py-4 text-sm text-midnight/70">
            <p className="font-semibold text-midnight">Chart ID</p>
            <p className="mt-2 break-all">{chartId}</p>
            <p className="mt-3">Expires: {new Date(expiresAt).toLocaleString()}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link href={`/ask/${chartId}`} className="rounded-full bg-midnight px-5 py-3 text-sm font-semibold text-white transition hover:bg-aurora">
            Ask a KP Question
          </Link>
          <Link href="/birth-details" className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora">
            Create Another Session
          </Link>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.92fr]">
        <div className="glass-panel p-6 sm:p-8">
          <p className="section-title">Birth Summary</p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <SummaryBadge label="Date of birth" value={chartData.birthSummary.dateOfBirth} />
            <SummaryBadge label="Time of birth" value={chartData.birthSummary.timeOfBirth} />
            <SummaryBadge label="Birth place" value={chartData.birthSummary.birthPlace} />
            <SummaryBadge label="State" value={chartData.birthSummary.state || "Not provided"} />
            <SummaryBadge label="Country" value={chartData.birthSummary.country} />
            <SummaryBadge label="Timezone" value={chartData.birthSummary.timezone} />
            <SummaryBadge label="Latitude" value={String(chartData.birthSummary.latitude ?? "Pending")} />
            <SummaryBadge label="Longitude" value={String(chartData.birthSummary.longitude ?? "Pending")} />
          </div>
          <p className="mt-5 rounded-2xl bg-saffron/10 px-4 py-3 text-sm leading-7 text-midnight/70">
            {chartData.birthSummary.birthTimeAccuracyNote}
          </p>
        </div>

        <div className="glass-panel p-6 sm:p-8">
          <p className="section-title">Current Dasha View</p>
          <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
            Placeholder timing panel
          </h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <SummaryBadge label="Maha dasha" value={chartData.dashaSummary.mahaDasha} />
            <SummaryBadge label="Bhukti" value={chartData.dashaSummary.bhukti} />
            <SummaryBadge label="Antara" value={chartData.dashaSummary.antara} />
          </div>
          <p className="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
            {chartData.dashaSummary.note}
          </p>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <DataPanel title="Planet Table">
          {chartData.planetaryPositions.map((position) => (
            <div key={position.planet} className="rounded-2xl bg-white p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-midnight">{position.planet}</p>
                  <p className="mt-1 text-sm text-midnight/70">
                    {position.sign} at {position.degree}
                  </p>
                </div>
                <span className="rounded-full bg-saffron/20 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-roseclay">
                  {position.status}
                </span>
              </div>
              <p className="mt-3 text-sm text-midnight/70">
                {position.nakshatra} Pada {position.pada}
              </p>
              <p className="mt-1 text-sm text-midnight/70">
                Star lord: {position.starLord} | Sub lord: {position.subLord}
              </p>
              <p className="mt-3 text-sm leading-6 text-midnight/60">{position.note}</p>
            </div>
          ))}
        </DataPanel>

        <DataPanel title="Cusp Table">
          {chartData.houseCusps.map((cusp) => (
            <div key={cusp.house} className="rounded-2xl bg-white p-4">
              <p className="font-semibold text-midnight">House {cusp.house}</p>
              <p className="mt-1 text-sm text-midnight/70">
                {cusp.sign} at {cusp.cuspDegree}
              </p>
              <p className="mt-2 text-sm text-midnight/70">
                Sign lord: {cusp.signLord} | Star lord: {cusp.starLord} | Sub lord: {cusp.subLord}
              </p>
              <p className="mt-3 text-sm leading-6 text-midnight/60">{cusp.note}</p>
            </div>
          ))}
        </DataPanel>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="glass-panel p-6 sm:p-8">
          <p className="section-title">Ruling Factors</p>
          <div className="mt-5 space-y-4">
            <RulingFactorCard title="Star lord" area={chartData.starLord.area} ruler={chartData.starLord.ruler} note={chartData.starLord.note} />
            <RulingFactorCard title="Sub lord" area={chartData.subLord.area} ruler={chartData.subLord.ruler} note={chartData.subLord.note} />
          </div>
        </div>

        <div className="glass-panel p-6 sm:p-8">
          <p className="section-title">Interpretation Layer</p>
          <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
            Structured placeholder KP output
          </h2>
          <ul className="mt-5 space-y-3">
            {chartData.interpretation.map((item) => (
              <li key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                {item}
              </li>
            ))}
          </ul>
          <div className="mt-5 rounded-2xl bg-aurora/10 px-4 py-3 text-sm text-midnight/75">
            Confidence: <span className="font-semibold">{chartData.confidenceLevel.level}</span> |{" "}
            {chartData.confidenceLevel.reason}
          </div>
          <div className="mt-5 rounded-2xl border border-saffron/40 bg-saffron/10 px-4 py-3 text-sm leading-7 text-midnight/75">
            {chartData.disclaimer}
          </div>
          {questionHistory.length > 0 ? (
            <div className="mt-6 rounded-3xl bg-slate-50 p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">Question history</p>
              <div className="mt-4 space-y-3">
                {questionHistory.map((item, index) => (
                  <div key={`${item.question}-${index}`} className="rounded-2xl bg-white p-4">
                    <p className="font-semibold text-midnight">{item.question}</p>
                    <p className="mt-2 text-sm text-midnight/70">Topic: {item.classifiedTopic}</p>
                    <p className="mt-2 text-sm leading-6 text-midnight/60">{item.interpretation[0]}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function SummaryBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/75">{label}</p>
      <p className="mt-2 text-sm text-midnight/75">{value}</p>
    </div>
  );
}

function RulingFactorCard({
  title,
  area,
  ruler,
  note,
}: {
  title: string;
  area: string;
  ruler: string;
  note: string;
}) {
  return (
    <div className="rounded-[2rem] bg-slate-50 p-5">
      <h3 className="text-lg font-semibold text-midnight">{title}</h3>
      <p className="mt-4 text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">{area}</p>
      <p className="mt-2 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">{ruler}</p>
      <p className="mt-3 text-sm leading-7 text-midnight/65">{note}</p>
    </div>
  );
}

function DataPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="glass-panel p-6 sm:p-8">
      <p className="section-title">{title}</p>
      <div className="mt-5 space-y-3">{children}</div>
    </div>
  );
}

function LoadingPanel({ label }: { label: string }) {
  return (
    <div className="glass-panel p-8 text-sm text-midnight/70">
      {label}
    </div>
  );
}

function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="glass-panel border border-roseclay/20 p-8 text-sm text-roseclay">
      {message}
    </div>
  );
}
