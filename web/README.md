# Quantum Crop Intelligence UI

This is the Next.js frontend for the Quantum ML Crop Recommendation system.

## Setup

```bash
cd web
npm install
```

## Development

```bash
npm run dev
```

The app will start at [http://localhost:3000](http://localhost:3000).

## Environment Variables

Create a `.env` in the `web/` directory with:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
This points to the legacy python backend. Ensure the backend is running before testing the frontend.

## Build

```bash
npm run build
npm start
```
