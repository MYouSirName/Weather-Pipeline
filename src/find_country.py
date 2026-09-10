"""
Small lookup helper used while exploring city.list.json - prints the country
code for a given city name.
"""

import json

INPUT_PATH = "city.list.json"
CITY_NAME = "Los Angeles"


def main() -> None:
    with open(INPUT_PATH, "r", encoding="utf-8") as read_file:
        cities = json.load(read_file)

    for city in cities:
        if city["name"] == CITY_NAME:
            print(city["country"])
            return

    print(f"{CITY_NAME} not found.")


if __name__ == "__main__":
    main()
