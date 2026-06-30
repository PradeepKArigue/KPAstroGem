"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { askQuestion, getChartSession, getQuestionTopics } from "@/lib/api";
import type { ChartQuestionResponse, ChartSessionResponse, QuestionTopic } from "@/types/kp";

type SuggestedPrompt = {
  topic: string;
  houseFocus: number[];
  sample: string;
};

export function QuestionWorkspace({ chartId }: { chartId: string }) {
  const [session, setSession] = useState<ChartSessionResponse | null>(null);
  const [topics, setTopics] = useState<QuestionTopic[]>([]);
  const [question, setQuestion] = useState("");
  const [dateRange, setDateRange] = useState("");
  const [answer, setAnswer] = useState<ChartQuestionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadWorkspace() {
      try {
        const [chartPayload, topicPayload] = await Promise.all([getChartSession(chartId), getQuestionTopics()]);

        if (!cancelled) {
          setSession(chartPayload);
          setTopics(topicPayload.topics);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(error instanceof Error ? error.message : "The question workspace could not be loaded.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadWorkspace();

    return () => {
      cancelled = true;
    };
  }, [chartId]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);

    if (!question.trim() || question.trim().length < 8) {
      setErrorMessage("Please enter a more specific question so the KP reading can focus on the right houses and timing.");
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = await askQuestion({
        chartId,
        question,
        optionalDateRange: dateRange.trim() || undefined,
      });
      setAnswer(payload);
      setSession((current) =>
        current
          ? {
              ...current,
              questionHistory: [...current.questionHistory, payload],
            }
          : current,
      );
      setQuestion("");
      setDateRange("");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "The backend could not answer the question.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="glass-panel p-8 text-sm text-midnight/70">Loading question workspace...</div>;
  }

  if (errorMessage && !session) {
    return <div className="glass-panel border border-roseclay/20 p-8 text-sm text-roseclay">{errorMessage}</div>;
  }

  if (!session) {
    return <div className="glass-panel p-8 text-sm text-midnight/70">The chart session is unavailable.</div>;
  }

  const moon = session.chartData.planetaryPositions.find((planet) => planet.planet === "Moon");
  const lagna = session.chartData.houseCusps.find((cusp) => cusp.house === 1);
  const activeTopic =
    topics.find((topic) => topic.name === session.chartData.birthSummary.questionCategory) ?? topics[0] ?? null;
  const suggestedPrompts = buildSuggestedPrompts(topics);
  const insightLines = buildInsightLines(session.chartData.dashaSummary);

  return (
    <div className="space-y-6">
      <section className="glass-panel overflow-hidden p-0">
        <div className="grid gap-0 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="bg-orbital-grid px-6 py-7 sm:px-8 sm:py-9">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p className="section-title">Ask a KP Question</p>
                <h1 className="mt-3 font-[family-name:var(--font-heading)] text-4xl font-semibold text-midnight sm:text-5xl">
                  Interactive KP Reading
                </h1>
                <p className="mt-4 max-w-3xl text-sm leading-7 text-midnight/70 sm:text-base">
                  Ask focused follow-up questions against the same computed chart. The reading stays tied to the
                  active dasha chain, relevant houses, and the same birth profile so the answer feels consistent rather
                  than generic.
                </p>
              </div>
              <Link
                href={`/dashboard/${chartId}`}
                className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora"
              >
                Back to Dashboard
              </Link>
            </div>

            <div className="mt-6 flex flex-wrap gap-2">
              {insightLines.map((line) => (
                <div
                  key={line}
                  className="rounded-full border border-white/80 bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-midnight/70"
                >
                  {line}
                </div>
              ))}
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <SessionBadge label="Name" value={session.chartData.birthSummary.name} />
              <SessionBadge label="Date of birth" value={session.chartData.birthSummary.dateOfBirth} />
              <SessionBadge label="Time of birth" value={session.chartData.birthSummary.timeOfBirth} />
              <SessionBadge
                label="Birth location"
                value={`${session.chartData.birthSummary.birthPlace}, ${session.chartData.birthSummary.country}`}
              />
            </div>
          </div>

          <div className="border-t border-slate-200/80 bg-white/85 px-6 py-7 sm:px-8 sm:py-9 xl:border-l xl:border-t-0">
            <p className="section-title">Current Reading Context</p>
            <div className="mt-5 space-y-3">
              <ContextRow label="Lagna" value={lagna ? `${lagna.sign} ${lagna.cuspDegree}` : "Pending"} />
              <ContextRow label="Janma rasi" value={moon?.sign ?? "Pending"} />
              <ContextRow label="Nakshatra" value={moon ? `${moon.nakshatra} Pada ${moon.pada}` : "Pending"} />
              <ContextRow
                label="Active dasha"
                value={`${session.chartData.dashaSummary.mahaDasha} / ${session.chartData.dashaSummary.bhukti} / ${session.chartData.dashaSummary.antara}`}
              />
              <ContextRow label="Timing window" value={session.chartData.dashaSummary.window} />
            </div>

            <div className="mt-5 rounded-3xl border border-saffron/40 bg-saffron/10 p-5">
              <p className="text-sm font-semibold text-midnight">Customer experience note</p>
              <p className="mt-2 text-sm leading-7 text-midnight/70">
                A stronger question usually names the topic, desired outcome, and time period. That gives the answer
                room to sound more specific and less repetitive.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <form className="glass-panel p-6 sm:p-8" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="section-title">Question Input</p>
                <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
                  Ask with chart-specific timing and topic context
                </h2>
              </div>
              {activeTopic ? (
                <div className="rounded-2xl border border-aurora/15 bg-aurora/5 px-4 py-3 text-sm text-midnight/70">
                  <span className="font-semibold text-midnight">Suggested house focus:</span>{" "}
                  {activeTopic.houseFocus.join(", ")}
                </div>
              ) : null}
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-3">
              <QuickGuide
                title="Be specific"
                detail="Name the exact life area, like job change, marriage timing, or property."
              />
              <QuickGuide
                title="Add timing"
                detail="Mention a month, quarter, or year if the question depends on timing."
              />
              <QuickGuide
                title="Keep one topic"
                detail="Single-focus questions usually produce clearer KP-style answers than mixed topics."
              />
            </div>

            <div className="mt-6">
              <p className="mb-3 text-sm font-semibold text-midnight">Suggested prompts</p>
              <div className="grid gap-3 sm:grid-cols-2">
                {suggestedPrompts.map((prompt) => (
                  <button
                    key={`${prompt.topic}-${prompt.sample}`}
                    type="button"
                    className="rounded-3xl border border-slate-200 bg-white p-4 text-left transition hover:-translate-y-0.5 hover:border-aurora hover:shadow-lg"
                    onClick={() => setQuestion(prompt.sample)}
                  >
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/80">{prompt.topic}</p>
                    <p className="mt-3 text-sm font-semibold leading-6 text-midnight">{prompt.sample}</p>
                    <p className="mt-3 text-xs uppercase tracking-[0.14em] text-midnight/55">
                      Houses {prompt.houseFocus.join(", ")}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            <label className="mt-6 block">
              <span className="mb-2 block text-sm font-semibold text-midnight">Question</span>
              <textarea
                className="min-h-40 w-full rounded-[28px] border border-slate-200 bg-white px-5 py-4 text-sm leading-7 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Example: Is a role change or promotion more likely for me in the second half of 2026?"
              />
            </label>

            <div className="mt-3 flex items-center justify-between text-xs uppercase tracking-[0.16em] text-midnight/45">
              <span>Better questions create better readings</span>
              <span>{question.trim().length} characters</span>
            </div>

            <label className="mt-5 block">
              <span className="mb-2 block text-sm font-semibold text-midnight">Optional date range</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
                value={dateRange}
                onChange={(event) => setDateRange(event.target.value)}
                placeholder="Example: Second half of 2026"
              />
            </label>

            {errorMessage ? (
              <div className="mt-5 rounded-2xl border border-roseclay/20 bg-roseclay/10 px-4 py-3 text-sm text-roseclay">
                {errorMessage}
              </div>
            ) : null}

            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm leading-7 text-midnight/60">
                The answer will be grounded in the current chart session rather than a generic horoscope template.
              </p>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center justify-center rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isSubmitting ? "Analyzing chart context..." : "Generate KP Reading"}
              </button>
            </div>
          </form>

          {answer ? (
            <section className="glass-panel p-6 sm:p-8">
              <p className="section-title">Latest Reading</p>
              <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <h2 className="font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
                    {answer.classifiedTopic} reading
                  </h2>
                  <p className="mt-3 max-w-3xl text-sm leading-7 text-midnight/70">
                    {pickAnswerLead(answer)}
                  </p>
                </div>
                <div className="rounded-3xl bg-midnight px-5 py-4 text-white">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/70">Confidence</p>
                  <p className="mt-2 text-2xl font-semibold">{answer.confidenceLevel.level}</p>
                  <p className="mt-2 max-w-52 text-sm leading-6 text-white/75">{answer.confidenceLevel.reason}</p>
                </div>
              </div>

              <div className="mt-6 grid gap-3 lg:grid-cols-3">
                <SessionBadge label="Topic" value={answer.classifiedTopic} />
                <SessionBadge label="Timing window" value={answer.possibleTimingWindow} />
                <SessionBadge label="Relevant houses" value={answer.relevantHouses.join(", ")} />
              </div>

              <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
                <div className="rounded-[28px] bg-slate-50 p-5">
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">Reading summary</p>
                  <div className="mt-4 space-y-3">
                    {answer.interpretation.slice(0, 3).map((item) => (
                      <div key={item} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
                        {item}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-[28px] border border-saffron/40 bg-saffron/10 p-5">
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-midnight">What to notice first</p>
                  <ul className="mt-4 space-y-3">
                    {buildPriorityHighlights(answer).map((item) => (
                      <li key={item} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-6 grid gap-6 xl:grid-cols-2">
                <AnswerList title="Cusp sub lord analysis" items={answer.cuspSubLordAnalysis} />
                <AnswerList title="Dasha support" items={answer.dashaSupport} />
                <AnswerList title="Supporting factors" items={answer.supportingFactors} />
                <AnswerList title="Blocking or delaying factors" items={answer.blockingFactors} />
              </div>

              <div className="mt-6 rounded-[28px] bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">Full KP-style interpretation</p>
                <ul className="mt-4 space-y-3">
                  {answer.interpretation.map((item) => (
                    <li key={item} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-6 rounded-[28px] border border-slate-200 bg-white p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-midnight/70">Calculation trail</p>
                <div className="mt-4 space-y-3">
                  {answer.calculationTrail.map((entry) => (
                    <div key={entry.step} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                      <span className="font-semibold text-midnight">{entry.step}:</span> {entry.detail}
                    </div>
                  ))}
                </div>
                <p className="mt-4 text-sm leading-7 text-midnight/70">{answer.disclaimer}</p>
              </div>
            </section>
          ) : null}
        </div>

        <aside className="space-y-6 xl:sticky xl:top-6 xl:self-start">
          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Question Themes</p>
            <div className="mt-5 space-y-3">
              {topics.map((topic) => (
                <div key={topic.name} className="rounded-3xl border border-slate-200 bg-slate-50/90 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-semibold text-midnight">{topic.name}</p>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-midnight/55">
                      H {topic.houseFocus.join(", ")}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-midnight/65">{topic.sampleQuestions[0]}</p>
                </div>
              ))}
            </div>
          </div>

          {session.questionHistory.length > 0 ? (
            <div className="glass-panel p-6 sm:p-8">
              <p className="section-title">Conversation History</p>
              <div className="mt-5 space-y-4">
                {session.questionHistory
                  .slice()
                  .reverse()
                  .map((item, index) => (
                    <div key={`${item.question}-${index}`} className="rounded-3xl bg-slate-50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/80">You asked</p>
                        <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-midnight/55">
                          {item.classifiedTopic}
                        </span>
                      </div>
                      <p className="mt-3 font-semibold leading-6 text-midnight">{item.question}</p>
                      <p className="mt-3 text-xs font-semibold uppercase tracking-[0.18em] text-midnight/60">Reading snapshot</p>
                      <p className="mt-2 text-sm leading-7 text-midnight/70">{pickHistoryPreview(item)}</p>
                    </div>
                  ))}
              </div>
            </div>
          ) : null}
        </aside>
      </section>
    </div>
  );
}

function SessionBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white px-4 py-3 shadow-sm shadow-slate-200/70">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/75">{label}</p>
      <p className="mt-2 text-sm text-midnight/75">{value}</p>
    </div>
  );
}

function ContextRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3">
      <p className="text-sm font-semibold text-midnight">{label}</p>
      <p className="max-w-[14rem] text-right text-sm leading-6 text-midnight/70">{value}</p>
    </div>
  );
}

function QuickGuide({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4">
      <p className="text-sm font-semibold text-midnight">{title}</p>
      <p className="mt-2 text-sm leading-6 text-midnight/65">{detail}</p>
    </div>
  );
}

function AnswerList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-[28px] bg-slate-50 p-5">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">{title}</p>
      <ul className="mt-4 space-y-3">
        {items.map((item, index) => (
          <li key={`${title}-${index}`} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function buildSuggestedPrompts(topics: QuestionTopic[]): SuggestedPrompt[] {
  return topics.slice(0, 6).flatMap((topic) =>
    topic.sampleQuestions.slice(0, 1).map((sample) => ({
      topic: topic.name,
      houseFocus: topic.houseFocus,
      sample,
    })),
  );
}

function buildInsightLines(dashaSummary: ChartSessionResponse["chartData"]["dashaSummary"]) {
  return [
    `Maha ${dashaSummary.mahaDasha}`,
    `Bhukti ${dashaSummary.bhukti}`,
    `Antara ${dashaSummary.antara}`,
    `Window ${dashaSummary.window}`,
  ];
}

function buildPriorityHighlights(answer: ChartQuestionResponse) {
  return [
    `Primary timing window: ${answer.possibleTimingWindow}.`,
    answer.supportingFactors[0] ?? "Supporting factors are still being assembled for this answer.",
    answer.blockingFactors[0] ?? "Blocking factors are currently limited in the generated reading.",
  ];
}

function pickAnswerLead(answer: ChartQuestionResponse) {
  return answer.interpretation[3] ?? answer.interpretation[1] ?? answer.interpretation[0] ?? "Answer summary unavailable.";
}

function pickHistoryPreview(item: ChartQuestionResponse) {
  return item.interpretation[3] ?? item.interpretation[1] ?? item.interpretation[0] ?? "Answer summary unavailable.";
}
