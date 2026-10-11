# UI Status Report — Quantum ML Crop Recommendation Project

**Review scope:** UI only  
**Backend modification:** None  
**Files modified by this report:** This Markdown file only

## 1. Stack and structure

### 1.1 UI implementations present

The repository contains three separate UI directions:

1. **Streamlit application — most complete**
   - Main file: [`app.py`](../app.py)
   - Uses Python, Streamlit, Plotly, inline HTML, and custom CSS.
   - Directly calls the Python prediction pipeline.

2. **Next.js web UI — partially implemented**
   - Root: [`web/`](../web/)
   - Uses Next.js, React, TypeScript, Tailwind CSS v4, shadcn-style configuration, Base UI, and related utility packages.
   - Contains a crop dashboard that calls the FastAPI endpoint.

3. **Vite/React frontend — untouched starter template**
   - Root: [`frontend/`](../frontend/)
   - Uses React, TypeScript, Vite, and plain CSS.
   - Still displays the default Vite starter screen.
   - Does not connect to the crop recommendation backend.

### 1.2 Framework, language, build tool, and styling

| UI area | Framework/library | Language | Build tool | Styling |
|---|---|---|---|---|
| Streamlit | Streamlit, Plotly | Python | Streamlit runtime | Inline CSS and HTML |
| `frontend/` | React | TypeScript | Vite | Plain CSS and CSS variables |
| `web/` | Next.js and React | TypeScript/TSX | Next.js | Tailwind CSS v4 and CSS variables |

There is no unified frontend architecture. The project currently has two React applications plus the Streamlit application.

### 1.3 UI-related tree

```text
quantum-agri-advisory/
├── app.py
│   └── Main Streamlit crop recommendation UI
├── app.py.checkpoint
│   └── Saved Streamlit UI checkpoint
├── app.py.rich_ui
│   └── Saved rich Streamlit UI version
├── rewrite.py
│   └── Script used to transform/rewrite app.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── App.css
│       ├── index.css
│       └── assets/
│           ├── hero.png
│           ├── react.svg
│           └── vite.svg
└── web/
    ├── package.json
    ├── package-lock.json
    ├── components.json
    ├── next.config.ts
    ├── public/
    │   ├── file.svg
    │   ├── globe.svg
    │   ├── next.svg
    │   ├── vercel.svg
    │   └── window.svg
    └── src/
        ├── app/
        │   ├── globals.css
        │   ├── layout.tsx
        │   └── page.tsx
        ├── components/
        │   └── ui/
        │       └── button.tsx
        └── lib/
            └── utils.ts
```

### 1.4 Dependencies

The Streamlit UI uses Streamlit, Plotly, pandas, Python standard-library modules, and the prediction functions from [`predict.py`](../predict.py). Its declared Python dependencies are in [`requirements.txt`](../requirements.txt).

The Next.js dependencies are declared in [`web/package.json`](../web/package.json) and locked in [`web/package-lock.json`](../web/package-lock.json). They include Next.js, React, TypeScript, Tailwind CSS v4, Base UI, `class-variance-authority`, `cn`, `shadcn`, and `tw-animate-css`.

The Vite dependencies are declared in [`frontend/package.json`](../frontend/package.json) and include React, TypeScript, Vite, and Oxlint.

## 2. History: what happened with the UI

### 2.1 Basic UI and frontend scaffolding

Commit `0a48d0c` is titled **“Model train and Basic UI”**. The repository contains:

- The root Streamlit app.
- A Vite/React starter under [`frontend/`](../frontend/).
- A Next.js starter under [`web/`](../web/).
- The FastAPI service in [`api.py`](../api.py).

The Vite and Next.js applications were scaffolded, but neither was fully consolidated as the single project UI.

### 2.2 Streamlit redesign

Commit `24edcee` is titled **“UI”**. It changed [`app.py`](../app.py) and [`predict.py`](../predict.py), and added:

- [`app.py.checkpoint`](../app.py.checkpoint)
- [`app.py.rich_ui`](../app.py.rich_ui)
- [`rewrite.py`](../rewrite.py)

The redesign introduced:

- Dark glassmorphism styling.
- Gold/orange and green accents.
- Sidebar input controls.
- Multilingual labels.
- Hero, loading, and empty states.
- Crop recommendation results.
- Confidence and crop-ranking displays.
- Crop metadata such as season, water requirement, and soil type.
- Nutrient gauges.
- Confidence-distribution and environmental-profile charts.

### 2.3 Current UI history

The repository now contains several parallel UI paths rather than one finalized product:

- **Streamlit:** most complete and directly connected to inference.
- **Next.js:** feature-specific prototype with HTTP API integration.
- **Vite:** default starter screen, not connected to the project.

The history does not show a later cleanup or consolidation step that retires the duplicate frontends or the saved Streamlit snapshots.

### 2.4 Decisions and constraints visible in the current code

1. Streamlit was treated as the primary implementation.
2. Streamlit imports the Python inference functions directly.
3. The visual redesign prioritized a presentation-oriented dashboard.
4. Next.js was developed as a separate browser/API option.
5. Vite remains an uncompleted alternative.
6. No shared design system or shared API client was created across the UIs.

## 3. Current state

### 3.1 Streamlit application

**Status: Mostly implemented, backend-dependent**

The active Streamlit entry point is [`app.py`](../app.py). It includes:

- Language selection.
- Soil nutrient controls.
- Climate and environmental controls.
- Slider and numeric-input synchronization.
- Awaiting-data hero state.
- Loading state.
- Crop recommendation report.
- Top-crop confidence and alternatives.
- Parameter status badges.
- Crop metadata.
- Nutrient gauges.
- Confidence distribution chart.
- Environmental radar chart.
- Timestamp/status information.

The seven input features are:

- Nitrogen
- Phosphorus
- Potassium
- Soil pH
- Temperature
- Humidity
- Rainfall

The UI constructs a pandas DataFrame and calls:

```python
result = predict_crops(pipeline, input_data)
```

The Streamlit UI expects output fields including:

- `predicted_crop`
- `top1`
- `top1_prob`
- `top2`
- `top2_prob`
- `top3`
- `top3_prob`

The model pipeline is loaded from the `models/` directory through `load_pipeline()`.

### 3.2 Next.js dashboard

**Status: Partial but functionally connected**

The main page is [`web/src/app/page.tsx`](../web/src/app/page.tsx). It contains:

- Seven feature sliders.
- React state for input values.
- A prediction button.
- Loading-state button text.
- A crop recommendation panel.
- Candidate crops and probability bars.
- Model metadata.
- An empty state before the first prediction.

The page sends:

```text
POST http://localhost:8000/predict
```

with a body shaped like:

```json
{
  "N": 50,
  "P": 50,
  "K": 50,
  "temperature": 25,
  "humidity": 70,
  "ph": 6.5,
  "rainfall": 100
}
```

It expects a response containing:

```json
{
  "primary_recommendation": "Crop name",
  "candidates": [
    {
      "name": "Crop name",
      "probability": 0.8
    }
  ],
  "meta": {
    "num_qubits": 7,
    "reps": 3,
    "C": 10
  }
}
```

The request and response contract is coupled to [`api.py`](../api.py).

#### Next.js issues

- The API URL is hardcoded to `http://localhost:8000/predict`.
- There is no environment-based API configuration.
- Network errors are only sent to `console.error`.
- HTTP errors are not explicitly handled through `response.ok`.
- There is no visible retry or error state.
- The API result and candidate entries use `any`.
- Unexpected response shapes are not validated.
- There is no request timeout or cancellation.
- The input ranges are manually duplicated instead of being read from a shared contract.
- The page uses raw HTML controls even though a reusable Button component exists.
- Accessibility labels and live-region announcements are incomplete.

### 3.3 Vite/React frontend

**Status: Incomplete starter template**

The main file is [`frontend/src/App.tsx`](../frontend/src/App.tsx). It currently shows:

- Vite and React logos.
- A counter button.
- Vite and React documentation links.
- Social/project links.

It does not show:

- Crop inputs.
- Crop recommendations.
- Quantum model metadata.
- API results.
- Agricultural content.
- Project-specific loading or error states.

It has no backend or model integration.

### 3.4 Known bugs and concerns

The following issues are supported by static inspection:

1. The repository has three competing UI implementations.
2. The Vite app is still a starter template.
3. Next.js API failures are not visible to users.
4. Next.js API data is untyped.
5. The Next.js API origin is hardcoded.
6. Frontend and backend input ranges are not exactly aligned.
7. Streamlit pipeline-loading exceptions are caught and reduced to a generic error state.
8. Streamlit relies heavily on raw HTML and CSS.
9. Multiple Streamlit snapshots are retained.
10. Some UI imports appear duplicated or unused.

The following were **NOT VERIFIED IN THIS READ-ONLY REVIEW**:

- Streamlit runtime behavior.
- Next.js production build.
- Vite production build.
- Browser console output.
- Lighthouse results.
- Automated accessibility results.

### 3.5 Real, static, and mock data

#### Streamlit

Prediction values are generated from the real model pipeline when it is available. Crop descriptions, translations, season information, water requirements, and soil descriptions are hardcoded presentation metadata in [`app.py`](../app.py).

#### Next.js

Prediction results come from the real API when the API is running. Initial input values are hardcoded defaults:

```text
N=50, P=50, K=50, temperature=25, humidity=70, ph=6.5, rainfall=100
```

#### Vite

The Vite interface is entirely starter/demo content.

### 3.6 Dead or duplicated UI code

Potentially inactive or development-only files include:

- [`app.py.checkpoint`](../app.py.checkpoint)
- [`app.py.rich_ui`](../app.py.rich_ui)
- [`rewrite.py`](../rewrite.py)
- [`frontend/src/App.tsx`](../frontend/src/App.tsx)
- [`frontend/src/App.css`](../frontend/src/App.css)
- Starter assets under [`frontend/src/assets/`](../frontend/src/assets/)
- Default assets under [`web/public/`](../web/public/)

The generated Button component at [`web/src/components/ui/button.tsx`](../web/src/components/ui/button.tsx) is not used by the main Next.js page. The utility in [`web/src/lib/utils.ts`](../web/src/lib/utils.ts) is also not used by the current dashboard page.

## 4. Design system status

### 4.1 Streamlit design

The Streamlit application uses:

- Very dark navy/black background.
- Warm orange/gold primary accent, including approximately `#f4a853`.
- Green success/positive accent, including approximately `#4ade80`.
- Warm off-white text, including approximately `#f0ece3`.
- Slate-gray secondary text, including approximately `#94a3b8`.
- Red error/attention color, including approximately `#ef4444`.
- Google Font `Plus Jakarta Sans`.
- Glassmorphism cards.
- Blurred translucent panels.
- Gradients and glow effects.
- Rounded cards.
- Animated hero/title elements.

### 4.2 Next.js design

The Next.js page mainly uses:

- Neutral light backgrounds.
- Emerald green cards and accents.
- Tailwind utility classes.
- Geist Sans and Geist Mono from [`web/src/app/layout.tsx`](../web/src/app/layout.tsx).

Global light/dark design tokens exist in [`web/src/app/globals.css`](../web/src/app/globals.css), but the page primarily uses explicit light-theme utility classes. No visible theme switcher exists.

### 4.3 Vite design

The Vite starter uses:

- Purple accent styling.
- System UI fonts.
- CSS variables.
- `prefers-color-scheme` light/dark behavior.

This design is unrelated to the Streamlit and Next.js designs.

### 4.4 Responsiveness

The Next.js UI has the clearest responsive structure, including a one-column-to-large-screen grid transition. However, mobile behavior has not been validated.

The Streamlit UI uses Streamlit columns and several fixed HTML heights, including large hero and chart containers. Narrow-screen overflow and layout behavior have not been formally tested.

The Vite UI has basic starter responsiveness but is not the project UI.

### 4.5 Accessibility

Accessibility is incomplete:

- Next.js range inputs do not clearly provide explicit accessible labels.
- Loading and result changes are not announced through an ARIA live region.
- API errors are not presented accessibly.
- Streamlit uses extensive raw HTML and decorative SVG.
- Color is heavily used to communicate status.
- Contrast, keyboard navigation, and screen-reader behavior have not been audited.

### 4.6 Loading, error, and empty states

#### Streamlit

Implemented:

- Missing-pipeline error block.
- Awaiting-data hero.
- Custom loading indicator.
- Empty/attention status content.

Missing or weak:

- Prediction exceptions are not explicitly handled for the user.
- Pipeline-loading errors are hidden behind a generic message.
- There is no retry action.

#### Next.js

Implemented:

- Disabled/loading prediction button.
- Empty result panel before inference.

Missing:

- Visible API error state.
- HTTP error state.
- Timeout state.
- Malformed-response state.
- Retry action.
- Empty-candidate handling.
- Request cancellation.

#### Vite

No project-specific loading, error, or empty states exist.

## 5. Backend dependency boundaries

### 5.1 UI files importing backend code directly

The following files directly import the Python inference layer:

- [`app.py`](../app.py)
- [`app.py.rich_ui`](../app.py.rich_ui)
- [`app.py.checkpoint`](../app.py.checkpoint)

They import `load_pipeline`, `predict_crops`, and `FEATURE_RANGES` from [`predict.py`](../predict.py).

### 5.2 UI files depending on backend APIs

[`web/src/app/page.tsx`](../web/src/app/page.tsx) depends on:

```text
POST http://localhost:8000/predict
```

Its request and response fields must remain compatible with [`api.py`](../api.py).

### 5.3 UI files without backend dependencies

- [`frontend/src/App.tsx`](../frontend/src/App.tsx)
- [`frontend/src/main.tsx`](../frontend/src/main.tsx)
- [`web/src/components/ui/button.tsx`](../web/src/components/ui/button.tsx)
- [`web/src/lib/utils.ts`](../web/src/lib/utils.ts)

### 5.4 Risky UI changes

The following must not be changed casually:

1. Input names: `N`, `P`, `K`, `temperature`, `humidity`, `ph`, and `rainfall`.
2. Input ranges and step sizes.
3. Streamlit DataFrame column order.
4. Prediction output names such as `predicted_crop` and `top1_prob`.
5. FastAPI request-body field names.
6. FastAPI response fields: `primary_recommendation`, `candidates`, and `meta`.
7. Model metadata fields: `num_qubits`, `reps`, and `C`.
8. Streamlit session-state keys.
9. CSS selectors tied to Streamlit internals.
10. The `models/` path and artifact-loading assumptions.

## 6. Unfinished UI work, in priority order

### Priority 1 — Choose one official UI

Select Streamlit, Next.js, or another single supported entry point. The Streamlit app is the most complete; the Next.js app is the strongest separate frontend prototype; the Vite app is currently only a starter.

### Priority 2 — Define and document the launch path

Document:

- The official UI command.
- Required backend process, if applicable.
- Required model artifacts.
- Required environment variables.
- Expected local ports.

### Priority 3 — Complete visible error handling

Especially in the Next.js dashboard:

- Check `response.ok`.
- Show an error panel.
- Add retry behavior.
- Validate response structure.
- Add timeout/cancellation behavior.

### Priority 4 — Align input contracts

Use one source of truth for:

- Feature names.
- Units.
- Minimums and maximums.
- Step sizes.
- Default values.

Current frontend/backend range differences include temperature and pH limits.

### Priority 5 — Remove or archive abandoned UI code

Decide the final status of:

- The Vite starter.
- `app.py.checkpoint`.
- `app.py.rich_ui`.
- `rewrite.py`.
- Unused starter assets.

### Priority 6 — Improve accessibility

Add:

- Explicit input labels.
- ARIA live regions for loading and results.
- Accessible error messages.
- Keyboard/focus testing.
- Screen-reader testing.
- Contrast verification.
- Non-color status indicators.

### Priority 7 — Establish a coherent design system

Standardize:

- Colors.
- Typography.
- Spacing.
- Border radius.
- Button states.
- Input states.
- Loading/error/empty states.
- Icons.
- Responsive breakpoints.

### Priority 8 — Make the Next.js frontend deployable

Replace the hardcoded API origin with an environment variable such as `NEXT_PUBLIC_API_BASE_URL`. Add environment-specific configuration and typed request/response models.

### Priority 9 — Run controlled UI validation

Run, where dependencies and the selected UI allow:

- Streamlit startup verification.
- Next.js development and production builds.
- Vite build or explicit retirement.
- Browser smoke tests.
- Mobile viewport checks.
- API failure checks.
- Model-unavailable checks.
- Accessibility checks.

These validations were not run during this read-only report.

### Priority 10 — Clarify user-facing claims

The UI should distinguish:

- Model predictions.
- SVM decision-score-derived confidence-like values.
- Static crop metadata.
- Agronomic advice.
- Quantum architecture information.
- Actual inference status.

The displayed confidence/probability values should not be presented as calibrated probabilities unless calibration is implemented and documented.

## Overall assessment

The Streamlit interface is the most complete UI in the repository. It provides a substantial visual dashboard and directly uses the crop prediction pipeline.

The Next.js interface is a functional prototype with real API integration, but it needs typed contracts, environment-based configuration, visible error handling, accessibility improvements, and deployment validation.

The Vite interface is still the default starter page and is not connected to the crop recommendation system.

The largest UI-level issue is architectural: the repository contains three competing UI directions with different frameworks, styling systems, and integration patterns. The next UI decision should be to select one official frontend and clearly archive or remove the alternatives.
