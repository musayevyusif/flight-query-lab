"""Running queries against the flight database."""

import math
import re
from datetime import datetime

def run_query(db: list[dict], query: dict) -> dict:
    response = {"query": query, "matches": []}

    if not isinstance(query, dict):
        response["error"] = "INVALID_QUERY"
        return response

    record_keys = (
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price",
    )

    allowed_keys = set(record_keys) | {
        "min_price", "sort_by", "order", "limit"
    }

    invalid = False

    for key, value in query.items():
        if key not in allowed_keys:
            invalid = True
            break

        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                invalid = True

        elif key in ("departure_datetime", "arrival_datetime"):
            pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"

            if not isinstance(value, str):
                invalid = True
            elif re.fullmatch(pattern, value) is None:
                invalid = True
            else:
                try:
                    datetime.strptime(value, "%Y-%m-%d %H:%M")
                except ValueError:
                    invalid = True

        elif key in ("price", "min_price"):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                invalid = True
            elif isinstance(value, float) and not math.isfinite(value):
                invalid = True

        elif key == "sort_by":
            if not isinstance(value, str) or value not in record_keys:
                invalid = True

        elif key == "order":
            if value not in ("asc", "desc"):
                invalid = True

        elif key == "limit":
            if type(value) is not int or value < 0:
                invalid = True

        if invalid:
            break

    if "order" in query and "sort_by" not in query:
        invalid = True

    if invalid:
        response["error"] = "INVALID_QUERY"
        return response

    matches = []

    for flight in db:
        match = True

        for key, value in query.items():
            if key in ("flight_id", "origin", "destination"):
                if flight[key] != value:
                    match = False

            elif key == "departure_datetime":
                if flight[key] < value:
                    match = False

            elif key == "arrival_datetime":
                if flight[key] > value:
                    match = False

            elif key == "price":
                if flight["price"] > value:
                    match = False

            elif key == "min_price":
                if flight["price"] < value:
                    match = False

            if not match:
                break

        if match:
            matches.append(flight)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[sort_key],
            reverse=descending,
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    response["matches"] = matches
    return response



def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]