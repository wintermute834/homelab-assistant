
from typing import Optional

from ..database import SnapshotDatabase
from ..harness import Tool



__all__ = (
    "get_newest_snapshots",
    "filter_snapshots",
    "database_tools"
)


DATABASE = SnapshotDatabase()


# Tool functions
def _get_newest_snapshots() -> list[str]:
    return DATABASE.get_newest()


def _filter_snapshots(
        *,
        hostnames: Optional[list[str]] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        new_to_old: bool = True,
        max_results: int = 4
    ) -> list[str]:

    return DATABASE.get_snapshots(hostnames, start_timestamp, end_timestamp, new_to_old, max(1, min(128, max_results)))


# Tool definiitons
get_newest_snapshots = Tool(**{
    "definition": {
        "function": {
            "name": "get_newest_snapshots",
            "description": "Gets the most recent snapshot from each machine."
        }
    },
    "function": _get_newest_snapshots
})

filter_snapshots = Tool(**{
    "definition": {
        "function": {
            "name": "filter_snapshots",
            "description": "Gets historical snapshots from specific machines in an optional time range. All timestamps should be in utc format: \"YYYY-MM-DD HH:MM:SS\".",
            "parameters": {
                "properties": {
                    "hostnames": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The hostnames of machines whose snapshots will be included. Gives data from all machines if unspecified."
                    },
                    "start_timestamp": {
                        "type": "string",
                        "description": "The start of the timestamp range. Defaults to the earliest snapshot if unspecified."
                    },
                    "end_timestamp": {
                        "type": "string",
                        "description": "The end of the timestamp range. Defaults to the newest snapshot if unspecified."
                    },
                    "newest_to_old": {
                        "type": "boolean",
                        "description": "Sorts results from newest timestamp to oldest when true, and oldest to newest when false. Defaults to true."
                    },
                    "max_results": {
                        "type": "number",
                        "description": "The maximum number of snapshots to return. Defaults to 4 and is capped at 128."
                    }
                }
            }
        }
    },
    "function": _filter_snapshots
})


# Collection of all database tools
database_tools = (
    get_newest_snapshots,
    filter_snapshots
)

