import click
import json
import logging

from pathlib import Path
from utils import load_config, fetch_data, save_json

# Configure the root logger for the entire project
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--endpoint", 
    type=click.Choice(["fixtures", "teams", "players", "statistics"], case_sensitive=False), 
    default="fixtures",
    required=True,
    help="Choose the API endpoint to ingest data from. Options: fixtures, teams, players, statistics."
)
@click.option(
    "--league",
    default=39,  # Default to English Premier League
    type=int, 
    help="Specify the league ID for which to ingest data. Default is 39 (English Premier League)."
)
@click.option(
    "--season",
    default=2024,
    type=int, 
    help="Specify the season year (format YYYY) for which to ingest data. Default is 2024."
)

def ingest_data(endpoint: str, league: int, season: int) -> None:
    # Dynamically resolve the absolute path to the project root
    root_path = Path(__file__).resolve().parent.parent
    # Idiomatic path construction using the slash operator
    config_path = root_path / "configs" / "config.yaml"
    env_path = root_path / ".env"

    config = load_config(config_path, env_path)
    logger.info(f"Configuration successfully loaded: {config}")

    url = config["api"]["base_url"] + config["api"]["endpoints"][endpoint]
    headers = {
        config["api"]["headers"]["key_name"]: config["api_football_key"]
    }
    timeout = (
        config["api"]["limits"]["timeout_connect"],
        config["api"]["limits"]["timeout_read"]
    )
    query_params = {
        "league": league,
        "season": season
        }

    raw_data = fetch_data(url=url, headers=headers, timeout=timeout, query_params=query_params)
    logger.info(f"Data successfully fetched. Payload snippet: {str(raw_data)[:300]}...")

    raw_dir = root_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{endpoint}_{league}_{season}.json"
    filepath = raw_dir / filename

    save_json(raw_data, filepath)
    
    logger.info(f"Raw data successfully saved to {filepath}")

if __name__ == "__main__":
    ingest_data()