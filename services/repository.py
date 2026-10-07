from __future__ import annotations
import json
import sqlite3
from pathlib import Path

class SimulationRepository:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS simulations (id TEXT PRIMARY KEY, state_json TEXT NOT NULL)")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get(self, sim_id: str):
        with self._connect() as con:
            row = con.execute("SELECT state_json FROM simulations WHERE id=?", (sim_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def save(self, sim_id: str, state: dict):
        payload = json.dumps(state, ensure_ascii=False)
        with self._connect() as con:
            con.execute(
                "INSERT INTO simulations(id,state_json) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json",
                (sim_id, payload),
            )

    def delete(self, sim_id: str):
        with self._connect() as con:
            con.execute("DELETE FROM simulations WHERE id=?", (sim_id,))
