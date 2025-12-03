"""Execution Accuracy failure analysis utilities.

This module provides tools for analyzing failed test cases by comparing
JSON result files and extracting SQL query details for further investigation.
"""

from typing import Any, Dict

from src.utils.json_io import read_json_raw, write_json_raw


def finder(path1: str, path2: str) -> list[Any]:
    """Find differences between two JSON files and write results.

    Parameters
    ----------
    path1 : str
        Path to the first JSON file (full dataset).
    path2 : str
        Path to the second JSON file (category dataset).

    Returns
    -------
    list
        Items present in path1 but not in path2.
    """
    full: list[Dict] = read_json_raw(path1)
    category: list[Dict] = read_json_raw(path2)
    diff = []
    for items in full:
        if items not in category:
            diff.append(items)
    write_json_raw("data/EA_diff", diff)

    for items in category:
        if items not in full:
            print(items)
    return diff


def analyser(arr: list[Any]) -> None:
    """Analyze failure cases and extract SQL details.

    Parameters
    ----------
    arr : list
        List of question IDs to analyze.
    """
    path = "data/full/19_RepairSQL.json"
    file = read_json_raw(path)
    res = []
    for items in arr:
        for records in file:
            if records["question_id"] == items:
                res.append(
                    {
                        "id": records["question_id"],
                        "question": records["question"],
                        "gold": records["SQL"],
                        "pred": records["pred_sql"],
                    }
                )

    write_json_raw("data/EA_sql_diff", res)


def main() -> None:
    """Run the EA failure analysis workflow."""
    path1 = "data/full/EA_failures.json"
    path2 = "data/category/EA_failures.json"

    res = finder(path1, path2)
    analyser(res)


if __name__ == "__main__":
    main()
