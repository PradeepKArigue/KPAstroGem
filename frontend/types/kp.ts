export type BirthInput = {
  name: string;
  dateOfBirth: string;
  timeOfBirth: string;
  birthPlace: string;
  state?: string;
  country: string;
  timezone: string;
  latitude?: number;
  longitude?: number;
  manualTimezoneOverride?: string;
  manualCoordinateOverride: boolean;
};

export type ChartCalculationRequest = BirthInput & {
  questionCategory: string;
  question: string;
};

export type LocationSearchResult = {
  displayName: string;
  city: string;
  stateOrProvince?: string | null;
  country?: string | null;
  latitude: number;
  longitude: number;
  timezone?: string | null;
  confidence: number;
};

export type TimezoneResolutionResponse = {
  timezone?: string | null;
  confidence: number;
  note: string;
};

export type LocationValidationRequest = {
  birthPlace: string;
  state?: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  dateOfBirth: string;
  timeOfBirth: string;
};

export type LocationValidationResponse = {
  birthPlace: string;
  state?: string | null;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  normalizedUtcTime: string;
  confidence: number;
  warnings: string[];
};

export type BirthSummary = {
  name: string;
  dateOfBirth: string;
  timeOfBirth: string;
  birthPlace: string;
  state?: string | null;
  country: string;
  timezone: string;
  latitude?: number | null;
  longitude?: number | null;
  questionCategory: string;
  question: string;
  summaryLine: string;
  birthTimeAccuracyNote: string;
};

export type PlanetaryPosition = {
  planet: string;
  sign: string;
  degree: string;
  nakshatra: string;
  pada: number;
  starLord: string;
  subLord: string;
  status: string;
  note: string;
};

export type HouseCusp = {
  house: number;
  sign: string;
  cuspDegree: string;
  signLord: string;
  starLord: string;
  subLord: string;
  note: string;
};

export type DashaSummary = {
  mahaDasha: string;
  bhukti: string;
  antara: string;
  window: string;
  mahaWindow: string;
  bhuktiWindow: string;
  antaraWindow: string;
  status: string;
  note: string;
};

export type RulingFactor = {
  area: string;
  ruler: string;
  note: string;
};

export type ConfidenceLevel = {
  level: string;
  reason: string;
};

export type CalculationTrailEntry = {
  step: string;
  detail: string;
};

export type ChartData = {
  birthSummary: BirthSummary;
  planetaryPositions: PlanetaryPosition[];
  houseCusps: HouseCusp[];
  starLord: RulingFactor;
  subLord: RulingFactor;
  dashaSummary: DashaSummary;
  interpretation: string[];
  confidenceLevel: ConfidenceLevel;
  disclaimer: string;
};

export type ChartCalculationResponse = {
  chartId: string;
  chart: ChartData;
};

export type ChartQuestionRequest = {
  chartId: string;
  question: string;
  optionalDateRange?: string;
};

export type ChartQuestionResponse = {
  question: string;
  classifiedTopic: string;
  plainExplanation: string;
  relevantHouses: number[];
  cuspSubLordAnalysis: string[];
  significatorAnalysis: string[];
  dashaSupport: string[];
  supportingFactors: string[];
  blockingFactors: string[];
  interpretation: string[];
  possibleTimingWindow: string;
  confidenceLevel: ConfidenceLevel;
  calculationTrail: CalculationTrailEntry[];
  disclaimer: string;
};

export type ChartSessionResponse = {
  chartId: string;
  createdAt: string;
  expiresAt: string;
  chartData: ChartData;
  questionHistory: ChartQuestionResponse[];
};

export type QuestionTopic = {
  name: string;
  houseFocus: number[];
  sampleQuestions: string[];
  cautionLevel: string;
};

export type QuestionTopicCatalog = {
  topics: QuestionTopic[];
};

