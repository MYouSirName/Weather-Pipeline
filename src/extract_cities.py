"""
Filters the full OpenWeatherMap city list down to US cities and keeps only
the fields the pipeline actually needs (name + coordinates).

Input:  city.list.json      (full city list, downloaded separately - see README)
Output: city_final_list.json
"""

import json

INPUT_PATH = "city.list.json"
OUTPUT_PATH = "city_final_list.json"


def main() -> None:
    with open(INPUT_PATH, "r", encoding="utf-8") as read_file:
        cities = json.load(read_file)

    us_cities = [city for city in cities if city["country"] == "US"]

    final_list = [
        {
            "name": city["name"],
            "coord": {
                "lon": city["coord"]["lon"],
                "lat": city["coord"]["lat"],
            },
        }
        for city in us_cities
    ]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as write_file:
        json.dump(final_list, write_file, indent=4, ensure_ascii=False)

    print(f"Wrote {len(final_list)} US cities to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
