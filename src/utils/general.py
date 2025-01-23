"""Utility functions for general use in the data processing workflow."""
from pathlib import Path
import pandas as pd
import yaml
# pylint: disable=W0703, W0719


def read_yaml(file_path: Path) -> dict:
    """Read yaml files for general use.

    Args:
        file_path (Path): file path of yaml to read

    Raises:
        PermissionError: Raised if function does not have permission to access file
        IOError: Raised if file cannot be read
        Exception: General exception just in case

    Returns:
        dict: dictionary with yaml information or None if error occurs
        str: Logged information in form of Exception or string
    """
    try:
        with open(
            file=file_path,
            mode='r',
            encoding="utf-8"
        ) as file:
            yaml_dict = yaml.safe_load(file)
    except PermissionError as pe:
        raise PermissionError('Try closing out the file you are trying to read') from pe
    except IOError as io:
        raise IOError("Trouble reading yaml file") from io
    except Exception as e:
        raise Exception("An unknown error has occured") from e

    return yaml_dict


def read_csv(file_path: Path) -> pd.DataFrame:
    """Read csv files for general use.

    Args:
        file_path (Path): file path of csv to read

    Raises:
        PermissionError: Raised if function does not have permission to access file
        IOError: Raised if file cannot be read
        Exception: General exception just in case

    Returns:
        pd.DataFrame: DataFrame of read csv file
    """
    try:
        df = pd.read_csv(
            file_path,
            encoding='utf-8'
        )
    except PermissionError as pe:
        raise PermissionError('Try closing out the file you are trying to read') from pe
    except IOError as io:
        raise IOError("Trouble reading csv file") from io
    except Exception as e:
        raise Exception("An unknown error has occured") from e

    return df


def read_excel(file_path: Path) -> pd.DataFrame:
    """Read excel files for general use.

    Args:
        file_path (Path): file path of excel to read

    Raises:
        PermissionError: Raised if function does not have permission to access file
        IOError: Raised if file cannot be read
        Exception: General exception just in case

    Returns:
        pd.DataFrame: DataFrame of read excel file
    """
    try:
        df = pd.read_excel(
            file_path,
        )
    except PermissionError as pe:
        raise PermissionError('Try closing out the file you are trying to read') from pe
    except IOError as io:
        raise IOError("Trouble reading excel file") from io
    except Exception as e:
        raise Exception("An unknown error has occured") from e

    return df


def write_to_csv(df: pd.DataFrame, write_directory: Path,
                 file_name: str):
    """Write to csv for general use.

    This function allows you to name the file based on the name of the firm as well as a file suffix
    to be appended to the end of the file name.

    Args:
        df (pd.DataFrame): DataFrame to write to csv
        write_directory (Path): Path location to write csv to
        file_suffix (str): Any additional information to append to the end of the file name

    Raises:
        PermissionError: Raised if function does not have permission to access file
        IOError: Raised if file cannot be written
        Exception: General exception just in case

    """
    try:
        df.to_csv(
            write_directory.joinpath(
                f'{file_name}.csv'
            )
        )
    except PermissionError as pe:
        raise PermissionError('Try closing out the file you are trying to read') from pe
    except IOError as io:
        raise IOError("Trouble writing csv file") from io
    except Exception as e:
        raise Exception("An unknown error has occured") from e


def write_to_pickle(df: pd.DataFrame, write_directory: Path,
                    file_name: str):
    """Write to pickle for general use.

    This function allows you to name the file based on the name of the firm as well as a file suffix
    to be appended to the end of the file name.

    Args:
        df (pd.DataFrame): DataFrame to write to pickle
        write_directory (Path): Path location to write pickle to
        file_suffix (str): Any additional information to append to the end of the file name

    Raises:
        PermissionError: Raised if function does not have permission to access file
        IOError: Raised if file cannot be written
        Exception: General exception just in case

    """
    try:
        df.to_pickle(
            write_directory.joinpath(
                f'{file_name}.pkl'
            )
        )
    except PermissionError as pe:
        raise PermissionError('Try closing out the file you are trying to read') from pe
    except IOError as io:
        raise IOError("Trouble writing pickle file") from io
    except Exception as e:
        raise Exception("An unknown error has occured") from e
