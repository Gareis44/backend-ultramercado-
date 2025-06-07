# from flask import Flask, jsonify, request, send_from_directory
# from flask_cors import CORS
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import os
# import logging

# app = Flask(__name__)
# CORS(app)

# # Configurar logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Neon config desde variables de entorno (Railway)
# PG_CONFIG = {
#     "host": os.getenv("PGHOST"),
#     "port": 5432,
#     "database": os.getenv("PGDATABASE"),
#     "user": os.getenv("PGUSER"),
#     "password": os.getenv("PGPASSWORD"),
#     "sslmode": "require"
# }

# def verificar_config_db():
#     """Verifica que todas las variables de entorno estén configuradas"""
#     required_vars = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
#     missing_vars = [var for var in required_vars if not os.getenv(var)]
    
#     if missing_vars:
#         logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
#         return False
    
#     logger.info("✅ Variables de entorno de DB configuradas correctamente")
#     return True

# @app.route("/")
# def index():
#     """Ruta raíz - devuelve información de la API"""
#     return jsonify({
#         "message": "UltraMercado API",
#         "version": "1.0",
#         "endpoints": {
#             "/productos": "GET - Obtener todos los productos o buscar con ?q=termino",
#             "/health": "GET - Estado de la API"
#         }
#     })

# @app.route("/health")
# def health_check():
#     """Endpoint para verificar el estado de la API y la DB"""
#     try:
#         # Verificar variables de entorno
#         if not verificar_config_db():
#             return jsonify({
#                 "status": "error",
#                 "message": "Variables de entorno de DB no configuradas"
#             }), 500

#         # Probar conexión a la base de datos
#         conn = psycopg2.connect(**PG_CONFIG)
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1")
#         cursor.close()
#         conn.close()
        
#         return jsonify({
#             "status": "healthy",
#             "database": "connected",
#             "message": "API funcionando correctamente"
#         })
    
#     except Exception as e:
#         logger.error(f"❌ Health check failed: {e}")
#         return jsonify({
#             "status": "error",
#             "database": "disconnected",
#             "error": str(e)
#         }), 500

# @app.route("/productos", methods=["GET"])
# def obtener_productos():
#     """Obtener productos con búsqueda opcional"""
#     try:
#         # Verificar configuración de DB
#         if not verificar_config_db():
#             return jsonify({
#                 "error": "Configuración de base de datos incompleta",
#                 "productos": []
#             }), 500

#         consulta = request.args.get("q", "").strip().lower()
#         logger.info(f"🔍 Búsqueda de productos: '{consulta}'")

#         # Conectar a la base de datos
#         conn = psycopg2.connect(**PG_CONFIG)
#         cursor = conn.cursor(cursor_factory=RealDictCursor)

#         if consulta:
#             cursor.execute("""
#                 SELECT id, db, nombre, precio, imagen, condicion_especial
#                 FROM productos
#                 WHERE LOWER(nombre) LIKE %s
#                 ORDER BY nombre
#             """, (f"%{consulta}%",))
#         else:
#             cursor.execute("""
#                 SELECT id, db, nombre, precio, imagen, condicion_especial
#                 FROM productos
#                 ORDER BY nombre
#             """)

#         resultados = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         # Convertir a lista de diccionarios para asegurar serialización JSON
#         productos = []
#         for row in resultados:
#             productos.append({
#                 "id": str(row["id"]),
#                 "db": row["db"],
#                 "nombre": row["nombre"],
#                 "precio": float(row["precio"]) if row["precio"] else 0.0,
#                 "imagen": row["imagen"] or "",
#                 "condicion_especial": row["condicion_especial"]
#             })

#         logger.info(f"✅ Productos encontrados: {len(productos)}")
        
#         # Asegurar que la respuesta sea JSON con headers correctos
#         response = jsonify(productos)
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     except psycopg2.Error as db_error:
#         logger.error(f"❌ Error de base de datos: {db_error}")
#         return jsonify({
#             "error": "Error de base de datos",
#             "message": str(db_error),
#             "productos": []
#         }), 500

#     except Exception as e:
#         logger.error(f"❌ Error general: {e}")
#         return jsonify({
#             "error": "Error interno del servidor",
#             "message": str(e),
#             "productos": []
#         }), 500

# @app.route("/static/<path:filename>")
# def serve_static(filename):
#     """Servir archivos estáticos si existen"""
#     try:
#         return send_from_directory("static", filename)
#     except:
#         return jsonify({"error": "Archivo no encontrado"}), 404

# @app.errorhandler(404)
# def not_found(error):
#     """Manejar rutas no encontradas devolviendo JSON"""
#     return jsonify({
#         "error": "Endpoint no encontrado",
#         "message": "La ruta solicitada no existe"
#     }), 404

# @app.errorhandler(500)
# def internal_error(error):
#     """Manejar errores internos devolviendo JSON"""
#     return jsonify({
#         "error": "Error interno del servidor",
#         "message": "Ocurrió un error inesperado"
#     }), 500

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     logger.info(f"🚀 Iniciando servidor en puerto {port}")
    
#     # Verificar configuración al inicio
#     if verificar_config_db():
#         logger.info("✅ Configuración verificada, iniciando servidor...")
#     else:
#         logger.warning("⚠️ Problemas de configuración detectados")
    
#     app.run(host="0.0.0.0", port=port, debug=False)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from datetime import datetime, timedelta

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
        "status": "running",
        "endpoints": {
            "/productos": "GET - Obtener productos recientes o buscar con ?q=termino",
            "/health": "GET - Estado de la API"
        }
    })

@app.route("/health")
def health_check():
    """Endpoint para verificar el estado de la API y la DB"""
    try:
        if not verificar_config_db():
            return jsonify({
                "status": "error",
                "message": "Variables de entorno de DB no configuradas",
                "database": "not_configured"
            }), 500

        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "total_productos": total_productos,
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
    """Obtener productos recientes con búsqueda opcional"""
    try:
        logger.info("🔍 Iniciando obtención de productos...")
        
        # Verificar configuración ANTES de hacer cualquier cosa
        if not verificar_config_db():
            logger.error("❌ Configuración de DB incompleta")
            return jsonify({
                "error": "Configuración de base de datos incompleta",
                "productos": [],
                "total": 0,
                "fecha_datos": "",
                "mensaje": "Error de configuración"
            }), 500

        consulta = request.args.get("q", "").strip().lower()
        
        # Calcular fechas para filtrar productos recientes
        hoy = datetime.now().date()
        ayer = hoy - timedelta(days=1)
        
        logger.info(f"🔍 Búsqueda: '{consulta}' | Fechas: {hoy}, {ayer}")

        # Conectar a la base de datos
        try:
            conn = psycopg2.connect(**PG_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Conexión a DB establecida")
        except Exception as db_error:
            logger.error(f"❌ Error conectando a DB: {db_error}")
            return jsonify({
                "error": "Error de conexión a base de datos",
                "message": str(db_error),
                "productos": [],
                "total": 0,
                "fecha_datos": "",
                "mensaje": "Error de conexión"
            }), 500

        # Primero intentar obtener productos de hoy
        if consulta:
            logger.info(f"🔍 Buscando productos con término: '{consulta}' para fecha: {hoy}")
            cursor.execute("""
                SELECT id, db, nombre, precio, precio_descuento, imagen, condicion_especial, fecha
                FROM productos
                WHERE LOWER(nombre) LIKE %s 
                AND DATE(fecha) = %s
                ORDER BY fecha DESC, nombre
                LIMIT 100
            """, (f"%{consulta}%", hoy))
        else:
            logger.info(f"🔍 Obteniendo todos los productos para fecha: {hoy}")
            cursor.execute("""
                SELECT id, db, nombre, precio, precio_descuento, imagen, condicion_especial, fecha
                FROM productos
                WHERE DATE(fecha) = %s
                ORDER BY fecha DESC, nombre
                LIMIT 100
            """, (hoy,))

        resultados = cursor.fetchall()
        logger.info(f"📊 Productos encontrados para {hoy}: {len(resultados)}")
        
        # Si no hay productos de hoy, buscar de ayer
        if not resultados:
            logger.info(f"📅 No hay productos de hoy ({hoy}), buscando de ayer ({ayer})")
            
            if consulta:
                cursor.execute("""
                    SELECT id, db, nombre, precio, precio_descuento, imagen, condicion_especial, fecha
                    FROM productos
                    WHERE LOWER(nombre) LIKE %s 
                    AND DATE(fecha) = %s
                    ORDER BY fecha DESC, nombre
                    LIMIT 100
                """, (f"%{consulta}%", ayer))
            else:
                cursor.execute("""
                    SELECT id, db, nombre, precio, precio_descuento, imagen, condicion_especial, fecha
                    FROM productos
                    WHERE DATE(fecha) = %s
                    ORDER BY fecha DESC, nombre
                    LIMIT 100
                """, (ayer,))
            
            resultados = cursor.fetchall()
            logger.info(f"📊 Productos encontrados para {ayer}: {len(resultados)}")

        cursor.close()
        conn.close()

        # Convertir a lista de diccionarios
        productos = []
        for i, row in enumerate(resultados):
            try:
                # Calcular precio final (usar precio_descuento si existe, sino precio normal)
                precio_final = float(row["precio_descuento"]) if row["precio_descuento"] else float(row["precio"]) if row["precio"] else 0.0
                precio_original = float(row["precio"]) if row["precio"] else 0.0
                tiene_descuento = row["precio_descuento"] is not None and row["precio_descuento"] != row["precio"]
                
                producto = {
                    "id": str(row["id"]),
                    "db": str(row["db"] or "unknown"),
                    "nombre": str(row["nombre"] or "Sin nombre"),
                    "precio": precio_final,
                    "precio_original": precio_original if tiene_descuento else None,
                    "tiene_descuento": tiene_descuento,
                    "imagen": str(row["imagen"] or ""),
                    "condicion_especial": str(row["condicion_especial"]) if row["condicion_especial"] else None,
                    "fecha": row["fecha"].isoformat() if row["fecha"] else None
                }
                productos.append(producto)
                
                if i < 3:  # Log primeros 3 productos para debug
                    logger.info(f"📦 Producto {i+1}: {producto['nombre']} - ${producto['precio']}")
                    
            except Exception as e:
                logger.error(f"❌ Error procesando producto {i}: {e}")
                logger.error(f"📄 Datos del producto: {dict(row)}")
                continue

        fecha_usada = hoy if len([p for p in productos if p["fecha"] and p["fecha"].startswith(str(hoy))]) > 0 else ayer
        
        logger.info(f"✅ Productos procesados: {len(productos)} (fecha: {fecha_usada})")
        
        # ASEGURAR que siempre devolvemos la estructura correcta
        response_data = {
            "productos": productos,  # SIEMPRE incluir esta propiedad
            "total": len(productos),
            "fecha_datos": str(fecha_usada),
            "mensaje": f"Productos del {fecha_usada}",
            "status": "success"
        }
        
        logger.info(f"📤 Enviando respuesta con {len(productos)} productos")
        logger.info(f"📤 Estructura de respuesta: {list(response_data.keys())}")
        
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    except psycopg2.Error as db_error:
        logger.error(f"❌ Error de base de datos: {db_error}")
        return jsonify({
            "error": "Error de base de datos",
            "message": str(db_error),
            "productos": [],  # SIEMPRE incluir
            "total": 0,
            "fecha_datos": "",
            "mensaje": "Error de base de datos",
            "status": "error"
        }), 500

    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        logger.error(f"❌ Stack trace: ", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "message": str(e),
            "productos": [],  # SIEMPRE incluir
            "total": 0,
            "fecha_datos": "",
            "mensaje": "Error interno",
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Manejar rutas no encontradas devolviendo JSON"""
    return jsonify({
        "error": "Endpoint no encontrado",
        "message": "La ruta solicitada no existe",
        "status": "not_found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores internos devolviendo JSON"""
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ocurrió un error inesperado",
        "status": "internal_error"
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Iniciando servidor en puerto {port}")
    
    if verificar_config_db():
        logger.info("✅ Configuración verificada, iniciando servidor...")
    else:
        logger.warning("⚠️ Problemas de configuración detectados")
    
    app.run(host="0.0.0.0", port=port, debug=False)

