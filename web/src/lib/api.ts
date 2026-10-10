import { PredictRequest, PredictResponse, ApiResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

let currentAbortController: AbortController | null = null;

export function cancelInFlightRequest() {
  if (currentAbortController) {
    currentAbortController.abort();
    currentAbortController = null;
  }
}

export async function predictCrop(request: PredictRequest): Promise<ApiResult> {
  cancelInFlightRequest();
  
  currentAbortController = new AbortController();
  const signal = currentAbortController.signal;
  
  const timeoutId = setTimeout(() => {
    if (currentAbortController) currentAbortController.abort();
  }, 15000);

  const startTime = performance.now();

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 422) {
        return { type: "error", kind: "invalid-input", message: "Invalid input values." };
      }
      return { type: "error", kind: "server", message: "Server error or model not loaded." };
    }

    const data = await response.json();
    
    // Hand-written runtime validation
    if (!data || typeof data !== "object") throw new Error("Not an object");
    if (typeof data.primary_recommendation !== "string") throw new Error("Missing primary_recommendation");
    if (!Array.isArray(data.candidates) || data.candidates.length < 1) throw new Error("Missing or empty candidates");
    
    for (const c of data.candidates) {
      if (typeof c.name !== "string") throw new Error("Candidate missing name");
      if (typeof c.probability !== "number" || !Number.isFinite(c.probability) || c.probability < 0 || c.probability > 1) {
        throw new Error("Candidate probability invalid");
      }
    }
    
    if (!data.meta || typeof data.meta !== "object") throw new Error("Missing meta");
    if (typeof data.meta.num_qubits !== "number") throw new Error("Missing num_qubits");
    if (typeof data.meta.reps !== "number") throw new Error("Missing reps");
    if (typeof data.meta.C !== "number") throw new Error("Missing C");

    const latencyMs = performance.now() - startTime;

    return { type: "success", data: data as PredictResponse, latencyMs };
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof Error && err.name === "AbortError") {
      return { type: "error", kind: "timeout", message: "Request timed out." };
    }
    if (err instanceof TypeError && err.message === "Failed to fetch") {
      return { type: "error", kind: "unreachable", message: "Could not connect to the server." };
    }
    return { type: "error", kind: "malformed-response", message: "Received malformed data from the server." };
  }
}
