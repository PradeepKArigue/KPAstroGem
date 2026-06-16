"use client";

import { useRouter } from "next/navigation";
import type { FormEvent, ReactNode } from "react";
import { useState } from "react";

import { createChartSession } from "@/lib/api";
import type { ChartCalculationRequest } from "@/types/kp";

const questionCategories = [
  "Career",
  "Marriage",
  "Finance",
  "Foreign Settlement",
  "Property",
  "Children",
  "Business",
  "Education",
  "Health Caution",
  "Legal Caution",
];

const initialForm: ChartCalculationRequest = {
  name: "Pradeep",
  dateOfBirth: "1988-12-09",
  timeOfBirth: "18:30",
  birthPlace: "Secunderabad",
  state: "Telangana",
  country: "India",
  timezone: "Asia/Kolkata",
  latitude: 17.4399,
  longitude: 78.4983,
  manualTimezoneOverride: "",
  manualCoordinateOverride: false,
  questionCategory: "Career",
  question: "How is my career growth?",
};

export function BirthForm() {
  const router = useRouter();
  const [formData, setFormData] = useState<ChartCalculationRequest>(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const updateField = <T extends keyof ChartCalculationRequest>(field: T, value: ChartCalculationRequest[T]) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const validate = () => {
    if (!formData.name.trim() || !formData.birthPlace.trim() || !formData.country.trim()) {
      return "Please complete the required birth identity fields.";
    }

    if (!formData.dateOfBirth || !formData.timeOfBirth) {
      return "Birth date and birth time are required.";
    }

    if (!formData.question.trim() || formData.question.trim().length < 8) {
      return "Please enter a more specific question so the KP flow has useful context.";
    }

    return null;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);

    const validationError = validate();
    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await createChartSession({
        ...formData,
        manualTimezoneOverride: formData.manualTimezoneOverride?.trim() || undefined,
      });
      router.push(`/dashboard/${response.chartId}`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "The chart session could not be created. Confirm the backend is running.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="glass-panel p-6 sm:p-8" onSubmit={handleSubmit}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-title">Birth Details</p>
          <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
            Create a temporary chart session
          </h2>
        </div>
        <span className="rounded-full bg-saffron/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-roseclay">
          No Login
        </span>
      </div>

      <div className="mt-8 grid gap-5 sm:grid-cols-2">
        <Field label="Name">
          <input className={inputClass} value={formData.name} onChange={(event) => updateField("name", event.target.value)} />
        </Field>
        <Field label="Question category">
          <select
            className={inputClass}
            value={formData.questionCategory}
            onChange={(event) => updateField("questionCategory", event.target.value)}
          >
            {questionCategories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Date of birth">
          <input type="date" className={inputClass} value={formData.dateOfBirth} onChange={(event) => updateField("dateOfBirth", event.target.value)} />
        </Field>
        <Field label="Time of birth">
          <input type="time" className={inputClass} value={formData.timeOfBirth} onChange={(event) => updateField("timeOfBirth", event.target.value)} />
        </Field>
        <Field label="Birth city">
          <input className={inputClass} value={formData.birthPlace} onChange={(event) => updateField("birthPlace", event.target.value)} />
        </Field>
        <Field label="State or province">
          <input className={inputClass} value={formData.state ?? ""} onChange={(event) => updateField("state", event.target.value)} />
        </Field>
        <Field label="Country">
          <input className={inputClass} value={formData.country} onChange={(event) => updateField("country", event.target.value)} />
        </Field>
        <Field label="Timezone">
          <input className={inputClass} value={formData.timezone} onChange={(event) => updateField("timezone", event.target.value)} />
        </Field>
        <Field label="Latitude">
          <input
            type="number"
            step="0.0001"
            className={inputClass}
            value={formData.latitude ?? ""}
            onChange={(event) => updateField("latitude", event.target.value ? Number(event.target.value) : undefined)}
          />
        </Field>
        <Field label="Longitude">
          <input
            type="number"
            step="0.0001"
            className={inputClass}
            value={formData.longitude ?? ""}
            onChange={(event) => updateField("longitude", event.target.value ? Number(event.target.value) : undefined)}
          />
        </Field>
      </div>

      <label className="mt-5 block">
        <span className="mb-2 block text-sm font-semibold text-midnight">Manual timezone override</span>
        <input
          className={inputClass}
          value={formData.manualTimezoneOverride ?? ""}
          onChange={(event) => updateField("manualTimezoneOverride", event.target.value)}
          placeholder="Optional override if the resolved timezone looks incorrect"
        />
      </label>

      <label className="mt-5 flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-midnight/75">
        <input
          type="checkbox"
          checked={formData.manualCoordinateOverride}
          onChange={(event) => updateField("manualCoordinateOverride", event.target.checked)}
        />
        Use the entered latitude and longitude as a manual override for this temporary session
      </label>

      <label className="mt-5 block">
        <span className="mb-2 block text-sm font-semibold text-midnight">Question</span>
        <textarea
          className="min-h-32 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10"
          value={formData.question}
          onChange={(event) => updateField("question", event.target.value)}
          placeholder="Ask a focused KP question..."
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
          {isSubmitting ? "Creating chart session..." : "Create Chart Session"}
        </button>
        <p className="text-sm text-midnight/60">
          Temporary chart sessions expire automatically and are not exposed in public birth-data URLs.
        </p>
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-midnight">{label}</span>
      {children}
    </label>
  );
}

const inputClass =
  "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-aurora focus:ring-4 focus:ring-aurora/10";
