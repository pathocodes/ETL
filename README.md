# Berlin Neighborhood Infrastructure ETL
This repository contains the ETL (Extract, Transform, Load) pipelines and data modeling logic for Berlin's neighborhood infrastructure. The project focuses on utilizing geospatial data to build a robust database for urban analysis.

## Project Overview
As a Naturwissenschaftlerin specializing in Data Science, this project applies systematic data collection and cleaning methods to OpenStreetMap (OSM) data. The primary goal is to transform raw geospatial "points of interest" into structured, normalized datasets ready for localized urban planning insights.

## Repository Structure
- `post_offices/`: The core logic for processing Berlin's postal infrastructure.

  - `data-modelling.ipynb`: Initial data retrieval from OSM, Exploratory Data Analysis (EDA), and brand normalization logic.

  - `data-transformation.ipynb`: Geospatial processing, including coordinate extraction and joining data with Berlin's district boundaries

  - `post_offices_berlin_populating_db.py`: Final scripts for PostgreSQL database ingestion.

  - `data/`: Local storage for GeoJSON and raw data samples.

- `dags/`: Contains the orchestration skeletons.

Note: For the full production-grade Airflow implementation, environment configurations, and Docker orchestration, please refer to the dedicated Airflow-DAGs repository.

## Tech Stack
- **Language**: Python 3.x
- **Geospatial Analysis**: OSMnx, GeoPandas, Shapely.
- **Database**: PostgreSQL.
- **Data Modeling**: Jupyter Notebooks for iterative research and validation.

## Key Features
1. **Automated Extraction**: Programmatic retrieval of Berlin's infrastructure using OSM APIs.
2. **Brand Normalization**: Cleaning and mapping inconsistent "brand" names in OSM to a standardized format.
3. **Database Integration**: Seamless loading of geospatial objects into a relational database schema.

## Getting Started
1. Clone the repository:

```bash
git clone https://github.com/pathocodes/ETL.git
```

2. Install dependencies:

```bash
pip install osmnx geopandas sqlalchemy psycopg2
```
3. Explore the modeling process in `post_offices/data-modelling.ipynb`.
