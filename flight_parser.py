"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB135"
FIRST_NAME = "Yusif"
LAST_NAME = "Musayev"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate flight CSV files and run flight queries."
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    args = parser.parse_args(argv)

    if (args.i is not None or args.d is not None) and args.a is None:
        parser.error("-a is required with -i or -d")

    if args.j is not None and args.o is not None:
        parser.error("-o cannot be used with -j")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        if args.j is not None:
            with open(args.j, encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list):
                raise ValueError("Database must be an array of objects")

            if not all(isinstance(record, dict) for record in db):
                raise ValueError("Database must be an array of objects")

        else:
            airports = load_airports(args.a)

            if args.i is not None:
                paths = [args.i]
            else:
                folder = Path(args.d)

                if not folder.is_dir():
                    raise ValueError("Input folder does not exist")

                paths = [
                    str(path)
                    for path in sorted(folder.iterdir())
                    if path.is_file() and path.name.endswith(".csv")
                ]

                if not paths:
                    raise ValueError("Input folder contains no CSV files")

            output_path = Path(args.o if args.o is not None else "db.json")
            log_path = output_path.parent / "errors.log"

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(handler)

            db, errors = parse_files(paths, airports)

            for message in errors:
                logger.warning(message)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

        if args.q is not None:
            with open(args.q, encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, (dict, list)):
                raise ValueError("Queries must be an object or an array")

            if isinstance(queries, list):
                if not all(isinstance(query, dict) for query in queries):
                    raise ValueError("Query array must contain objects")

            responses = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_"
                f"{timestamp}.json"
            )
            response_path = Path(args.r) / filename

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2)

        return 0

    except (OSError, ValueError, UnicodeError) as error:
        message = " ".join(str(error).splitlines())
        print(f"Error: {message}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
