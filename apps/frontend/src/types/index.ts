export interface User {
  id: string;
  email: string;
  fullName: string;
  role: string;
  createdAt?: string;
}

export interface AuthResponse {
  token: string;
  tokenType: string;
  user: User;
}

export interface DetectionResult {
  damageType: string;
  confidence: number;
  boundingBox: number[];
  classId: number;
}

export interface AssessmentImage {
  imageId: string;
  filename: string;
  storagePath: string;
  width: number;
  height: number;
  detections: DetectionResult[];
}

export interface NearbyFacility {
  type: string;
  name: string;
  distanceMeters: number;
}

export interface LocationContext {
  latitude: number | null;
  longitude: number | null;
  address: string;
  road: string;
  roadType: string;
  osmMetadata?: Record<string, any>;
  nearbyInfrastructure: NearbyFacility[];
}

export interface WeatherDay {
  date: string;
  precipitationMm: number;
  tempMaxC: number;
  tempMinC: number;
  condition: string;
  isForecast: boolean;
}

export interface WeatherContext {
  available: boolean;
  historical7Days: WeatherDay[];
  forecast7Days: WeatherDay[];
  retrievedAt?: string;
  environmentalNote?: string;
}

export interface TrafficContext {
  available: boolean;
  timestamp?: string;
  durationSeconds?: number;
  staticDurationSeconds?: number;
  trafficDelaySeconds?: number;
  trafficVolumeLevel?: string;
  routeSummary?: string;
  operationalNote?: string;
}

export interface CitationItem {
  sourceId: string;
  title: string;
  page: number;
  chunkId: string;
}

export interface RagAssessmentReport {
  query: string;
  ragMode: string;
  report: string;
  executiveSummary: string;
  engineeringAssessment: string;
  recommendations: string[];
  uncertainties: string[];
  citations: CitationItem[];
  claimVerification?: Record<string, any>;
  latencyMs?: number;
}

export interface Assessment {
  id: string;
  assessmentId: string;
  userId: string;
  images: AssessmentImage[];
  location: LocationContext;
  weather: WeatherContext;
  traffic: TrafficContext;
  rag: RagAssessmentReport;
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: CitationItem[];
  timestamp: string;
}
