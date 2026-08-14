import json
import logging
import os
from pathlib import Path

import boto3
import botocore.exceptions
import requests
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_config(config_path: str | Path, env_path: str | Path) -> dict:
    """Loads YAML configuration and injects environment variables.

    Args:
        config_path (str): Path to the config.yaml file.
        env_path (str): Path to the .env file.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the YAML file is malformed.

    Returns:
        dict: Parsed configuration data.
    """
    # Silently ignores if .env is missing (expected in Docker/cloud)
    load_dotenv(env_path)
    config_path = Path(config_path)

    try:
        config = yaml.safe_load(config_path.read_text())
        config["api_football_key"] = os.environ["API_FOOTBALL_KEY"]
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise
    except PermissionError as e:
        logger.error(f"Permission denied when accessing the configuration file: {e}")
        raise

    return config


def fetch_data(
    url: str, headers: dict, timeout: tuple, query_params: dict | None = None
) -> dict:
    """Executes a GET request to the API with rate limiting constraints.

    Args:
        url (str): The endpoint URL.
        headers (dict): Request headers containing authentication tokens.
        timeout (tuple): Connection and read timeouts (connect, read).
        query_params (dict | None, optional): Query string parameters. Defaults to None.

    Raises:
        requests.exceptions.HTTPError: If the HTTP request returns an unsuccessful status code (e.g., 401, 429, 500).
        requests.exceptions.RequestException: For underlying network issues.
        ValueError: If the API response contains business logic errors despite a 200 OK status.

    Returns:
        dict: JSON payload from the API response.
    """
    try:
        response = requests.get(
            url, headers=headers, params=query_params, timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errors"):
            raise ValueError(f"API returned errors: {data['errors']}")
        return data

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred during request to {url}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error occurred during request to {url}: {e}")
        raise


def save_json(data: dict | list, output_path: str) -> None:
    """Saves data as a JSON file, creating parent directories if necessary.

    Args:
        data (dict | list): The payload to save.
        output_path (str): The target file path.

    Raises:
        OSError: If directory creation or file writing fails.
        TypeError: If the data object is not JSON serializable.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except OSError as e:
        logger.error(f"Failed to write JSON to {output_path}: {e}")
        raise


def upload_to_s3(raw_data: dict, bucket: str, s3_key: str) -> None:
    """Uploads a dictionary as a JSON object to an AWS S3 bucket.

    Args:
        raw_data (dict): The payload to serialize and upload.
        bucket (str): The name of the target S3 bucket.
        s3_key (str): The destination key (path) in the S3 bucket.

    Raises:
        botocore.exceptions.ClientError: If the AWS S3 put_object operation fails.
        TypeError: If the data object is not JSON serializable.
    """
    s3 = boto3.resource("s3")
    raw_data_json = json.dumps(raw_data, ensure_ascii=False, indent=4)
    try:
        s3.Bucket(bucket).put_object(Key=s3_key, Body=raw_data_json)
    except botocore.exceptions.ClientError as e:
        logger.error(
            f"Failed to upload data to S3 bucket '{bucket}' at '{s3_key}': {e}"
        )
        raise
    except botocore.exceptions.ParamValidationError as e:
        logger.error(
            f"Parameter validation error during S3 upload to bucket '{bucket}' at '{s3_key}': {e}"
        )
        raise
