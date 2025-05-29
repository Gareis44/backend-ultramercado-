from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from psycopg2 import connect

app = Flask(__name__)
CORS(app)

# Neon config desde variables de entorno (Railway)
PG_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": 5432,
    "database": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
    "sslmode": "require"
}

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route("/productos", methods=["GET"])
def obtener_productos():
    consulta = request.args.get("q", "").strip().lower()

    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if consulta:
            cursor.execute("""
                SELECT db, nombre, precio, imagen, condicion_especial
                FROM productos
                WHERE LOWER(nombre) LIKE %s
            """, (f"%{consulta}%",))
        else:
            cursor.execute("""
                SELECT db, nombre, precio, imagen, condicion_especial
                FROM productos
            """)

        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultados)

    except Exception as e:
        print("❌ Error al conectar a PostgreSQL:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
