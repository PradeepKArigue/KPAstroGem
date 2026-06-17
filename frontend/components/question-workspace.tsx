"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { askQuestion, getChartSession, getQuestionTopics } from "@/lib/api";
import type { ChartQuestionResponse, ChartSessionResponse, QuestionTopic } from "@/types/kp";

export function QuestionWorkspace({ chartId }: { chartId: string }) {
  const [session, setSession] = useState<ChartSessionResponse | null>(null);
  const [topics, setTopics] = useState<QuestionTopic[]>([]);
  const [question, setQuestion] = useState("How is my career growth?");
  const [dateRange, setDateRange] = useState("");
  const [answer, setAnswer] = useState<ChartQuestionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadWorkspace() {
      try {
        const [chartPayload, topicPayload] = await Promise.all([
          getChartSession(chartId),
          getQuestionTopics(),
        ]);

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
      setErrorMessage("Please enter a detailed question before asking the KP engine.");
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

  return (
    <div className="space-y-6">
      <section className="glass-panel p-6 sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="section-title">Ask a KP Question</p>
            <h1 className="mt-3 font-[family-name:var(--font-heading)] text-4xl font-semibold text-midnight">
              Question workspace for {session.chartData.birthSummary.name}
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-midnight/70">
              This flow uses a temporary chart session, mapped topic houses, placeholder cusp-sub-lord analysis,
              and a structured disclaimer model.
            </p>
          </div>
          <Link href={`/dashboard/${chartId}`} className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora">
            Back to Dashboard
          </Link>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <form className="glass-panel p-6 sm:p-8" onSubmit={handleSubmit}>
          <p className="section-title">Question Input</p>
          <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
            Ask with a chart-specific context
          </h2>

          <div className="mt-6 rounded-3xl bg-slate-50 p-5">
            <p className="text-sm font-semibold text-midnight">Current chart question category</p>
            <p className="mt-2 text-sm text-midnight/70">{session.chartData.birthSummary.questionCategory}</p>
          </div>

          <div className="mt-5">
            <p className="mb-3 text-sm font-semibold text-midnight">Suggested questions</p>
            <div className="flex flex-wrap gap-2">
              {topics.flatMap((topic) =>
                topic.sampleQuestions.slice(0, 1).map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-midnight transition hover:border-aurora hover:text-aurora"
                    onClick={() => setQuestion(sample)}
                  >
                    {sample}
                  </button>
                )),
              )}
            </div>
          </div>

          <label className="mt-5 block">
            <span className="mb-2 block text-sm font-semibold text-midnight">Question</span>
            <textarea
              className="min-h-36 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </label>

          <label className="mt-5 block">
            <span className="mb-2 block text-sm font-semibold text-midnight">Optional date range</span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
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

          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-6 inline-flex items-center justify-center rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Asking placeholder KP engine..." : "Ask Question"}
          </button>
        </form>

        <aside className="glass-panel p-6 sm:p-8">
          <p className="section-title">Supported Topics</p>
          <div className="mt-5 space-y-3">
            {topics.map((topic) => (
              <div key={topic.name} className="rounded-2xl bg-slate-50 p-4">
                <p className="font-semibold text-midnight">{topic.name}</p>
                <p className="mt-2 text-sm text-midnight/70">Relevant houses: {topic.houseFocus.join(", ")}</p>
                <p className="mt-2 text-sm text-midnight/60">{topic.sampleQuestions[0]}</p>
              </div>
            ))}
          </div>

          {session.questionHistory.length > 0 ? (
            <div className="mt-6">
              <p className="section-title">Conversation History</p>
              <div className="mt-4 space-y-3">
                {session.questionHistory.map((item, index) => (
                  <div key={`${item.question}-${index}`} className="rounded-2xl bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-aurora/80">You asked</p>
                    <p className="mt-2 font-semibold text-midnight">{item.question}</p>
                    <p className="mt-3 text-xs font-semibold uppercase tracking-[0.18em] text-midnight/60">KP response</p>
                    <p className="mt-2 text-sm leading-6 text-midnight/70">{item.interpretation[0]}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </aside>
      </section>

      {answer ? (
        <section className="glass-panel p-6 sm:p-8">
          <p className="section-title">Answer Card</p>
          <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
            {answer.classifiedTopic} reading
          </h2>
          <div className="mt-6 grid gap-6 xl:grid-cols-2">
            <AnswerList title="Relevant houses" items={answer.relevantHouses.map((house) => `House ${house}`)} />
            <AnswerList title="Cusp sub lord analysis" items={answer.cuspSubLordAnalysis} />
            <AnswerList title="Significator analysis" items={answer.significatorAnalysis} />
            <AnswerList title="Dasha support" items={answer.dashaSupport} />
            <AnswerList title="Supporting factors" items={answer.supportingFactors} />
            <AnswerList title="Blocking or delaying factors" items={answer.blockingFactors} />
          </div>

          <div className="mt-6 rounded-3xl bg-slate-50 p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">KP-based interpretation</p>
            <ul className="mt-4 space-y-3">
              {answer.interpretation.map((item) => (
                <li key={item} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-4 text-sm text-midnight/70">Possible timing window: {answer.possibleTimingWindow}</p>
            <p className="mt-2 text-sm text-midnight/70">
              Confidence: {answer.confidenceLevel.level} | {answer.confidenceLevel.reason}
            </p>
          </div>

          <div className="mt-6 rounded-3xl border border-saffron/40 bg-saffron/10 p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-midnight">Calculation trail</p>
            <div className="mt-4 space-y-3">
              {answer.calculationTrail.map((entry) => (
                <div key={entry.step} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
                  <span className="font-semibold text-midnight">{entry.step}:</span> {entry.detail}
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm leading-7 text-midnight/75">{answer.disclaimer}</p>
          </div>
        </section>
      ) : null}
    </div>
  );
}

function AnswerList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-3xl bg-slate-50 p-5">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">{title}</p>
      <ul className="mt-4 space-y-3">
        {items.map((item) => (
          <li key={item} className="rounded-2xl bg-white px-4 py-3 text-sm leading-7 text-midnight/70">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

