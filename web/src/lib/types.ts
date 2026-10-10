export interface PredictRequest {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
}

export interface Candidate {
  name: string;
  probability: number;
}

export interface PredictResponse {
  primary_recommendation: string;
  candidates: Candidate[];
  meta: {
    num_qubits: number;
    reps: number;
    C: number;
  };
}

export type ApiResult = 
  | { type: "success"; data: PredictResponse; latencyMs: number }
  | { type: "error"; kind: "unreachable" | "timeout" | "server" | "invalid-input" | "malformed-response"; message: string };
