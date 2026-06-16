"use client";

import { FormEvent, useState } from "react";

import type { AnalysisRequest, AnalysisResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const questionCategories = [
  "Career",
  "Relationships",
  "Finance",
  "Education",
  "Family",
  "Health",
  "Travel",
  "Spirituality",
  "Other",
];

const initialForm: AnalysisRequest = {
  name: "Pradeep",
  dateOfBirth: "1988-12-09",
  timeOfBirth: "18:30",
  birthPlace: "Secunderabad",
  country: "India",
  questionCategory: "Career",
  question: "How is my career growth?",
};

export default function HomePage() {
  const [formData, setFormData] = useState<AnalysisRequest>(initialForm);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateField = (field: keyof AnalysisRequest, value: string) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const validateForm = () => {
    const missingField = Object.entries(formData).find(([, value]) => !value.trim());
    if (missingField) {
      return "Please complete every field before generating a KP reading.";
    }

    if (formData.question.trim().length < 8) {
      return "Please enter a slightly more detailed question so the reading has context.";
    }

    return null;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);

    const validationError = validateForm();
    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/kp/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const fallbackMessage = "The backend could not complete the placeholder KP analysis.";
        let detail = fallbackMessage;

        try {
          const payload = (await response.json()) as { detail?: string };
          if (typeof payload.detail === "string") {
            detail = payload.detail;
          }
        } catch {
          detail = fallbackMessage;
        }

        throw new Error(detail);
      }

      const payload = (await response.json()) as AnalysisResponse;
      setResult(payload);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "The frontend could not reach the FastAPI backend. Confirm it is running on port 8000.";

      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="relative overflow-hidden px-4 py-8 text-midnight sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-8">
        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="glass-panel bg-orbital-grid p-8 sm:p-10">
            <p className="section-title">KP Astrology MVP</p>
            <h1 className="mt-4 max-w-3xl font-[family-name:var(--font-heading)] text-5xl font-semibold leading-none text-midnight sm:text-6xl">
              Build a calm, structured first reading experience.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-midnight/75 sm:text-lg">
              This local-first version collects birth details and a focused question, then returns a
              structured placeholder KP astrology reading from the FastAPI backend.
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl bg-white/70 p-4">
                <p className="text-sm font-semibold text-aurora">Frontend</p>
                <p className="mt-2 text-sm text-midnight/70">Next.js, React, TypeScript, Tailwind</p>
              </div>
              <div className="rounded-2xl bg-white/70 p-4">
                <p className="text-sm font-semibold text-aurora">Backend</p>
                <p className="mt-2 text-sm text-midnight/70">FastAPI with typed KP placeholder output</p>
              </div>
              <div className="rounded-2xl bg-white/70 p-4">
                <p className="text-sm font-semibold text-aurora">Flow</p>
                <p className="mt-2 text-sm text-midnight/70">One-page submit and results experience</p>
              </div>
            </div>
          </div>

          <aside className="glass-panel p-6 sm:p-8">
            <p className="section-title">Local Test Profile</p>
            <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
              Sample values are preloaded.
            </h2>
            <p className="mt-4 text-sm leading-7 text-midnight/70">
              You can submit immediately once the backend is running, or edit the fields to try other
              questions and locations.
            </p>
            <dl className="mt-6 grid gap-4 text-sm">
              <div className="rounded-2xl bg-slate-50 p-4">
                <dt className="font-semibold text-midnight">Birth profile</dt>
                <dd className="mt-2 text-midnight/70">
                  Pradeep, 1988-12-09, 18:30, Secunderabad, India
                </dd>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <dt className="font-semibold text-midnight">Question</dt>
                <dd className="mt-2 text-midnight/70">How is my career growth?</dd>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <dt className="font-semibold text-midnight">Backend URL</dt>
                <dd className="mt-2 break-all text-midnight/70">{API_BASE_URL}</dd>
              </div>
            </dl>
          </aside>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <form className="glass-panel p-6 sm:p-8" onSubmit={handleSubmit}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="section-title">Birth Input</p>
                <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
                  Enter birth details and a focused question
                </h2>
              </div>
              <span className="rounded-full bg-saffron/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-roseclay">
                MVP
              </span>
            </div>

            <div className="mt-8 grid gap-5 sm:grid-cols-2">
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-midnight">Name</span>
                <input
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                  value={formData.name}
                  onChange={(event) => updateField("name", event.target.value)}
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-midnight">Question category</span>
                <select
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                  value={formData.questionCategory}
                  onChange={(event) => updateField("questionCategory", event.target.value)}
                >
                  {questionCategories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-midnight">Date of birth</span>
                <input
                  type="date"
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                  value={formData.dateOfBirth}
                  onChange={(event) => updateField("dateOfBirth", event.target.value)}
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-midnight">Time of birth</span>
                <input
                  type="time"
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                  value={formData.timeOfBirth}
                  onChange={(event) => updateField("timeOfBirth", event.target.value)}
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-midnight">Birth place</span>
                <input
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                  value={formData.birthPlace}
                  onChange={(event) => updateField("birthPlace", event.target.value)}
                  required
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-midnight">Country</span>
                <input
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                  value={formData.country}
                  onChange={(event) => updateField("country", event.target.value)}
                  required
                />
              </label>
            </div>

            <label className="mt-5 block">
              <span className="mb-2 block text-sm font-semibold text-midnight">Free-text question</span>
              <textarea
                className="min-h-32 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                value={formData.question}
                onChange={(event) => updateField("question", event.target.value)}
                placeholder="Ask a clear question for this MVP reading..."
                required
              />
            </label>

            {errorMessage ? (
              <div className="mt-5 rounded-2xl border border-roseclay/20 bg-roseclay/10 px-4 py-3 text-sm text-roseclay">
                {errorMessage}
              </div>
            ) : null}

            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center justify-center rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isSubmitting ? "Generating placeholder reading..." : "Generate KP Reading"}
              </button>
              <p className="text-sm text-midnight/60">
                No login required. Local development only for this first MVP.
              </p>
            </div>
          </form>

          <section className="glass-panel p-6 sm:p-8">
            <p className="section-title">Results</p>
            <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
              Placeholder KP output appears here
            </h2>

            {!result ? (
              <div className="mt-8 rounded-[2rem] border border-dashed border-slate-300 bg-slate-50/70 p-8 text-sm leading-7 text-midnight/65">
                Start the FastAPI backend, then submit the sample profile or your own details. This
                panel will show birth summary data, planetary placeholders, house cusps, ruling factors,
                interpretation notes, confidence, and the MVP disclaimer.
              </div>
            ) : (
              <div className="mt-8 space-y-6">
                <div className="rounded-[2rem] bg-slate-50 p-5">
                  <h3 className="text-lg font-semibold text-midnight">Birth details summary</h3>
                  <p className="mt-3 text-sm leading-7 text-midnight/75">{result.birthSummary.summaryLine}</p>
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <SummaryBadge label="Name" value={result.birthSummary.name} />
                    <SummaryBadge label="Date of birth" value={result.birthSummary.dateOfBirth} />
                    <SummaryBadge label="Time of birth" value={result.birthSummary.timeOfBirth} />
                    <SummaryBadge label="Birth place" value={result.birthSummary.birthPlace} />
                    <SummaryBadge label="Country" value={result.birthSummary.country} />
                    <SummaryBadge label="Category" value={result.birthSummary.questionCategory} />
                  </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <div className="rounded-[2rem] bg-slate-50 p-5">
                    <h3 className="text-lg font-semibold text-midnight">Planetary positions</h3>
                    <div className="mt-4 space-y-3">
                      {result.planetaryPositions.map((position) => (
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
                          <p className="mt-3 text-sm leading-6 text-midnight/65">{position.note}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-[2rem] bg-slate-50 p-5">
                    <h3 className="text-lg font-semibold text-midnight">House cusps</h3>
                    <div className="mt-4 space-y-3">
                      {result.houseCusps.map((cusp) => (
                        <div key={cusp.house} className="rounded-2xl bg-white p-4">
                          <p className="font-semibold text-midnight">House {cusp.house}</p>
                          <p className="mt-1 text-sm text-midnight/70">
                            {cusp.sign} at {cusp.cuspDegree}
                          </p>
                          <p className="mt-3 text-sm leading-6 text-midnight/65">{cusp.note}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <RulingFactorCard title="Star lord" factor={result.starLord} />
                  <RulingFactorCard title="Sub lord" factor={result.subLord} />
                </div>

                <div className="rounded-[2rem] bg-slate-50 p-5">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <h3 className="text-lg font-semibold text-midnight">KP-style interpretation</h3>
                    <span className="rounded-full bg-aurora/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-aurora">
                      Confidence: {result.confidenceLevel.level}
                    </span>
                  </div>
                  <ul className="mt-4 space-y-3">
                    {result.interpretation.map((item) => (
                      <li key={item} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/75">
                        {item}
                      </li>
                    ))}
                  </ul>
                  <p className="mt-4 text-sm text-midnight/60">{result.confidenceLevel.reason}</p>
                </div>

                <div className="rounded-[2rem] border border-saffron/40 bg-saffron/10 p-5 text-sm leading-7 text-midnight/75">
                  <span className="font-semibold text-midnight">Disclaimer:</span> {result.disclaimer}
                </div>
              </div>
            )}
          </section>
        </section>
      </div>
    </main>
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
  factor,
}: {
  title: string;
  factor: AnalysisResponse["starLord"];
}) {
  return (
    <div className="rounded-[2rem] bg-slate-50 p-5">
      <h3 className="text-lg font-semibold text-midnight">{title}</h3>
      <p className="mt-4 text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">{factor.area}</p>
      <p className="mt-2 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
        {factor.ruler}
      </p>
      <p className="mt-3 text-sm leading-7 text-midnight/65">{factor.note}</p>
    </div>
  );
}
