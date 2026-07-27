
from shim import get_shim
from database.database import SnapshotDatabase
from orchestrator.lan_addresses import rivendell



db = SnapshotDatabase()

snapshot = get_shim(rivendell)

if snapshot:
    db.insert_snapshot(snapshot)


