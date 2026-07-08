# Premier League Data Pipeline

## Overview

Premier League Data Pipeline is an end-to-end ELT project that extracts English Premier League league, team, and match data from the API-Football API into PostgreSQL, transforms it using dbt (staging → marts), and visualises the results through Apache Superset dashboards covering team and league performance. Docker provides a reproducible execution environment for the ingestion pipeline, PostgreSQL, and dbt. Incremental loading prevents duplicate records and the ingestion pipeline includes comprehensive logging to support debugging and reliability

## Architrecture

![Project Architecture](docs/architecture.png)


The pipeline follows a layered ELT architecture:

1. **Source** – Football data is extracted from the API-Football REST API.
2. **Ingestion** – A containerised Python pipeline incrementally loads the data into PostgreSQL while preventing duplicate records.
3. **Storage & Transformation** – PostgreSQL stores both the raw ingestion tables and the transformed analytics tables. dbt standardises the raw data and handles duplicates through staging models before building analytics marts.
4. **Presentation** – Apache Superset connects to PostgreSQL to provide interactive dashboards for league and team performance using the analytics tables as the source data.

## Technologies

| Technology | Purpose |
| :--- | :--- |
| Python | Extracts data from API Football and loads it into PostgreSQL 
| PostgreSQL | Stores the raw ingestion and transformed analytics tables
| dbt | Cleans, standardises and transforms raw data into analytics-ready marts while performing data quality tests. |
| Apache Superset | Provides interactive dashboards for exploring Premier League analytics. |
| Docker | Containerizes the ingestion pipeline, PostgreSQL and dbt to provide a reproducible environment. |

## Project Structure

|  | |
| :--- | :---  |
| docs/ | Architecture diagram and screenshots |
| pl_dbt | dbt project | 
| scripts | Python ingestion pipeline |
| .env-struct | File that outlines the expected .env config file structure |
| compose.yaml | Defines and starts the local PostgreSQL, dbt, and ingestion containers |


## Features

### Data Ingestion

- Extracts Premier League data from the API-Football REST API.
- Incremental loading prevents duplicate league, team and match records.
- Containerised Python ingestion pipeline with comprehensive timestamped logging.

### Data Storage

- PostgreSQL stores both raw ingestion tables and transformed analytics models.
- Layered warehouse design separating raw, staging and mart tables.

### Data Transformation

- dbt staging models standardise and clean the raw data.
- dbt marts provide analytics-ready datasets for reporting.

### Data Visualisation

- Interactive Apache Superset dashboards for team and league performance.
- Cross-season filtering to compare Premier League seasons.

## Getting started

### Prerequisites

Before running the project, ensure you have the following: 
- Git
- Docker 
- Docker Compose
- An API FOOTBALL API key

### 1. Clone the repository

```bash
git clone https://github.com/syntax-ray/premier-league-data-pipeline.git
cd premier-league-data-pipeline
```

### 2. Configure the environment

Create two `.env` files using the provided templates.
One should be located at the project root while the other one in the pl_dbt directory.

Populate the required environment variables, including your API-Football API key and PostgreSQL credentials.

```bash
cp .env-struct .env
cp pl_dbt/.env-struct pl_dbt/.env
```

### 3. Start PostgreSQL

```bash
docker compose up postgres -d
```

Docker will automatically create the PostgreSQL container and persist the database using a local volume.

### 4. Run the ingestion pipeline

Execute the full ingestion pipeline.

```bash
docker compose run extractor
```

To run an individual stage instead:

```bash
docker compose run extractor python scripts/fetch_matches.py
```

### 5. Build the warehouse

Materialise the dbt models.

```bash
docker compose run dbt dbt run
```

Validate the models.

```bash
docker compose run dbt dbt test
```

### 6. Launch Apache Superset

The dashboards are visualised using Apache Superset. A companion repository containing the required Docker configuration is provided.

Clone the repository and switch to the `pl_superset` branch.

```bash
git clone https://github.com/syntax-ray/superset.git
cd superset
git checkout pl_superset
sudo docker compose -f docker-compose-image-tag.yml up -d
```

### 7. Import the Superset assets

The repository contains exported Superset assets for both the database connection and dashboards.

1. Open Apache Superset.
2. Navigate to **Settings → Import**.
3. Import `league_summary.zip` and `team_performance.zip` located in pl_dashboards/ subdirectory.
4. Open the imported database connection and verify the PostgreSQL hostname, port and credentials match your local environment.
5. Save the connection if any changes were required.

The Team Performance and League Summary dashboards will now be available and connected to the PostgreSQL warehouse.

## Dashboard Screenshots

### Team Performance Dashboard

![Team Performance Dashboard](docs/team_performance_dashboard.png)

The Team Performance Dashboard provides an interactive English Premier League league table across all available seasons.

**Features**
- Season filter for comparing different Premier League seasons.
- Complete league standings.
- Team position and points.
- Matches played.
- Wins, draws and losses.
- Goals scored and goals conceded.
- Goal difference.
- Win percentage.

---

### League Summary Dashboard

![League Summmary Dashboard](docs/league_summary_dashboard.png)

The League Summary Dashboard provides season-level analytics across the available Premier League seasons.

**Features**
- Season filter for comparing league statistics across seasons.
- Total matches played.
- Total goals scored.
- Average goals per match.
- Home win percentage.
- Away win percentage.
- Draw percentage.

## Future Improvements

- Deploy the data platform to AWS.
- Integrate additional football data sources to enrich the analytics layer.
- Introduce workflow orchestration for automated pipeline execution.
- Implement CI/CD for automated testing and deployment.
