export interface CropMetadata {
  season: string;
  water: string;
  soil: string;
}

export const CROP_METADATA: Record<string, CropMetadata> = {
  "rice":        { season: "Kharif",       water: "High",     soil: "Clay/Loam" },
  "maize":       { season: "Kharif",       water: "Moderate", soil: "Loamy" },
  "jute":        { season: "Kharif",       water: "High",     soil: "Alluvial" },
  "cotton":      { season: "Kharif",       water: "Moderate", soil: "Black Cotton Soil" },
  "coconut":     { season: "Perennial",    water: "High",     soil: "Sandy Loam" },
  "papaya":      { season: "Perennial",    water: "Moderate", soil: "Sandy Loam" },
  "orange":      { season: "Rabi",         water: "Moderate", soil: "Well-drained Loam" },
  "apple":       { season: "Rabi",         water: "Moderate", soil: "Loamy" },
  "muskmelon":   { season: "Zaid",         water: "Moderate", soil: "Sandy Loam" },
  "watermelon":  { season: "Zaid",         water: "Moderate", soil: "Sandy Loam" },
  "grapes":      { season: "Rabi",         water: "Moderate", soil: "Well-drained" },
  "mango":       { season: "Perennial",    water: "Moderate", soil: "Alluvial/Laterite" },
  "banana":      { season: "Perennial",    water: "High",     soil: "Rich Loamy" },
  "pomegranate": { season: "Perennial",    water: "Low",      soil: "Well-drained" },
  "lentil":      { season: "Rabi",         water: "Low",      soil: "Loamy" },
  "blackgram":   { season: "Kharif/Rabi",  water: "Low",      soil: "Clay Loam" },
  "mungbean":    { season: "Kharif/Zaid",  water: "Low",      soil: "Well-drained Loam" },
  "mothbeans":   { season: "Kharif",       water: "Low",      soil: "Sandy" },
  "pigeonpeas":  { season: "Kharif",       water: "Moderate", soil: "Deep Loam" },
  "kidneybeans": { season: "Kharif",       water: "Moderate", soil: "Well-drained Loam" },
  "chickpea":    { season: "Rabi",         water: "Low",      soil: "Heavy Clay/Loam" },
  "coffee":      { season: "Perennial",    water: "High",     soil: "Rich Forest Loam" },
};

export const DEFAULT_CROP: CropMetadata = { season: "-", water: "-", soil: "-" };

export function getCropMetadata(apiName: string): CropMetadata {
  return CROP_METADATA[apiName.toLowerCase()] || DEFAULT_CROP;
}
