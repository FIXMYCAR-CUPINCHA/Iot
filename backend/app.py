import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visionmoto.db')


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = 'visionmoto-secret'
    return app


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            frame INTEGER,
            track_id INTEGER,
            x1 INTEGER,
            y1 INTEGER,
            x2 INTEGER,
            y2 INTEGER,
            fps REAL,
            count INTEGER
        );
        """
    )
    connection.commit()
    connection.close()


app = create_app()
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/detections', methods=['POST'])
def detections():
    payload = request.get_json(silent=True) or {}
    frame = int(payload.get('frame', 0))
    track_id = int(payload.get('track_id', -1))
    x1 = int(payload.get('x1', 0))
    y1 = int(payload.get('y1', 0))
    x2 = int(payload.get('x2', 0))
    y2 = int(payload.get('y2', 0))
    fps = float(payload.get('fps', 0.0))
    count = int(payload.get('count', 0))

    created_at = datetime.utcnow().isoformat()

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO detections (created_at, frame, track_id, x1, y1, x2, y2, fps, count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (created_at, frame, track_id, x1, y1, x2, y2, fps, count)
    )
    connection.commit()
    connection.close()

    event = {
        'created_at': created_at,
        'frame': frame,
        'track_id': track_id,
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'fps': fps,
        'count': count,
    }
    socketio.emit('detection', event, broadcast=True)
    return jsonify({'status': 'ok'}), 201


@app.route('/metrics', methods=['GET'])
def metrics():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT COUNT(*) FROM detections')
    total_events = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT track_id) FROM detections WHERE track_id >= 0')
    unique_tracks = cursor.fetchone()[0]

    cursor.execute('SELECT fps FROM detections ORDER BY id DESC LIMIT 60')
    last_fps = [row[0] for row in cursor.fetchall()]
    avg_fps = sum(last_fps) / len(last_fps) if last_fps else 0.0

    connection.close()

    return jsonify({
        'total_events': total_events,
        'unique_tracks': unique_tracks,
        'avg_fps_last_60': avg_fps,
    })


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    init_db()
    # eventlet/gevent are optional; use Werkzeug for dev
    socketio.run(app, host='0.0.0.0', port=5000)


