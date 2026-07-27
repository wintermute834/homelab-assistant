
import sqlite3
from typing import Literal, Optional

from pydantic import BaseModel

from shim.schema import Snapshot


# """
# CREATE TABLE cpu(
#     percent     REAL,
#     core_count  INT,
#     load_avg_1m REAL
# ) STRICT
# """
# """
# CREATE TABLE memory(
#     total_gb REAL,
#     used_gb  REAL,
#     used_pct REAL
# ) STRICT
# """
# """
# CREATE TABLE disk(
#     mount    TEXT,
#     total_gb REAL,
#     used_gb  REAL,
#     used_pct REAL
# ) STRICT
# """
# """
# CREATE TABLE gpu(
#     name            TEXT,
#     memory_total_mb INT,
#     memory_used_mb  INT,
#     utilization_pct INT,
#     temp_celcius    INT
# ) STRICT
# """
# """
# CREATE TABLE network(
#     interface TEXT
# ) STRICT
# """
# """
# CREATE TABLE services(
#     interface TEXT
# ) STRICT
# """

# CREATE_TABLE = """
# CREATE TABLE snapshots(
#     hostname  TEXT,
#     timestamp TEXT,
#     cpu INT,
#     memory INT,
#     disk_start INT,
#     disk_end INT,
#     gpu INT,
#     network_start INT,
#     network_end INT,
#     network_available INT,

# ) STRICT
# """



SNAPSHOTS = """
CREATE TABLE IF NOT EXISTS snapshots (
    hostname  INTEGER NOT NULL,  -- mapped to an integer using `hostnames`
    timestamp TEXT NOT NULL,
    snapshot  TEXT NOT NULL
) STRICT
"""

HOSTNAMES = """
CREATE TABLE IF NOT EXISTS hostnames (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL UNIQUE
) STRICT
"""



class TimestampFilter(BaseModel):
    before: Optional[str] = None
    after: Optional[str] = None

    def get_filter(self) -> tuple[str, tuple[str, ...]]:
        match self.before, self.after:
            case None, None:
                raise Exception("Invalid filter. Must have at least one of `before` or `after` set.")

            case before, None:
                return "timestamp < ?", (before,)

            case None, after:
                return "timestamp > ?", (after,)

            case before, after:
                return "BETWEEN ? and ?", (before, after)


class Like(BaseModel):
    pattern: str


class OrderBy(BaseModel):
    column: Literal["hostname", "timestamp"]
    order: Literal["ASC", "DESC"] = "ASC"



class SnapshotDatabase:
    def __init__(self) -> None:
        self.connection = sqlite3.connect("test.db")
        cursor = self.connection.cursor()

        cursor.execute(SNAPSHOTS)
        cursor.execute(HOSTNAMES)


    def _commit(self) -> None:
        self.connection.commit()


    def get_hostname_id(self, hostname: str) -> int:
        cursor = self.connection.cursor()

        cursor.execute("INSERT OR IGNORE INTO hostnames (hostname) VALUES (?)", (hostname,))
        self._commit()

        cursor.execute("SELECT id FROM hostnames WHERE hostname = ?", (hostname,))
        result: tuple[int] = cursor.fetchone()

        return result[0]


    def insert_snapshot(self, snapshot: Snapshot) -> None:
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO snapshots VALUES (?, ?, ?)", (
            self.get_hostname_id(snapshot.hostname),
            snapshot.utc_timestamp,
            snapshot.model_dump_json()
        ))
        self._commit()


    def select(
            self,
            where: str,
            order_by: str = "timestamp DESC",
            max_values: Optional[int] = None
        ) -> list[str]:

        cursor = self.connection.cursor()

        cursor.execute(f"SELECT snapshot FROM snapshots WHERE {where} ORDER BY {order_by}")
        result: list[tuple[str]] = cursor.fetchall()

        return [i[0] for i in result[:max_values]]


    def select_snapshots(
            self,
            hostnames: list[str] | Literal["all"] = "all",
            timestamp_filter: Optional[TimestampFilter] = None,
            snapshot_like: Optional[Like] = None,
            order_by: OrderBy = OrderBy(column="timestamp", order="DESC"),
            max_values: Optional[int] = None
        ) -> list[str]:

        cursor = self.connection.cursor()

        sql = "SELECT snapshot FROM snapshots"
        args = []

        match hostnames, timestamp_filter:
            case "all", None:
                pass

            case "all", filter:
                sql += " WHERE "


        hostnames_filter = "" if hostnames == "all" else " hostname IN "

        cursor.execute(sql, args)
        result: list[tuple[str]] = cursor.fetchall()

        return [i[0] for i in result[:max_values]]

