"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Leaf, Info, ChevronDown, ChevronUp, AlertCircle, 
  CloudRain, Beaker, Sprout, CheckCircle2 
} from "lucide-react";
import { features, Feature } from "@/lib/features";
import { predictCrop, cancelInFlightRequest } from "@/lib/api";
import { PredictResponse } from "@/lib/types";
import { getCropMetadata } from "@/lib/crops";
import { t, tCrop, tCond, SupportedLanguage } from "@/lib/i18n";
import { Button } from "@/components/ui/button";

export default function Page() {
  const [lang, setLang] = useState<SupportedLanguage>("English");
  const [isMounted, setIsMounted] = useState(false);

  const [inputs, setInputs] = useState<Record<string, number>>(() => {
    const init: Record<string, number> = {};
    features.forEach((f) => { init[f.key] = f.defaultValue; });
    return init;
  });

  const [lastAnalyzedInputs, setLastAnalyzedInputs] = useState<Record<string, number> | null>(null);
  
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [result, setResult] = useState<{ data: PredictResponse; latencyMs: number } | null>(null);
  const [errorInfo, setErrorInfo] = useState<{ kind: string; message: string } | null>(null);

  const [metaExpanded, setMetaExpanded] = useState(false);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsMounted(true);
    try {
      const saved = localStorage.getItem("app_lang") as SupportedLanguage;
      if (saved && ["English", "Hindi", "Tamil", "Telugu", "Marathi"].includes(saved)) {
        setLang(saved);
        document.documentElement.lang = saved === "English" ? "en" : (saved === "Hindi" ? "hi" : saved === "Tamil" ? "ta" : saved === "Telugu" ? "te" : "mr");
      }
    } catch {
      // ignore
    }
    
    return () => cancelInFlightRequest();
  }, []);

  const handleLangChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value as SupportedLanguage;
    setLang(newLang);
    try {
      localStorage.setItem("app_lang", newLang);
      document.documentElement.lang = newLang === "English" ? "en" : (newLang === "Hindi" ? "hi" : newLang === "Tamil" ? "ta" : newLang === "Telugu" ? "te" : "mr");
    } catch {
      // ignore
    }
  };

  const handleInputChange = (key: string, value: string) => {
    const num = parseFloat(value);
    if (isNaN(num)) return;
    setInputs((prev) => ({ ...prev, [key]: num }));
  };

  const handleInputBlur = (key: string, value: string, f: Feature) => {
    let num = parseFloat(value);
    if (isNaN(num)) num = f.defaultValue;
    if (num < f.min) num = f.min;
    if (num > f.max) num = f.max;
    // apply step clamping
    const steps = Math.round((num - f.min) / f.step);
    num = f.min + steps * f.step;
    // handle float precision issues
    num = Number(num.toFixed(2));
    setInputs((prev) => ({ ...prev, [key]: num }));
  };

  const handleAnalyze = async () => {
    setStatus("loading");
    setErrorInfo(null);
    setLastAnalyzedInputs(null);

    const req = {
      N: inputs.N,
      P: inputs.P,
      K: inputs.K,
      temperature: inputs.temperature,
      humidity: inputs.humidity,
      ph: inputs.ph,
      rainfall: inputs.rainfall,
    };

    const res = await predictCrop(req);

    if (res.type === "success") {
      setResult({ data: res.data, latencyMs: res.latencyMs });
      setStatus("success");
      setLastAnalyzedInputs({ ...inputs });
      
      // Scroll to result on mobile
      if (window.innerWidth < 1024 && resultRef.current) {
        setTimeout(() => {
          resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 100);
      }
      
      // Focus result heading for screen readers
      setTimeout(() => {
        const heading = document.getElementById("result-heading");
        if (heading) heading.focus();
      }, 100);
      
    } else {
      setStatus("error");
      setErrorInfo({ kind: res.kind, message: res.message });
    }
  };

  const inputsChanged = lastAnalyzedInputs !== null && features.some(f => inputs[f.key] !== lastAnalyzedInputs[f.key]);

  const renderInputRow = (f: Feature) => (
    <div key={f.key} className="flex flex-col gap-2 py-3 border-b border-[var(--hairline)] last:border-0">
      <div className="flex justify-between items-center">
        <label htmlFor={`input-${f.key}`} className="text-callout font-medium text-[var(--text)]">
          {t(lang, f.labelKey)} {f.unit ? <span className="text-[var(--text-secondary)] font-normal ml-1">({f.unit})</span> : null}
        </label>
        <input
          id={`input-num-${f.key}`}
          type="number"
          min={f.min}
          max={f.max}
          step={f.step}
          value={inputs[f.key] ?? ""}
          onChange={(e) => handleInputChange(f.key, e.target.value)}
          onBlur={(e) => handleInputBlur(f.key, e.target.value, f)}
          className="w-20 text-right tabular-nums bg-[var(--elevated)] border border-[var(--hairline)] rounded-md px-2 py-1 text-[var(--text)] text-callout focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
          aria-label={`${t(lang, f.labelKey)} numeric input`}
        />
      </div>
      <div className="flex items-center gap-3 mt-1">
        <span className="text-caption text-[var(--text-secondary)] w-8 text-right tabular-nums">{f.min}</span>
        <input
          id={`input-${f.key}`}
          type="range"
          min={f.min}
          max={f.max}
          step={f.step}
          value={inputs[f.key] ?? f.defaultValue}
          onChange={(e) => handleInputChange(f.key, e.target.value)}
          className="flex-1 accent-[var(--accent)] h-1 bg-[var(--hairline)] rounded-full appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2"
          aria-valuetext={`${inputs[f.key]} ${f.unit}`}
          style={{
             // Basic styling for webkit thumb is in globals.css, but we can do inline var for fill
             background: `linear-gradient(to right, var(--accent) 0%, var(--accent) ${((inputs[f.key] - f.min) / (f.max - f.min)) * 100}%, var(--hairline) ${((inputs[f.key] - f.min) / (f.max - f.min)) * 100}%, var(--hairline) 100%)`
          }}
        />
        <span className="text-caption text-[var(--text-secondary)] w-10 tabular-nums">{f.max}</span>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col pb-20">
      {/* Top Bar */}
      <header className="sticky top-0 z-50 top-bar-translucent h-[60px] flex items-center justify-between px-4 lg:px-8">
        <div className="flex items-center gap-2">
          <Leaf className="w-5 h-5 text-[var(--accent)]" />
          <span className="font-semibold text-callout tracking-tight">Quantum Crop Intelligence</span>
        </div>
        {isMounted && (
          <select 
            value={lang} 
            onChange={handleLangChange}
            className="bg-transparent border border-[var(--hairline)] rounded-md px-2 py-1 text-footnote font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
            aria-label="Select language"
          >
            <option className="bg-[var(--surface)] text-[var(--text)]" value="English">English</option>
            <option className="bg-[var(--surface)] text-[var(--text)]" value="Hindi">हिंदी</option>
            <option className="bg-[var(--surface)] text-[var(--text)]" value="Tamil">தமிழ்</option>
            <option className="bg-[var(--surface)] text-[var(--text)]" value="Telugu">తెలుగు</option>
            <option className="bg-[var(--surface)] text-[var(--text)]" value="Marathi">मराठी</option>
          </select>
        )}
      </header>

      <main className="flex-1 w-full max-w-[1080px] mx-auto px-4 lg:px-8 pt-8 lg:pt-12">
        <div className="mb-10 lg:mb-14 text-center lg:text-left">
          <h1 className="text-hero text-[var(--text)] mb-3">{t(lang, "title")}</h1>
          <p className="text-title text-[var(--text-secondary)] font-normal">{t(lang, "subtitle")}</p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 items-start">
          
          {/* Left Column: Inputs */}
          <section className="w-full lg:w-[420px] shrink-0" aria-labelledby="inputs-heading">
            <h2 id="inputs-heading" className="sr-only">Field conditions</h2>
            
            <div className="bg-[var(--surface)] rounded-[20px] shadow-sm border border-[var(--hairline)] overflow-hidden mb-6">
              <div className="bg-[var(--elevated)] px-5 py-3 border-b border-[var(--hairline)]">
                <h3 className="text-headline flex items-center gap-2">
                  <Beaker className="w-4 h-4 text-[var(--text-secondary)]" />
                  {t(lang, "soil_nutrients")}
                </h3>
              </div>
              <div className="px-5 py-2">
                {features.slice(0, 4).map(renderInputRow)}
              </div>
            </div>

            <div className="bg-[var(--surface)] rounded-[20px] shadow-sm border border-[var(--hairline)] overflow-hidden mb-8">
              <div className="bg-[var(--elevated)] px-5 py-3 border-b border-[var(--hairline)]">
                <h3 className="text-headline flex items-center gap-2">
                  <CloudRain className="w-4 h-4 text-[var(--text-secondary)]" />
                  {t(lang, "climate_env")}
                </h3>
              </div>
              <div className="px-5 py-2">
                {features.slice(4, 7).map(renderInputRow)}
              </div>
            </div>

            <Button 
              className="w-full btn-press h-[50px] text-[17px]" 
              onClick={handleAnalyze} 
              disabled={status === "loading"}
            >
              {status === "loading" ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {t(lang, "loading")}
                </div>
              ) : t(lang, "analyze")}
            </Button>
          </section>

          {/* Right Column: Result */}
          <section className="w-full lg:w-[600px] lg:sticky lg:top-[100px]" ref={resultRef} aria-live="polite">
            
            {status === "idle" && !result && (
              <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-center p-8 bg-[var(--surface)] rounded-[20px] border border-[var(--hairline)] border-dashed">
                <Sprout className="w-12 h-12 text-[var(--hairline)] mb-4" />
                <p className="text-body text-[var(--text-secondary)] max-w-[280px]">
                  {t(lang, "empty_placeholder")}
                </p>
              </div>
            )}

            {status === "loading" && !result && (
              <div className="h-full min-h-[400px] flex flex-col items-center justify-center p-8 bg-[var(--surface)] rounded-[20px] border border-[var(--hairline)]">
                <div className="w-10 h-10 border-4 border-[var(--hairline)] border-t-[var(--accent)] rounded-full animate-spin mb-4" />
                <p className="text-callout text-[var(--text-secondary)]">{t(lang, "loading")}</p>
              </div>
            )}

            {status === "error" && errorInfo && (
              <div role="alert" className="p-6 bg-[var(--surface)] rounded-[20px] border border-[var(--status-red)] shadow-sm">
                <div className="flex items-start gap-4">
                  <AlertCircle className="w-6 h-6 text-[var(--status-red)] shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-headline text-[var(--status-red)] mb-1">Analysis failed</h3>
                    <p className="text-body text-[var(--text)] mb-4">{t(lang, `error_${errorInfo.kind.replace("-", "_")}`)}</p>
                    <Button variant="secondary" onClick={handleAnalyze}>{t(lang, "retry")}</Button>
                  </div>
                </div>
              </div>
            )}

            {result && result.data && (
              <div className={`transition-opacity duration-300 ${status === "loading" ? "opacity-50" : "opacity-100 animate-reveal"}`}>
                
                {inputsChanged && (
                  <div className="mb-4 inline-flex items-center gap-2 bg-[var(--status-orange)]/10 text-[var(--status-orange)] px-3 py-1.5 rounded-full text-footnote font-medium">
                    <Info className="w-4 h-4" />
                    {t(lang, "inputs_changed")}
                  </div>
                )}

                <div className="bg-[var(--surface)] rounded-[20px] p-6 lg:p-8 shadow-sm border border-[var(--hairline)] mb-6">
                  <h2 id="result-heading" tabIndex={-1} className="text-footnote text-[var(--text-secondary)] uppercase tracking-wider font-semibold mb-2 outline-none">
                    {t(lang, "recommended")}
                  </h2>
                  <div className="text-hero text-[var(--accent)] mb-8">
                    {tCrop(lang, result.data.primary_recommendation)}
                  </div>

                  {(() => {
                    const cInfo = getCropMetadata(result.data.primary_recommendation);
                    return (
                      <dl className="grid grid-cols-3 gap-4 mb-6">
                        <div>
                          <dt className="text-caption text-[var(--text-secondary)] mb-1">{t(lang, "season")}</dt>
                          <dd className="text-callout font-medium">{tCond(lang, cInfo.season)}</dd>
                        </div>
                        <div>
                          <dt className="text-caption text-[var(--text-secondary)] mb-1">{t(lang, "water_need")}</dt>
                          <dd className="text-callout font-medium">{tCond(lang, cInfo.water)}</dd>
                        </div>
                        <div>
                          <dt className="text-caption text-[var(--text-secondary)] mb-1">{t(lang, "ideal_soil")}</dt>
                          <dd className="text-callout font-medium">{tCond(lang, cInfo.soil)}</dd>
                        </div>
                      </dl>
                    );
                  })()}
                  <p className="text-caption text-[var(--text-secondary)] italic pt-4 border-t border-[var(--hairline)]">
                    * {t(lang, "agronomic_footnote")}
                  </p>
                </div>

                <div className="bg-[var(--surface)] rounded-[20px] p-6 lg:p-8 shadow-sm border border-[var(--hairline)] mb-6">
                  <h3 className="text-headline mb-4">{t(lang, "alternatives")}</h3>
                  <div className="space-y-4">
                    {result.data.candidates.map((c, idx) => {
                      const probPct = Math.round(c.probability * 100);
                      const isFirst = idx === 0;
                      return (
                        <div key={c.name} className="flex flex-col gap-1.5">
                          <div className="flex justify-between items-end">
                            <span className="text-callout font-medium text-[var(--text)]">{tCrop(lang, c.name)}</span>
                            <span className="text-footnote text-[var(--text-secondary)] tabular-nums">{probPct}%</span>
                          </div>
                          <div className="h-1 w-full bg-[var(--hairline)] rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${isFirst ? 'bg-[var(--accent)]' : 'bg-[var(--text-secondary)]'}`} 
                              style={{ width: `${probPct}%` }}
                            />
                          </div>
                          {isFirst && (
                            <p className="text-caption text-[var(--text-secondary)] mt-1">
                              {t(lang, "match_score_footnote")}
                            </p>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div className="bg-[var(--surface)] rounded-[20px] p-6 lg:p-8 shadow-sm border border-[var(--hairline)] mb-6">
                  <h3 className="text-headline mb-4">{t(lang, "your_inputs")}</h3>
                  <div className="space-y-4">
                    {features.map(f => {
                      const val = lastAnalyzedInputs ? lastAnalyzedInputs[f.key] : inputs[f.key];
                      const pct = ((val - f.min) / (f.max - f.min)) * 100;
                      const isNearEdge = pct < 15 || pct > 85;
                      
                      return (
                        <div key={f.key} className="flex flex-col gap-1.5">
                          <div className="flex justify-between items-center text-footnote">
                            <span className="text-[var(--text-secondary)]">{t(lang, f.labelKey)}</span>
                            <span className="tabular-nums font-medium">
                              {val} {f.unit}
                            </span>
                          </div>
                          <div className="relative h-1.5 w-full bg-[var(--hairline)] rounded-full">
                            <div 
                              className="absolute h-2.5 w-2.5 rounded-full bg-[var(--text)] top-1/2 -translate-y-1/2 -ml-1.25 shadow-sm border border-[var(--surface)]"
                              style={{ left: `${pct}%` }}
                            />
                          </div>
                          <div className={`flex items-center gap-1.5 text-caption mt-0.5 ${isNearEdge ? 'text-[var(--status-orange)]' : 'text-[var(--status-green)]'}`}>
                            {isNearEdge ? <AlertCircle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                            {isNearEdge ? t(lang, "near_edge") : t(lang, "within_range")}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div className="bg-[var(--surface)] rounded-[20px] shadow-sm border border-[var(--hairline)] overflow-hidden">
                  <button 
                    onClick={() => setMetaExpanded(!metaExpanded)}
                    className="w-full flex items-center justify-between p-4 text-left focus-visible:outline-none focus-visible:bg-[var(--elevated)] hover:bg-[var(--elevated)] transition-colors"
                    aria-expanded={metaExpanded}
                  >
                    <span className="text-callout font-medium">{t(lang, "about_model")}</span>
                    {metaExpanded ? <ChevronUp className="w-5 h-5 text-[var(--text-secondary)]" /> : <ChevronDown className="w-5 h-5 text-[var(--text-secondary)]" />}
                  </button>
                  {metaExpanded && (
                    <div className="p-4 pt-0 border-t border-[var(--hairline)]">
                      <dl className="grid grid-cols-3 gap-4 mt-4">
                        <div>
                          <dt className="text-caption text-[var(--text-secondary)] mb-1">{t(lang, "num_qubits")}</dt>
                          <dd className="text-callout tabular-nums">{result.data.meta.num_qubits}</dd>
                        </div>
                        <div>
                          <dt className="text-caption text-[var(--text-secondary)] mb-1">{t(lang, "reps")}</dt>
                          <dd className="text-callout tabular-nums">{result.data.meta.reps}</dd>
                        </div>
                        <div>
                          <dt className="text-caption text-[var(--text-secondary)] mb-1">{t(lang, "c_penalty")}</dt>
                          <dd className="text-callout tabular-nums">{result.data.meta.C}</dd>
                        </div>
                      </dl>
                      <p className="text-caption text-[var(--text-secondary)] mt-4">
                        Latency: {result.latencyMs.toFixed(0)} ms
                      </p>
                    </div>
                  )}
                </div>

              </div>
            )}
          </section>

        </div>
      </main>
    </div>
  );
}
