import json
from pathlib import Path
from typing import Any


def load_config(workspace_path: str | Path) -> dict[str, Any]:
    config_path = Path(__file__).resolve().parents[2] / "mcp.json"

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    config["mcpServers"]["filesystem"]["args"][-1] = str(
        Path(workspace_path).resolve()
    )

    return config