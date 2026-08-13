
import os

from database.database import SnapshotDatabase
from lan_addresses import *



try:
    os.remove("test.db")
except: pass


db = SnapshotDatabase()

for hostname, timestamp, snapshot in [
    ("rivendell", "2026-06-01 00:00:01", "rivendell 0"),
    ("rivendell", "2026-06-01 00:00:05", "rivendell 1"),
    ("rivendell", "2026-06-01 00:01:01", "rivendell 2"),
    ("rivendell", "2026-06-01 00:02:01", "rivendell 3"),
    ("rivendell", "2026-06-01 00:03:01", "rivendell 4"),
    ("rivendell", "2026-06-01 00:04:01", "rivendell 5"),
    ("rivendell", "2026-06-01 01:00:01", "rivendell 6"),
    ("rivendell", "2026-06-01 02:00:01", "rivendell 7"),
    ("rivendell", "2026-06-01 03:00:01", "rivendell 8"),
    ("rivendell", "2026-06-01 03:00:05", "rivendell 9"),
    ("rivendell", "2026-06-02 00:00:01", "rivendell A"),
    ("rivendell", "2026-06-03 00:00:01", "rivendell B"),
    ("rivendell", "2026-06-05 00:00:01", "rivendell C"),
    ("rivendell", "2026-06-10 00:00:01", "rivendell D"),
    ("rivendell", "2026-07-00 00:00:01", "rivendell E"),
    ("rivendell", "2026-07-01 00:00:01", "rivendell F"),
    
    ("caladan", "2026-06-01 00:00:02", "caladan 0"),
    ("caladan", "2026-06-01 00:00:03", "caladan 1"),
    ("caladan", "2026-06-01 00:01:02", "caladan 2"),
    ("caladan", "2026-06-01 00:02:02", "caladan 3"),
    ("caladan", "2026-06-01 00:03:02", "caladan 4"),
    ("caladan", "2026-06-01 00:04:02", "caladan 5"),
    ("caladan", "2026-06-01 01:00:02", "caladan 6"),
    ("caladan", "2026-06-01 02:00:02", "caladan 7"),
    ("caladan", "2026-06-01 03:00:02", "caladan 8"),
    ("caladan", "2026-06-01 03:00:06", "caladan 9"),
    ("caladan", "2026-06-02 00:00:02", "caladan A"),
    ("caladan", "2026-06-03 00:00:02", "caladan B"),
    ("caladan", "2026-06-05 00:00:02", "caladan C"),
    ("caladan", "2026-06-10 00:00:02", "caladan D"),
    ("caladan", "2026-07-00 00:00:02", "caladan E"),
    ("caladan", "2026-07-01 00:00:02", "caladan F"),
]:
    db.connection.cursor().execute("INSERT INTO snapshots VALUES (?, ?, ?)", (hostname, timestamp, snapshot))


print(db.get_hostnames())
print()
print(db.get_newest())
print()
print(db.get_snapshots(["rivendell", "caladan"], max_results=5))
print()
print(db.get_snapshots(start_timestamp="2026-06-10 00:00:02"))
print()
print(db.get_snapshots(["rivendell"], end_timestamp="2026-06-02 09:00:00"))
print()
print(db.get_snapshots(new_to_old=False, max_results=1))
print()
print(db.get_snapshots(["rivendell"], max_results=1) + db.get_snapshots(["caladan"], max_results=1))

