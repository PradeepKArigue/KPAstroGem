"use client";

import { useRouter } from "next/navigation";
import type { FormEvent, ReactNode } from "react";
import { useEffect, useState } from "react";

import { resolveTimezone, searchLocations } from "@/lib/api";
import type { ChartCalculationRequest, LocationSearchResult } from "@/types/kp";

const PENDING_CHART_SESSION_KEY = "kpastrogem.pending-chart-request";

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
  name: "",
  dateOfBirth: "",
  timeOfBirth: "",
  birthPlace: "",
  state: "",
  country: "",
  timezone: "",
  latitude: undefined,
  longitude: undefined,
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
  const [locationSuggestions, setLocationSuggestions] = useState<LocationSearchResult[]>([]);
  const [isResolvingPlace, setIsResolvingPlace] = useState(false);
  const [placeLookupMessage, setPlaceLookupMessage] = useState<string | null>(null);
  const [hasSelectedSuggestion, setHasSelectedSuggestion] = useState(false);

  const updateField = <T extends keyof ChartCalculationRequest>(field: T, value: ChartCalculationRequest[T]) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  useEffect(() => {
    if (formData.manualCoordinateOverride) {
      setLocationSuggestions([]);
      setPlaceLookupMessage(null);
      return;
    }

    const query = formData.birthPlace.trim();
    if (query.length < 2) {
      setLocationSuggestions([]);
      setPlaceLookupMessage(null);
      return;
    }

    let isCancelled = false;
    const timeoutId = window.setTimeout(async () => {
      setIsResolvingPlace(true);
      setPlaceLookupMessage(null);

      try {
        const suggestions = await searchLocations(query, formData.state, formData.country);
        if (isCancelled) {
          return;
        }

        setLocationSuggestions(suggestions);
        if (suggestions.length === 0) {
          setPlaceLookupMessage("No matching places were found yet. Try adding a state or country.");
        } else if (suggestions.length > 1) {
          setPlaceLookupMessage("Multiple location matches were found. Please choose the best one before continuing.");
        }
      } catch {
        if (!isCancelled) {
          setLocationSuggestions([]);
          setPlaceLookupMessage("Place lookup is unavailable right now. You can still enter coordinates manually.");
        }
      } finally {
        if (!isCancelled) {
          setIsResolvingPlace(false);
        }
      }
    }, 350);

    return () => {
      isCancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [formData.birthPlace, formData.country, formData.manualCoordinateOverride, formData.state]);

  const applyLocationSuggestion = async (suggestion: LocationSearchResult) => {
    const timezoneResult = suggestion.timezone
      ? { timezone: suggestion.timezone }
      : await resolveTimezone(suggestion.latitude, suggestion.longitude, formData.dateOfBirth);

    setFormData((current) => ({
      ...current,
      birthPlace: suggestion.city,
      state: suggestion.stateOrProvince ?? current.state,
      country: suggestion.country ?? current.country,
      latitude: suggestion.latitude,
      longitude: suggestion.longitude,
      timezone: timezoneResult.timezone || current.timezone,
      manualCoordinateOverride: false,
    }));
    setLocationSuggestions([]);
    setHasSelectedSuggestion(true);
    setPlaceLookupMessage(
      timezoneResult.timezone
        ? `Coordinates and timezone loaded from ${suggestion.displayName}. Confidence ${Math.round(
            suggestion.confidence * 100,
          )}%.`
        : `Coordinates loaded from ${suggestion.displayName}.`,
    );
  };

  const validate = () => {
    if (!formData.name.trim() || !formData.birthPlace.trim() || !formData.country.trim()) {
      return "Please complete the required birth identity fields.";
    }

    if (!formData.dateOfBirth || !formData.timeOfBirth) {
      return "Birth date and birth time are required.";
    }

    if (!formData.manualCoordinateOverride && !hasSelectedSuggestion) {
      return "Please select one of the suggested locations so the correct coordinates can be confirmed.";
    }

    if ((formData.latitude ?? null) === null || (formData.longitude ?? null) === null) {
      return "Latitude and longitude are required before continuing to location confirmation.";
    }

    if (!formData.question.trim() || formData.question.trim().length < 8) {
      return "Please enter a more specific question so the KP flow has useful context.";
    }

    return null;
  };

  const handleBirthPlaceChange = (value: string) => {
    setHasSelectedSuggestion(false);
    setFormData((current) => ({
      ...current,
      birthPlace: value,
      latitude: current.manualCoordinateOverride ? current.latitude : undefined,
      longitude: current.manualCoordinateOverride ? current.longitude : undefined,
      timezone: current.manualCoordinateOverride ? current.timezone : "",
    }));
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
      window.sessionStorage.setItem(
        PENDING_CHART_SESSION_KEY,
        JSON.stringify({
          ...formData,
          manualTimezoneOverride: formData.manualTimezoneOverride?.trim() || undefined,
        }),
      );
      router.push("/location-confirmation");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "The location confirmation step could not be prepared. Please try again.",
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
          <input
            className={inputClass}
            value={formData.name}
            onChange={(event) => updateField("name", event.target.value)}
            placeholder="Enter the chart owner's name"
          />
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
          <div className="space-y-3">
            <input
              className={inputClass}
              value={formData.birthPlace}
              onChange={(event) => handleBirthPlaceChange(event.target.value)}
              placeholder="Start typing a city, town, or locality"
            />
            {!formData.manualCoordinateOverride && (isResolvingPlace || locationSuggestions.length > 0 || placeLookupMessage) ? (
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-midnight/60">
                  {isResolvingPlace ? "Resolving place..." : "Suggested places"}
                </p>
                <div className="mt-2 space-y-2">
                  {locationSuggestions.map((suggestion) => (
                    <button
                      key={`${suggestion.displayName}-${suggestion.latitude}-${suggestion.longitude}`}
                      type="button"
                      className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm text-midnight transition hover:border-aurora hover:bg-aurora/5"
                      onClick={() => void applyLocationSuggestion(suggestion)}
                    >
                      <span className="block font-semibold">{suggestion.city}</span>
                      <span className="mt-1 block text-midnight/65">{suggestion.displayName}</span>
                      <span className="mt-2 block text-xs uppercase tracking-[0.18em] text-aurora/80">
                        Confidence {Math.round(suggestion.confidence * 100)}%
                      </span>
                    </button>
                  ))}
                  {placeLookupMessage ? <p className="text-sm text-midnight/70">{placeLookupMessage}</p> : null}
                </div>
              </div>
            ) : null}
          </div>
        </Field>
        <Field label="State or province">
          <input
            className={inputClass}
            value={formData.state ?? ""}
            onChange={(event) => updateField("state", event.target.value)}
            placeholder="Optional, but helps narrow the location"
          />
        </Field>
        <Field label="Country">
          <input
            className={inputClass}
            value={formData.country}
            onChange={(event) => updateField("country", event.target.value)}
            placeholder="Country"
          />
        </Field>
        <Field label="Timezone">
          <input
            className={inputClass}
            value={formData.timezone}
            onChange={(event) => updateField("timezone", event.target.value)}
            placeholder="Auto-filled after selecting a location"
          />
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
          onChange={(event) => {
            setHasSelectedSuggestion(event.target.checked || hasSelectedSuggestion);
            updateField("manualCoordinateOverride", event.target.checked);
          }}
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
          {isSubmitting ? "Preparing location confirmation..." : "Continue to Location Confirmation"}
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
