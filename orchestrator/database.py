"""
A simple SQLite database for storing system snapshots based on machine and timestamp.
"""

import sqlite3
from typing import Optional

from shim import Snapshot



SNAPSHOTS = """
CREATE TABLE IF NOT EXISTS snapshots (
    hostname  TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    snapshot  TEXT NOT NULL
) STRICT
"""



class SnapshotDatabase:
    __slots__ = "connection", "cursor"

    def __init__(self) -> None:
        self.connection = sqlite3.connect("snapshots.db", check_same_thread=False)
        cursor = self.connection.cursor()

        cursor.execute(SNAPSHOTS)


    def _commit(self) -> None:
        self.connection.commit()


    def insert_snapshot(self, snapshot: Snapshot) -> None:
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO snapshots VALUES (?, ?, ?)", (
            snapshot.hostname,
            snapshot.utc_timestamp,
            snapshot.model_dump_json()
        ))
        self._commit()


    def get_hostnames(self) -> list[str]:
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT hostname FROM snapshots")
        result: list[tuple[str]] | None = cursor.fetchall()

        return [] if result is None else [i[0] for i in result]


    def get_newest(self, hostnames: Optional[list[str]] = None) -> list[str]:
        cursor = self.connection.cursor()
        out = []

        for hostname in hostnames if hostnames is not None else self.get_hostnames():
            cursor.execute(f"SELECT snapshot FROM snapshots WHERE hostname = ? ORDER BY timestamp DESC LIMIT 1", (hostname,))
            result: tuple[str] | None = cursor.fetchone()

            if result is not None:
                out.append(result[0])

        return out


    def _execute(self, command: str) -> list[tuple[str]]:
        cursor = self.connection.cursor()

        cursor.execute(command)
        result: list[tuple[str]] = cursor.fetchall()

        return result


    def get_snapshots(
            self,
            hostnames: Optional[list[str]] = None,
            start_timestamp: Optional[str] = None,
            end_timestamp: Optional[str] = None,
            new_to_old: bool = True,
            max_results: int = -1,
            print_sql: bool = False
        ) -> list[str]:

        cursor = self.connection.cursor()

        sql = "SELECT snapshot FROM snapshots"
        args = []
        conjunction = "WHERE"

        if hostnames is not None:
            sql += f" {conjunction} hostname in ({", ".join(["?"] * len(hostnames))})"
            args.extend(hostnames)
            conjunction = "AND"

        match start_timestamp, end_timestamp:
            case None, None:
                pass

            case start, None:
                sql += f" {conjunction} timestamp >= ?"
                args.append(start)
                conjunction = "AND"

            case None, end:
                sql += f" {conjunction} timestamp <= ?"
                args.append(end)
                conjunction = "AND"

            case start, end:
                sql += f" {conjunction} timestamp BETWEEN ? and ?"
                args.extend((start, end))
                conjunction = "AND"

        # add ordering and max_values
        sql += f" ORDER BY timestamp {"DESC" if new_to_old else "ASC"}"
        sql += f" LIMIT {max_results}"

        if print_sql: print(f"SQL: {sql}\nARGS: {args}\n")

        cursor.execute(sql, args)
        result: list[tuple[str]] = cursor.fetchall()

        return [res[0] for res in result]

