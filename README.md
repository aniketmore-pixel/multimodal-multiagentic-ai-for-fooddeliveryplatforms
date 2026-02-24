# CustomerPulse AI | Multi-Modal Multi-Agentic AI Framework for Customer Satisfaction Assessment on Food Delivery Platforms

## Overview

This project presents a distributed, multi-modal, multi-agent AI
framework designed to assess and predict customer satisfaction on a
food delivery platform in real time.

The system integrates transformer-based NLP models, tabular machine
learning models, real-time telemetry pipelines, and interactive
dashboards into a unified AI ecosystem.

------------------------------------------------------------------------

## How to run this project?
We've provided a batch file to run every agent, there are 5 batch files in total,
one for every agent and one for the unified dashboard.

------------------------------------------------------------------------

## Screenshots
<img width="1920" height="1080" alt="Screenshot (222)" src="https://github.com/user-attachments/assets/8f340fd0-a5f3-4c92-a340-166ec839e9ac" />
<img width="1920" height="1080" alt="Screenshot (219)" src="https://github.com/user-attachments/assets/ec035315-1373-4e61-af63-808cdcc14611" />
<img width="1920" height="1080" alt="Screenshot (221)" src="https://github.com/user-attachments/assets/e521ea02-5034-454d-ad46-618e42154f53" />
<img width="1920" height="1080" alt="Screenshot (224)" src="https://github.com/user-attachments/assets/c6d33094-0120-4468-8d4a-773d15e729ea" />
<img width="1920" height="1080" alt="Screenshot (223)" src="https://github.com/user-attachments/assets/efdc70f3-7ea9-42ce-9c6e-b93eb515ace2" />

------------------------------------------------------------------------

## System Architecture

The framework consists of multiple intelligent agents:

### 1. UX Agent (DistilBERT-based ANN)

-   Analyzes behavioral logs, session activity, and textual signals
-   Produces a continuous UX score (0--10)
-   Maintains historical session telemetry
-   Exposed via FastAPI

### 2. Food Quality Agent (DistilBERT Regression Model)

-   Trained on Amazon + Yelp datasets (80K+ reviews)
-   Outputs normalized food quality score (0--1)
-   Integrated with Redis stream pipeline
-   Real-time dashboard monitoring

### 3. Delivery KPI Agent

-   Computes operational performance metrics
-   Orders processed
-   Average delivery score
-   Critical alerts
-   Holistic delivery index

### 4. Churn Intelligence Agent (RandomForestRegressor)

-   Aggregates cross-agent metrics
-   Predicts churn percentage (0--100%)
-   Maintains rolling historical telemetry
-   Provides explainable feature importance

### 5. Mission Control Dashboard

-   Real-time system-wide observability
-   Cross-agent analytics
-   Trend visualization
-   Predictive alerting

------------------------------------------------------------------------

## Multi-Modal Design

The framework integrates:

-   Textual data (Transformer-based NLP models)
-   Structured numerical metrics
-   Behavioral session analytics
-   Operational delivery KPIs
-   Real-time streaming data (Redis)

This enables comprehensive customer satisfaction assessment.

------------------------------------------------------------------------

## Technology Stack

### Backend

-   Python
-   FastAPI
-   Flask
-   PyTorch
-   HuggingFace Transformers
-   Scikit-learn
-   Redis

### Machine Learning

-   DistilBERT (Regression & ANN architectures)
-   RandomForestRegressor
-   MSE / MAE evaluation metrics

### Frontend

-   Tailwind CSS
-   Chart.js
-   Streamlit Dashboards

------------------------------------------------------------------------

## Key Features

-   Real-time cross-agent metric aggregation
-   Continuous satisfaction scoring
-   Predictive churn modeling
-   Explainable AI insights
-   Automated alert triggering (SMS/WhatsApp ready)
-   Redis-based streaming architecture
-   Rolling telemetry history tracking

------------------------------------------------------------------------

## Data Flow

Review Generator → Redis Stream → Food Quality Model → Holistic Index\
UX Agent + Delivery Agent → Feature Engineering → Churn Model\
All Agents → Mission Control Dashboard → Alert System

------------------------------------------------------------------------

## Model Training Summary

### Food Quality Model

-   Dataset: Amazon Polarity + Yelp Review Full
-   Normalized to 0--1 regression scale
-   Model: DistilBERT (num_labels=1)
-   Loss: Mean Squared Error

### Churn Model

-   Model: RandomForestRegressor
-   Target: Churn Percentage (0--100)
-   Evaluation: MAE, R²
-   Feature importance supported

------------------------------------------------------------------------

## Project Highlights

-   Distributed AI agent architecture
-   Multi-model ecosystem
-   Real-time monitoring & prediction
-   Microservice-based deployment design
-   Production-ready pipeline structure

------------------------------------------------------------------------

## Potential Extensions

-   ONNX optimization for faster inference
-   Kubernetes deployment
-   Temporal churn modeling
-   Reinforcement learning-based dynamic interventions
-   A/B testing integration

------------------------------------------------------------------------

## Authors

Aniket More,
Aarya Arban,
Digvijaysingh Rajput,
Vamshi Marri

