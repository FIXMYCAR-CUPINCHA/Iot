#!/usr/bin/env python3
"""
DatabaseManager - Gerenciador de banco de dados
Módulo para persistência de dados
"""

import sqlite3
from datetime import datetime
import os


class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""

    def __init__(self, db_path="visionmoto.db"):
        self.db_path = db_path

    def initialize(self):
        """Inicializa o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela de detecções
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                frame INTEGER,
                class INTEGER,
                class_name TEXT,
                confidence REAL,
                x1 INTEGER,
                y1 INTEGER,
                x2 INTEGER,
                y2 INTEGER,
                area INTEGER,
                fps REAL,
                total_detections INTEGER,
                unique_motos INTEGER,
                detection_rate REAL
            )
        """
        )

        # Tabela de métricas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_frames INTEGER,
                total_detections INTEGER,
                avg_fps REAL,
                session_duration REAL
            )
        """
        )

        conn.commit()
        conn.close()

    def save_detection(
        self,
        frame_num,
        detections,
        fps,
        total_detections=0,
        unique_motos=0,
        detection_rate=0.0,
    ):
        """Salva detecção no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for det in detections:
            bbox = det["bbox"]
            cursor.execute(
                """
                INSERT INTO detections (created_at, frame, class, class_name, confidence, 
                                      x1, y1, x2, y2, area, fps, total_detections, unique_motos, detection_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    frame_num,
                    det["class"],
                    det["class_name"],
                    det["confidence"],
                    bbox[0],
                    bbox[1],
                    bbox[2],
                    bbox[3],
                    det["area"],
                    fps,
                    total_detections,
                    unique_motos,
                    detection_rate,
                ),
            )

        conn.commit()
        conn.close()

    def save_detections(
        self,
        frame_num,
        detections,
        fps,
        total_detections=0,
        unique_motos=0,
        detection_rate=0.0,
    ):
        """Salva múltiplas detecções"""
        self.save_detection(
            frame_num, detections, fps, total_detections, unique_motos, detection_rate
        )

    def get_statistics(self):
        """Retorna estatísticas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM detections")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT class_name) FROM detections")
        classes = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(fps) FROM detections")
        avg_fps = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_detections": total,
            "unique_classes": classes,
            "avg_fps": avg_fps,
        }

    def get_recent_detections(self, limit=10):
        """Retorna detecções recentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT frame, class_name, confidence, created_at as timestamp 
            FROM detections 
            ORDER BY id DESC 
            LIMIT ?
        """,
            (limit,),
        )

        detections = []
        for row in cursor.fetchall():
            detections.append(
                {
                    "frame": row[0],
                    "class_name": row[1],
                    "confidence": row[2],
                    "timestamp": row[3],
                }
            )

        conn.close()
        return detections
