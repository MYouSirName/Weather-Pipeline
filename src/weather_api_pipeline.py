"""
This is the final result after using Claude to polish my code

Weather API -> Snowflake pipeline.

For every US city in city_final_list.json, fetches current weather data from
the OpenWeatherMap API and loads the raw JSON response into a Snowflake table.

Required environment variables (see .env.example):
    API_KEY
    SNOWFLAKE_USER
    SNOWFLAKE_PASSWORD
    SNOWFLAKE_ACCOUNT
    SNOWFLAKE_WAREHOUSE
    SNOWFLAKE_DATABASE
    SNOWFLAKE_SCHEMA
    SNOWFLAKE_ROLE
"""

import json
import logging
import os
import time

import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
CITY_LIST_PATH = "city_final_list.json"

API_KEY = os.getenv("API_KEY")
SNOWFLAKE_CONFIG = {
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}


def load_cities(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as read_file:
        return json.load(read_file)


def connect_snowflake():
    return snowflake.connector.connect(
        autocommit=True,
        **SNOWFLAKE_CONFIG,
    )


def fetch_weather(city: dict) -> dict | None:
    query_params = {
        "appid": API_KEY,
        "lat": city["coord"]["lat"],
        "lon": city["coord"]["lon"],
        "units": "metric",
        "lang": "en",
    }
    headers = {
        "User-Agent": "weather-pipeline",
        "Accept": "application/json",
    }

    response = requests.get(
        OPENWEATHER_URL,
        params=query_params,
        headers=headers,
        timeout=5,
    )

    if response.status_code == 429:
        logger.warning("Rate limited, sleeping before retry.")
        time.sleep(10)
        return None

    response.raise_for_status()
    return response.json()


def main() -> None:
    if not API_KEY:
        raise RuntimeError("API_KEY is not set. Did you create a .env file from .env.example?")
    if not all(SNOWFLAKE_CONFIG.values()):
        raise RuntimeError("Missing Snowflake credentials. Check your .env file.")

    cities = load_cities(CITY_LIST_PATH)

    conn = connect_snowflake()
    cursor = conn.cursor()

    try:
        for city in cities:
            city_name = city.get("name", "Unknown city")
            logger.info("Fetching weather for %s", city_name)

            try:
                data = fetch_weather(city)
            except requests.exceptions.RequestException:
                logger.exception("Request failed for %s", city_name)
                continue

            if not data:
                continue

            try:
                cursor.execute(
                    "INSERT INTO raw_weather (raw_data) SELECT PARSE_JSON(%s)",
                    (json.dumps(data),),
                )
                logger.info("Saved %s into Snowflake.", city_name)
            except snowflake.connector.errors.Error:
                logger.exception("Snowflake insert failed for %s", city_name)

            time.sleep(1.1)
    finally:
        cursor.close()
        conn.close()

    logger.info("Pipeline run completed.")


if __name__ == "__main__":
    main()
