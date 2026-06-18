"""Serialize and deserialize a list of fasting values.

Uses .csv files in CFG_DATAFILE_PREFIX to read from and write into.
"""

import csv
import logging
import os
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Get cache directory from environment or use default
BGCHOF_CFG_CFG_DATAFILE_PREFIX = Path(
    os.environ.get("BGCHOF_CFG_CFG_DATAFILE_PREFIX", "./.bgchofcache/")
)
CFG_DATAFILE_MODE = 0o777


def read_fasting_list(input_year: int) -> list[int] | None:
    """Load contents of .csv cache file into a list.

    Args:
        input_year: int representing the year for which to load the cache file.

    Returns:
        A list of status values (as integers) for each day of the year,
        or None if the cache file doesn't exist.

    Raises:
        FileNotFoundError: if cache file doesn't exist. Returns None instead.
    """
    fasting_list: list[int] = []
    file_path = BGCHOF_CFG_CFG_DATAFILE_PREFIX / f"{input_year}.csv"

    try:
        with file_path.open(mode="r", encoding="utf-8") as fasting_list_file:
            file_reader = csv.reader(fasting_list_file, delimiter=",")
            next(file_reader, None)  # skip headers
            for row in file_reader:
                fasting_list.append(int(row[1]))
            logger.info(f"Loaded fasting data for year {input_year} from cache")
            return fasting_list
    except FileNotFoundError:
        logger.info(
            f"Can't find the data file for year {input_year}. Creating new one..."
        )
        sys.stderr.write(
            f"Can't find the data file for year {input_year}. Creating new one...\n"
        )
        return None


def write_fasting_list(input_year: int, input_list: list[int]) -> bool:
    """Dump a year's worth of fasting statuses into a .csv cache file.

    Args:
        input_year: An int representing the year for which the status values apply.
        input_list: A list of status values (0..6) for each day of the year.

    Returns:
        True if serialization was successful.

    Raises:
        OSError: If cache directory can't be created.
        PermissionError: If insufficient permissions to create directory or file.
        IOError: If cache file can't be created.
    """
    # Create the cache directory if it doesn't exist
    try:
        BGCHOF_CFG_CFG_DATAFILE_PREFIX.mkdir(
            mode=CFG_DATAFILE_MODE, parents=True, exist_ok=True
        )
        logger.debug(f"Cache directory ensured: {BGCHOF_CFG_CFG_DATAFILE_PREFIX}")
    except OSError as e:
        error_msg = f"Can't create the cache directory: {e}"
        logger.error(error_msg)
        sys.stderr.write(f"{error_msg}\n")
        raise

    file_path = BGCHOF_CFG_CFG_DATAFILE_PREFIX / f"{input_year}.csv"

    try:
        with file_path.open(mode="w", encoding="utf-8", newline="") as fasting_list_file:
            file_writer = csv.writer(fasting_list_file, delimiter=",")
            file_writer.writerow(["dayNumber", "Status"])
            for n, status in enumerate(input_list, start=1):
                file_writer.writerow([n, status])
        logger.info(f"Successfully wrote fasting data for year {input_year} to cache")
        return True
    except OSError as e:
        error_msg = f"Can't create data file for year {input_year}: {e}"
        logger.error(error_msg)
        sys.stderr.write(f"{error_msg}\n")
        raise


def clear_cache(year: int) -> bool:
    """Clear cache file for a specific year.
    
    Args:
        year: Year for which to clear the cache file.
    
    Returns:
        True if file was deleted, False if file didn't exist.
    
    Raises:
        PermissionError: If insufficient permissions to delete file.
        OSError: If deletion fails for other reasons.
    
    Examples:
        >>> clear_cache(2023)  # Clear cache for 2023
        True
        >>> clear_cache(2024)  # Try to clear non-existent cache
        False
    """
    file_path = BGCHOF_CFG_CFG_DATAFILE_PREFIX / f"{year}.csv"
    
    if not file_path.exists():
        logger.warning(f"Cache file for year {year} does not exist")
        return False
    
    try:
        file_path.unlink()
        logger.info(f"Successfully cleared cache for year {year}")
        return True
    except OSError as e:
        error_msg = f"Failed to clear cache for year {year}: {e}"
        logger.error(error_msg)
        sys.stderr.write(f"{error_msg}\n")
        raise
