# Weather Data Pipeline

Python pipeline that collects real-time weather data for U.S. cities via [OpenWeatherMap](https://openweathermap.org/api) and loads the raw JSON data into a Snowflake table for downstream analysis.

## Architecture
```
city.list.json (OpenWeatherMap's global city list)
│
▼
extract_cities.py ──► city_final_list.json (U.S. cities only: name + coordinates)
│
▼
weather_API_script.py
│ for each city:
│ 1. calls the OpenWeatherMap API
│ 2. inserts the raw JSON into the RAW.raw_weather table (Snowflake)
▼
Snowflake (WEATHER_DB.RAW.raw_weather)
```

`find_country.py` is a small helper script used while exploring the dataset early on (not part of the main pipeline).

A sample API response is available at [`sample_output/weather_data_sample.json`](sample_output/weather_data_sample.json).

## Stack

- Python 3
- [requests](https://pypi.org/project/requests/) — OpenWeatherMap API calls
- [snowflake-connector-python](https://pypi.org/project/snowflake-connector-python/) — Snowflake loading
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variables

## Project structure

weather-pipeline/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── sample_output/
│ └── weather_data_sample.json
└── src/
├── extract_cities.py
├── find_country.py
└── weather_API_script.py


## Setup

1. Clone the repository and create a virtual environment:

```bash
   git clone https://github.com/<your-username>/weather-pipeline.git
   cd weather-pipeline
   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your credentials (never commit `.env`):

```bash
   copy .env.example .env      # Windows
```

   | Variable | Description |
   |---|---|
   | `API_KEY` | OpenWeatherMap API key |
   | `SNOWFLAKE_USER` | Snowflake username |
   | `SNOWFLAKE_PASSWORD` | Snowflake password |
   | `SNOWFLAKE_ACCOUNT` | Snowflake account identifier |
   | `SNOWFLAKE_WAREHOUSE` | Warehouse to use |
   | `SNOWFLAKE_DATABASE` | Target database |
   | `SNOWFLAKE_SCHEMA` | Target schema |
   | `SNOWFLAKE_ROLE` | Role used for the connection |

3. Download the full city dataset ([`city.list.json`](https://openweathermap.org/current#cityid) from OpenWeatherMap) and place it at the project root.

4. Create the destination table in Snowflake:

```sql
   CREATE TABLE IF NOT EXISTS raw_weather (
       raw_data VARIANT
   );
```

## Usage

```bash
python src/extract_cities.py      # generates city_final_list.json
python src/weather_API_script.py  # fetches weather data and loads it into Snowflake
```

## Future improvements

- Automated tests for the extraction and transformation functions
- Scheduling via cron / GitHub Actions / Airflow for periodic runs
- A transformation layer (e.g., dbt) on top of the raw data in Snowflake
- Exponential backoff retries on API calls
