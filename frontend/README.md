# Civ-AI Frontend: Smart Road Intelligence Dashboard

This is the frontend for the **Civ-AI** system, a modern, glassmorphic dashboard built with Next.js to visualize road infrastructure intelligence.

## 🚀 Features

- **Pothole Analysis Dashboard**: real-time visualization of detection results.
- **Unified Media Upload**: Seamlessly upload images and videos for processing.
- **Interactive Reports**: Downloadable PDF reports with repair estimations.
- **Dark Mode UI**: Professional fintech-inspired aesthetic with Framer Motion animations.

## 🛠 Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **API Client**: Axios
- **State Management**: React Hooks

## 🏁 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Ensure the backend is running at `http://localhost:8000`. You can configure the API base URL in `services/api.ts`.

### 3. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the dashboard.

## 📁 Structure

- `app/`: Next.js App Router pages and layouts.
- `components/`: UI components (Cards, Stats, Uploaders).
- `services/`: API integration services.
- `public/`: Static assets and icons.

## 📖 Learn More

To learn more about the Civ-AI backend and the underlying YOLOv8 model, refer to the root [README](../README.md).

