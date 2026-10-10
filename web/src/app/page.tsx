"use client";

import { useState } from "react";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const [features, setFeatures] = useState({
    N: 50,
    P: 50,
    K: 50,
    temperature: 25.0,
    humidity: 70.0,
    ph: 6.5,
    rainfall: 100.0,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFeatures({ ...features, [e.target.name]: parseFloat(e.target.value) });
  };

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(features),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 font-sans p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="bg-emerald-900 text-white rounded-xl p-8 shadow-sm">
          <h1 className="text-3xl font-semibold tracking-tight">Crop Recommendation System</h1>
          <p className="text-emerald-100 mt-2 max-w-2xl text-sm leading-relaxed">
            Analytical engineering dashboard. Adjust soil nutrients and climate parameters to simulate inference via 7-qubit Quantum Support Vector Classifier.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Input Panel */}
          <div className="lg:col-span-5 bg-white border border-neutral-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-6 pb-2 border-b">
              Input Parameters
            </h2>

            <div className="space-y-6">
              
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-neutral-800">Soil Nutrients</h3>
                
                {[
                  { name: "N", label: "Nitrogen (N)", min: 0, max: 140 },
                  { name: "P", label: "Phosphorus (P)", min: 5, max: 145 },
                  { name: "K", label: "Potassium (K)", min: 5, max: 205 },
                ].map((input) => (
                  <div key={input.name}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-neutral-600">{input.label}</span>
                      <span className="text-emerald-700 font-semibold">{features[input.name as keyof typeof features]}</span>
                    </div>
                    <input
                      type="range"
                      name={input.name}
                      min={input.min}
                      max={input.max}
                      value={features[input.name as keyof typeof features]}
                      onChange={handleChange}
                      className="w-full accent-emerald-600 h-1.5 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-neutral-800">Climate Conditions</h3>
                
                {[
                  { name: "temperature", label: "Temperature (°C)", min: 8, max: 45, step: 0.1 },
                  { name: "humidity", label: "Humidity (%)", min: 14, max: 100, step: 0.1 },
                  { name: "rainfall", label: "Rainfall (mm)", min: 20, max: 300, step: 1 },
                ].map((input) => (
                  <div key={input.name}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-neutral-600">{input.label}</span>
                      <span className="text-emerald-700 font-semibold">{features[input.name as keyof typeof features]}</span>
                    </div>
                    <input
                      type="range"
                      name={input.name}
                      min={input.min}
                      max={input.max}
                      step={input.step}
                      value={features[input.name as keyof typeof features]}
                      onChange={handleChange}
                      className="w-full accent-emerald-600 h-1.5 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-neutral-800">Soil Chemistry</h3>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-neutral-600">pH Level</span>
                    <span className="text-emerald-700 font-semibold">{features.ph}</span>
                  </div>
                  <input
                    type="range"
                    name="ph"
                    min="3.5"
                    max="10"
                    step="0.1"
                    value={features.ph}
                    onChange={handleChange}
                    className="w-full accent-emerald-600 h-1.5 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
              </div>

            </div>

            <button
              onClick={handleRun}
              disabled={loading}
              className="mt-8 w-full bg-emerald-800 hover:bg-emerald-900 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? "Computing Kernels..." : "Run Model Inference"}
            </button>

          </div>

          {/* Results Panel */}
          <div className="lg:col-span-7 bg-white border border-neutral-200 rounded-xl p-6 shadow-sm min-h-[500px] flex flex-col">
            <h2 className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-6 pb-2 border-b">
              Analysis Output
            </h2>

            {result ? (
              <div className="flex-1 flex flex-col">
                <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-8 text-center mb-8">
                  <p className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-2">
                    Primary Recommendation
                  </p>
                  <h3 className="text-4xl font-bold text-emerald-900">
                    {result.primary_recommendation}
                  </h3>
                </div>

                <div className="space-y-5">
                  <h4 className="text-xs font-bold text-neutral-500 uppercase tracking-wider">
                    Model Confidence
                  </h4>
                  
                  {result.candidates.map((cand: any, idx: number) => {
                    const prob = (cand.probability * 100).toFixed(1);
                    return (
                      <div key={idx} className="flex items-center gap-4">
                        <div className="w-6 h-6 rounded bg-neutral-100 text-neutral-500 flex items-center justify-center text-xs font-bold">
                          {idx + 1}
                        </div>
                        <div className="w-24 font-medium text-neutral-800 text-sm">{cand.name}</div>
                        <div className="w-12 text-right font-semibold text-neutral-700 text-sm">{prob}%</div>
                        <div className="flex-1 h-2 bg-neutral-100 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-emerald-500 rounded-full" 
                            style={{ width: `${prob}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="mt-auto pt-8 border-t border-neutral-100">
                  <p className="text-xs text-neutral-400">
                    Inference via {result.meta.num_qubits}-qubit ZZFeatureMap • reps={result.meta.reps} • C={result.meta.C}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-neutral-400">
                <p className="text-sm">Awaiting input data. Adjust sliders and run inference.</p>
              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}
