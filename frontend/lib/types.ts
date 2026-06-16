export type AnalysisRequest = {
  name: string;
  dateOfBirth: string;
  timeOfBirth: string;
  birthPlace: string;
  country: string;
  questionCategory: string;
  question: string;
};

export type BirthSummary = AnalysisRequest & {
  summaryLine: string;
};

export type PlanetaryPosition = {
  planet: string;
  sign: string;
  degree: string;
  status: string;
  note: string;
};

export type HouseCusp = {
  house: number;
  sign: string;
  cuspDegree: string;
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

export type AnalysisResponse = {
  birthSummary: BirthSummary;
  planetaryPositions: PlanetaryPosition[];
  houseCusps: HouseCusp[];
  starLord: RulingFactor;
  subLord: RulingFactor;
  interpretation: string[];
  confidenceLevel: ConfidenceLevel;
  disclaimer: string;
};

