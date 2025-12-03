"""Script to add unique identifiers to JSON data items.

This script reads a JSON file, adds an 'idx' field to each item based
on its 'question_id', and writes the updated data back to the same file.
"""

from argparse import ArgumentParser

from src.utils.json_io import read_json_raw, write_json_raw


def main(file: str) -> None:
    """Add unique identifiers to items in a JSON file.

    Parameters
    ----------
    file : str
        Path to the JSON file to process.
    """
    data = read_json_raw(file)
    for item in data:
        if "idx" in item:
            continue
        item["idx"] = f"bird_{item['question_id']}"
    write_json_raw(file, data)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-f", type=str, required=True)
    args = arg_parser.parse_args()
    main(args.f)
