import type {
  ChartCalculationRequest,
  ChartCalculationResponse,
  ChartQuestionRequest,
  ChartQuestionResponse,
  ChartSessionResponse,
  LocationSearchResult,
  LocationValidationRequest,
  LocationValidationResponse,
  QuestionTopicCatalog,
  TimezoneResolutionResponse,
} from "@/types/kp";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = "The backend request failed.";

    try {
      const payload = (await response.json()) as { detail?: string };
      if (typeof payload.detail === "string") {
        detail = payload.detail;
      }
    } catch {
      detail = "The backend request failed.";
    }

    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function createChartSession(payload: ChartCalculationRequest) {
  return apiRequest<ChartCalculationResponse>("/api/charts/calculate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function searchLocations(query: string, state?: string, country?: string) {
  const params = new URLSearchParams({ q: query });
  if (state?.trim()) {
    params.set("state", state.trim());
  }
  if (country?.trim()) {
    params.set("country", country.trim());
  }

  return apiRequest<LocationSearchResult[]>(`/api/locations/search?${params.toString()}`);
}

export function resolveTimezone(latitude: number, longitude: number, birthDate?: string) {
  return apiRequest<TimezoneResolutionResponse>("/api/locations/resolve-timezone", {
    method: "POST",
    body: JSON.stringify({
      latitude,
      longitude,
      birthDate,
    }),
  });
}

export function validateLocation(payload: LocationValidationRequest) {
  return apiRequest<LocationValidationResponse>("/api/locations/validate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getChartSession(chartId: string) {
  return apiRequest<ChartSessionResponse>(`/api/charts/${chartId}`);
}

export function deleteChartSession(chartId: string) {
  return apiRequest<{ status: string }>(`/api/charts/${chartId}`, {
    method: "DELETE",
  });
}

export function askQuestion(payload: ChartQuestionRequest) {
  return apiRequest<ChartQuestionResponse>("/api/questions/ask", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getQuestionTopics() {
  return apiRequest<QuestionTopicCatalog>("/api/questions/topics");
}

