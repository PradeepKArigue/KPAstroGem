"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { createChartSession, validateLocation } from "@/lib/api";
import type { ChartCalculationRequest, LocationValidationResponse } from "@/types/kp";

const PENDING_CHART_SESSION_KEY = "kpastrogem.pending-chart-request";

export function LocationConfirmation() {
  const router = useRouter();
  const [pendingRequest, setPendingRequest] = useState<ChartCalculationRequest | null>(null);
  const [validation, setValidation] = useState<LocationValidationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const rawPayload = window.sessionStorage.getItem(PENDING_CHART_SESSION_KEY);
    if (!rawPayload) {
      setErrorMessage("No pending birth profile was found. Please enter birth details again.");
      setIsLoading(false);
      return;
    }

    const payload = JSON.parse(rawPayload) as ChartCalculationRequest;
    setPendingRequest(payload);

    async function runValidation() {
      if (payload.latitude == null || payload.longitude == null) {
        setErrorMessage("Resolved latitude and longitude are required before location confirmation.");
        setIsLoading(false);
        return;
      }

      try {
        const result = await validateLocation({
          birthPlace: payload.birthPlace,
          state: payload.state,
          country: payload.country,
          latitude: payload.latitude,
          longitude: payload.longitude,
          timezone: payload.manualTimezoneOverride?.trim() || payload.timezone,
          dateOfBirth: payload.dateOfBirth,
          timeOfBirth: payload.timeOfBirth,
        });
        setValidation(result);
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "The selected location could not be validated.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void runValidation();
  }, []);

  const handleCreateChart = async () => {
    if (!pendingRequest || !validation) {
      return;
    }

    setIsCreating(true);
    setErrorMessage(null);

    try {
      const response = await createChartSession({
        ...pendingRequest,
        timezone: validation.timezone,
        latitude: validation.latitude,
        longitude: validation.longitude,
        manualTimezoneOverride: pendingRequest.manualTimezoneOverride?.trim() || undefined,
      });
      window.sessionStorage.removeItem(PENDING_CHART_SESSION_KEY);
      router.push(`/dashboard/${response.chartId}`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "The chart session could not be created from the confirmed location.",
      );
    } finally {
      setIsCreating(false);
    }
  };

  if (isLoading) {
    return <div className="glass-panel p-8 text-sm text-midnight/70">Validating location, timezone, and normalized birth time...</div>;
  }

  if (!pendingRequest || !validation) {
    return (
      <div className="glass-panel border border-roseclay/20 p-8 text-sm text-roseclay">
        {errorMessage ?? "The location confirmation step is unavailable."}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="glass-panel p-6 sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="section-title">Location Confirmation</p>
            <h1 className="mt-3 font-[family-name:var(--font-heading)] text-4xl font-semibold text-midnight">
              Review the resolved birthplace before chart calculation
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-midnight/70">
              This step keeps private birth details out of the URL while letting you confirm latitude, longitude,
              timezone, and normalized UTC time before creating the temporary chart session.
            </p>
          </div>
          <div className="rounded-3xl bg-slate-50 px-5 py-4 text-sm text-midnight/70">
            <p className="font-semibold text-midnight">Location confidence</p>
            <p className="mt-2 text-2xl font-semibold text-aurora">{Math.round(validation.confidence * 100)}%</p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.92fr]">
        <div className="glass-panel p-6 sm:p-8">
          <p className="section-title">Resolved location</p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <SummaryBadge label="Birth place" value={validation.birthPlace} />
            <SummaryBadge label="State" value={validation.state || "Not provided"} />
            <SummaryBadge label="Country" value={validation.country} />
            <SummaryBadge label="Timezone" value={validation.timezone} />
            <SummaryBadge label="Latitude" value={String(validation.latitude)} />
            <SummaryBadge label="Longitude" value={String(validation.longitude)} />
          </div>
        </div>

        <div className="glass-panel p-6 sm:p-8">
          <p className="section-title">Normalization preview</p>
          <div className="mt-5 rounded-3xl bg-slate-50 p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-aurora/80">Normalized UTC time</p>
            <p className="mt-3 font-[family-name:var(--font-heading)] text-2xl font-semibold text-midnight">
              {new Date(validation.normalizedUtcTime).toUTCString()}
            </p>
          </div>
          <div className="mt-5 space-y-3">
            {validation.warnings.map((warning) => (
              <div key={warning} className="rounded-2xl border border-saffron/40 bg-saffron/10 px-4 py-3 text-sm leading-7 text-midnight/75">
                {warning}
              </div>
            ))}
          </div>
        </div>
      </section>

      {errorMessage ? (
        <div className="rounded-2xl border border-roseclay/20 bg-roseclay/10 px-4 py-3 text-sm text-roseclay">
          {errorMessage}
        </div>
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <button
          type="button"
          disabled={isCreating}
          onClick={() => void handleCreateChart()}
          className="inline-flex items-center justify-center rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isCreating ? "Creating chart session..." : "Create Chart Session"}
        </button>
        <Link
          href="/birth-details"
          className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora"
        >
          Back to Birth Details
        </Link>
      </div>
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
