export type FeatureKey = "N" | "P" | "K" | "temperature" | "humidity" | "ph" | "rainfall";

export interface Feature {
  key: FeatureKey;
  labelKey: string;
  unit: string;
  min: number;
  max: number;
  step: number;
  defaultValue: number;
}

// Source: FEATURE_RANGES in predict.py
export const features: Feature[] = [
  { key: "N", labelKey: "nitrogen", unit: "mg/kg", min: 0, max: 140, step: 1, defaultValue: 50 },
  { key: "P", labelKey: "phosphorus", unit: "mg/kg", min: 5, max: 145, step: 1, defaultValue: 50 },
  { key: "K", labelKey: "potassium", unit: "mg/kg", min: 5, max: 205, step: 1, defaultValue: 50 },
  { key: "ph", labelKey: "ph", unit: "", min: 3.5, max: 9.9, step: 0.1, defaultValue: 6.5 },
  { key: "temperature", labelKey: "temperature", unit: "°C", min: 8, max: 44, step: 0.5, defaultValue: 25 },
  { key: "humidity", labelKey: "humidity", unit: "%", min: 14, max: 100, step: 1, defaultValue: 70 },
  { key: "rainfall", labelKey: "rainfall", unit: "mm", min: 20, max: 300, step: 5, defaultValue: 100 },
];
