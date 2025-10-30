#!/usr/bin/env python3
"""
Event Publisher IoT -> Backend Java
Envia POST /eventos com Idempotency-Key, retry exponencial com jitter e fila offline simples.
"""

import os
import time
import json
import uuid
import random
import sqlite3
from datetime import datetime
from typing import Dict, Optional

import requests


DB_PATH = os.environ.get("IOT_QUEUE_DB", "iot_queue.db")


def _ensure_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS queue (
            id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            last_error TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _enqueue(event_id: str, payload: Dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO queue (id, payload, created_at, attempts) VALUES (?, ?, ?, ?)",
        (event_id, json.dumps(payload), datetime.utcnow().isoformat() + "Z", 0),
    )
    conn.commit()
    conn.close()


def _dequeue_batch(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, payload, attempts FROM queue ORDER BY created_at LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def _delete(id_: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM queue WHERE id = ?", (id_,))
    conn.commit()
    conn.close()


class IoTEventPublisher:
    def __init__(self):
        self.base_url = os.environ.get("BACKEND_BASE_URL", "http://localhost:5001").rstrip("/")
        self.auth_bearer = os.environ.get("AUTH_BEARER", "demo-token")
        self.device_id = os.environ.get("DEVICE_ID", "cam-01")
        self.batch_size = int(os.environ.get("EVENT_BATCH_SIZE", "10"))
        self.retry_ms = int(os.environ.get("EVENT_RETRY_MS", "2000"))
        _ensure_db()

    def _headers(self, event_id: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.auth_bearer}",
            "Content-Type": "application/json",
            "Idempotency-Key": event_id,
            "X-Correlation-Id": event_id,
        }

    def send_event(self, payload: Dict, event_id: Optional[str] = None) -> bool:
        event_id = event_id or payload.get("id") or str(uuid.uuid4())
        url = f"{self.base_url}/api/iot/eventos"
        try:
            res = requests.post(url, headers=self._headers(event_id), json=payload, timeout=5)
            if res.status_code in (200, 201):
                return True
            # respostas não 2xx: enfileira
            _enqueue(event_id, payload)
            return False
        except requests.exceptions.RequestException as e:
            _enqueue(event_id, payload)
            return False

    def flush_queue(self):
        rows = _dequeue_batch(self.batch_size)
        if not rows:
            return 0, 0
        sent = 0
        for id_, payload_str, attempts in rows:
            payload = json.loads(payload_str)
            try:
                res = requests.post(
                    f"{self.base_url}/api/iot/eventos", headers=self._headers(id_), json=payload, timeout=5
                )
                if res.status_code in (200, 201):
                    _delete(id_)
                    sent += 1
                else:
                    # backoff simples por item (incremento attempts)
                    self._bump_attempts(id_)
            except requests.exceptions.RequestException:
                self._bump_attempts(id_)
        return sent, len(rows) - sent

    def _bump_attempts(self, id_: str):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE queue SET attempts = attempts + 1 WHERE id = ?", (id_,))
        conn.commit()
        conn.close()


def simulate_events(count: int = 1, event_type: str = "PARKING_OUT_OF_SPOT"):
    pub = IoTEventPublisher()
    sent = 0
    for i in range(count):
        event_id = f"evt-{uuid.uuid4()}"
        payload = {
            "id": event_id,
            "deviceId": pub.device_id,
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "imageUrl": f"{pub.base_url}/static/{pub.device_id}/frame-{random.randint(1,999)}.jpg",
            "location": {
                "lat": float(os.environ.get("SITE_LAT", "-23.56168")),
                "lng": float(os.environ.get("SITE_LNG", "-46.65614")),
            },
            "metadata": {"plate": "ABC1D23", "slot": "VAGA-07"},
        }
        ok = pub.send_event(payload, event_id=event_id)
        sent += 1 if ok else 0
        # pequeno intervalo
        time.sleep(0.1)

    # tenta flush após enviar
    flushed, pending = pub.flush_queue()
    print(f"Enviados imediatos: {sent} | Reprocessados: {flushed} | Pendentes: {pending}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IoT Event Publisher")
    sub = parser.add_subparsers(dest="cmd")

    sim = sub.add_parser("simulate", help="Simula envio de eventos")
    sim.add_argument("--type", default="PARKING_OUT_OF_SPOT")
    sim.add_argument("--count", type=int, default=1)

    args = parser.parse_args()
    if args.cmd == "simulate":
        simulate_events(count=args.count, event_type=args.type)
    else:
        parser.print_help()


