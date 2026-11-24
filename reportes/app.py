import logging
import os
import hmac
import uuid
from werkzeug.exceptions import HTTPException
from errors import InvalidData, ServiceUnavailable
from reports import bp as reports_bp
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("reportes")

app = Flask(__name__)

def error_response(error, message, status):
    return jsonify({
        "error": error,
        "message": message,
        "correlation_id": getattr(g, "correlation_id", None),
    }), status

@app.before_request
def check_internal_token():
    g.correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
    logger.info("%s %s correlation_id=%s", request.method, request.full_path.rstrip("?"), g.correlation_id)
    if request.path == "/health":
        return None
    expected = os.getenv("INTERNAL_TOKEN", "")
    received = request.headers.get("X-Internal-Token", "")
    if not expected or not hmac.compare_digest(expected, received):
        return error_response("TOKEN_INTERNO_INVALIDO", "Esta ruta solo la puede usar el API Gateway", 401)
    return None

@app.after_request
def add_correlation_header(response):
    response.headers["X-Correlation-Id"] = getattr(g, "correlation_id", "")
    return response

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "reportes"})

app.register_blueprint(reports_bp)

@app.errorhandler(ServiceUnavailable)
def service_unavailable(e):
    return error_response("SERVICIO_NO_DISPONIBLE", f"El servicio de {e.service} no está disponible en este momento", 503)

@app.errorhandler(InvalidData)
def invalid_data(e):
    return error_response("DATOS_INVALIDOS", e.message, 400)

@app.errorhandler(HTTPException)
def http_error(e):
    if e.code == 404:
        return error_response("NO_ENCONTRADO", "La ruta no existe", 404)
    if e.code == 405:
        return error_response("METODO_NO_PERMITIDO", f"El método {request.method} no está permitido en esta ruta", 405)
    return error_response("DATOS_INVALIDOS", e.description, e.code)

@app.errorhandler(Exception)
def unexpected_error(e):
    logger.exception("ERROR inesperado correlation_id=%s", getattr(g, "correlation_id", None))
    return error_response("ERROR_INTERNO", "Error interno del servidor", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG") == "1")