# Data-Project
1. The Hero Project: UK Public Legal Data Pipeline & Explorer
Build a mini end-to-end pipeline using actual UK court or public data.

Data Source: Use the National Archives Find Case Law API (free, public access to UK court judgments) or Companies House API.

What to Build:

Ingestion Script: A Python script or scraper that pulls judgments (e.g., all 2025/2026 High Court or Employment Tribunal decisions in a specific category).

Data Transformation & Database: Parse the raw XML/HTML, extract key metadata (case name, neutral citation, judge, court, date, parties), and store it in a lightweight SQLite or PostgreSQL database.

Lightweight Web UI: A simple search/filter interface using Streamlit, FastAPI + vanilla HTML/CSS, or Next.js that lets users filter cases by judge, date, or keyword.

Why it wins: It proves full-stack literacy—backend, database, and UI—directly within Assize Data's business domain.
