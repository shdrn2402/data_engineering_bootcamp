import logging
from datetime import UTC, datetime
from pathlib import Path

import click

from utils import fetch_data, load_config, upload_to_s3

# Configure the root logger for the entire project
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--endpoint",
    type=click.Choice(
        ["fixtures", "teams", "players", "transfers"], case_sensitive=False
    ),
    default="fixtures",
    required=True,
    help="Choose the API endpoint to ingest data from. Options: fixtures, teams, players, transfers.",
)
@click.option(
    "--league",
    default=39,  # Default to English Premier League
    type=int,
    help="Specify the league ID for which to ingest data. Default is 39 (English Premier League).",
)
@click.option(
    "--season",
    default=2024,
    type=int,
    help="Specify the season year (format YYYY) for which to ingest data. Default is 2024.",
)
def ingest_data(endpoint: str, league: int, season: int) -> None:

    # Loading configuration and environment variables
    # Dynamically resolve the absolute path to the project root
    root_path = Path(__file__).resolve().parent.parent
    # Idiomatic path construction using the slash operator
    config_path = root_path / "configs" / "config.yaml"
    env_path = root_path / ".env"

    config = load_config(config_path, env_path)
    safe_config = {
        k: ("***" if "key" in k.lower() or "secret" in k.lower() else v)
        for k, v in config.items()
    }
    logger.info(f"Configuration successfully loaded: {safe_config}")

    # Retrieving a RAW data payload from the API
    url = config["api"]["base_url"] + config["api"]["endpoints"][endpoint]
    headers = {config["api"]["headers"]["key_name"]: config["api_football_key"]}
    timeout = (
        config["api"]["limits"]["timeout_connect"],
        config["api"]["limits"]["timeout_read"],
    )
    delay_seconds = config["api"]["limits"]["delay_seconds"]
    query_params = {"league": league, "season": season}

    raw_data = fetch_data(
        url=url,
        headers=headers,
        timeout=timeout,
        query_params=query_params,
        delay_seconds=delay_seconds,
    )
    logger.info(f"Data successfully fetched. Payload snippet: {str(raw_data)[:300]}...")

    # Uploading the RAW data to S3
    ingest_date = datetime.now(UTC).strftime("%Y-%m-%d")
    bucket_name = config["s3_bucket"]
    s3_key = f"raw/{endpoint}/league_id={league}/season={season}/ingest_date={ingest_date}/data.json"

    upload_to_s3(raw_data, bucket_name, s3_key)
    logger.info(
        f"Data successfully uploaded to S3 bucket '{bucket_name}' at '{s3_key}'."
    )


if __name__ == "__main__":
    ingest_data()
