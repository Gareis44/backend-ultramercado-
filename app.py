# from flask import Flask, jsonify, request, send_from_directory
# from flask_cors import CORS
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import os

# from psycopg2 import connect

# app = Flask(__name__)
# CORS(app)

# # Neon config desde variables de entorno (Railway)
# PG_CONFIG = {
#     "host": os.getenv("PGHOST"),
#     "port": 5432,
#     "database": os.getenv("PGDATABASE"),
#     "user": os.getenv("PGUSER"),
#     "password": os.getenv("PGPASSWORD"),
#     "sslmode": "require"
# }

# @app.route("/")
# def index():
#     return send_from_directory("static", "index.html")

# @app.route("/static/<path:filename>")
# def serve_static(filename):
#     return send_from_directory("static", filename)

# @app.route("/productos", methods=["GET"])
# def obtener_productos():
#     consulta = request.args.get("q", "").strip().lower()

#     try:
#         conn = psycopg2.connect(**PG_CONFIG)
#         cursor = conn.cursor(cursor_factory=RealDictCursor)

#         if consulta:
#             cursor.execute("""
#                 SELECT DISTINCT ON (db, nombre)
#                     id, db, nombre, precio, imagen, condicion_especial
#                 FROM productos
#                 WHERE LOWER(nombre) LIKE %s
#                 ORDER BY db, nombre, fecha DESC;
#             """, (f"%{consulta}%",))
#         else:
#             cursor.execute("""
#                 SELECT DISTINCT ON (db, nombre)
#                     id, db, nombre, precio, imagen, condicion_especial
#                 FROM productos
#                 ORDER BY db, nombre, fecha DESC;
#             """)

#         resultados = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return jsonify(resultados)

#     except Exception as e:
#         print("❌ Error al conectar a PostgreSQL:", e)
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neon config desde variables de entorno (Railway)
PG_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": 5432,
    "database": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
    "sslmode": "require"
}

def verificar_config_db():
    """Verifica que todas las variables de entorno estén configuradas"""
    required_vars = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        return False
    
    logger.info("✅ Variables de entorno de DB configuradas correctamente")
    return True

@app.route("/")
def index():
    """Ruta raíz - devuelve información de la API"""
    return jsonify({
        "message": "UltraMercado API",
        "version": "1.0",
        "endpoints": {
            "/productos": "GET - Obtener todos los productos o buscar con ?q=termino",
            "/health": "GET - Estado de la API"
        }
    })

@app.route("/health")
def health_check():
    """Endpoint para verificar el estado de la API y la DB"""
    try:
        # Verificar variables de entorno
        if not verificar_config_db():
            return jsonify({
                "status": "error",
                "message": "Variables de entorno de DB no configuradas"
            }), 500

        # Probar conexión a la base de datos
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "message": "API funcionando correctamente"
        })
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route("/productos", methods=["GET"])
def obtener_productos():
    """Obtener productos con búsqueda opcional"""
    try:
        # Verificar configuración de DB
        if not verificar_config_db():
            return jsonify({
                "error": "Configuración de base de datos incompleta",
                "productos": []
            }), 500

        consulta = request.args.get("q", "").strip().lower()
        logger.info(f"🔍 Búsqueda de productos: '{consulta}'")

        # Conectar a la base de datos
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if consulta:
            cursor.execute("""
                SELECT id, db, nombre, precio, imagen, condicion_especial
                FROM productos
                WHERE LOWER(nombre) LIKE %s
                ORDER BY nombre
            """, (f"%{consulta}%",))
        else:
            cursor.execute("""
                SELECT id, db, nombre, precio, imagen, condicion_especial
                FROM productos
                ORDER BY nombre
            """)

        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convertir a lista de diccionarios para asegurar serialización JSON
        productos = []
        for row in resultados:
            productos.append({
                "id": str(row["id"]),
                "db": row["db"],
                "nombre": row["nombre"],
                "precio": float(row["precio"]) if row["precio"] else 0.0,
                "imagen": row["imagen"] or "",
                "condicion_especial": row["condicion_especial"]
            })

        logger.info(f"✅ Productos encontrados: {len(productos)}")
        
        # Asegurar que la respuesta sea JSON con headers correctos
        response = jsonify(productos)
        response.headers['Content-Type'] = 'application/json'
        return response

    except psycopg2.Error as db_error:
        logger.error(f"❌ Error de base de datos: {db_error}")
        return jsonify({
            "error": "Error de base de datos",
            "message": str(db_error),
            "productos": []
        }), 500

    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return jsonify({
            "error": "Error interno del servidor",
            "message": str(e),
            "productos": []
        }), 500

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Servir archivos estáticos si existen"""
    try:
        return send_from_directory("static", filename)
    except:
        return jsonify({"error": "Archivo no encontrado"}), 404

@app.errorhandler(404)
def not_found(error):
    """Manejar rutas no encontradas devolviendo JSON"""
    return jsonify({
        "error": "Endpoint no encontrado",
        "message": "La ruta solicitada no existe"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores internos devolviendo JSON"""
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ocurrió un error inesperado"
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Iniciando servidor en puerto {port}")
    
    # Verificar configuración al inicio
    if verificar_config_db():
        logger.info("✅ Configuración verificada, iniciando servidor...")
    else:
        logger.warning("⚠️ Problemas de configuración detectados")
    
    app.run(host="0.0.0.0", port=port, debug=False)

