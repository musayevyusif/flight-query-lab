"""Row validation: airport list loading, single-row checks, record building."""


import math
import re
from datetime import datetime


def load_airports(path: str) -> set[str]:
    airports = set()

    with open(path, encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if code and not code.startswith("#"):
                airports.add(code)

    return airports



def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:  ##Checking if the row has exactly 6 fields
        return "WRONG_FIELD_COUNT"

    fields = [field.strip() for field in fields]


    

    if any(field == "" for field in fields): ### CheckIf any field is empty
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price = fields





    if re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id) is None: ####Checking ifd the flight id is 2–8 ascii letters and  digits
        return "INVALID_FLIGHT_ID"




    if re.fullmatch(r"[A-Z]{3}", origin) is None or origin not in airports: ##Checking if origin is 3 uppercase ascii letters and is in airport set
        return "INVALID_ORIGIN"

    if (re.fullmatch(r"[A-Z]{3}", destination) is None or destination not in airports ## Same as origfin
    ):
        return "INVALID_DESTINATION" 




    if origin == destination: ##    Check if origin and destination is different
        return "SAME_ORIGIN_DESTINATION"

    date_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"



## contidions for times. 

    if re.fullmatch(date_pattern, departure) is None: #Check if departure time is real date and time in corrwect format
        return "INVALID_DEPARTURE"

    try:
        departure_time = datetime.strptime(departure, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_DEPARTURE"

    if re.fullmatch(date_pattern, arrival) is None:
        return "INVALID_ARRIVAL"

    try:
        arrival_time = datetime.strptime(arrival, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_ARRIVAL"

    if arrival_time <= departure_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_value = float(price)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price_value):
        return "INVALID_PRICE"

    if price_value <= 0:
        return "NON_POSITIVE_PRICE"






    return None




def to_record(fields: list[str]) -> dict:
    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5]),
    }
