import hmac, logging, time, uuid
from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException
from database import INTERNAL_TOKEN
from orders import orders
from returns import returns
from utils import ApiError, error_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("compras")
app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False
app.register_blueprint(orders)
app.register_blueprint(returns)

@app.before_request
def check_internal_token():
    g.correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
    g.start = time.monotonic()
    if request.path == "/health":
        return None
    received = request.headers.get("X-Internal-Token", "")
    if not INTERNAL_TOKEN or not hmac.compare_digest(received.encode(), INTERNAL_TOKEN.encode()):
        return error_response(401, "TOKEN_INTERNO_INVALIDO", "Esta ruta solo la puede usar el API Gateway")
    return None

@app.after_request
def log_request(response):
    response.headers["X-Correlation-Id"] = g.get("correlation_id", "")
    logger.info("%s %s %s %sms user_id=%s correlation_id=%s", request.method, request.path, response.status_code,
                round((time.monotonic() - g.get("start", time.monotonic())) * 1000),
                request.headers.get("X-User-Id", "-"), g.get("correlation_id"))
    return response

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "compras"})

@app.errorhandler(ApiError)
def handle_api_error(error):
    return error_response(error.status, error.code, error.message, error.errors)

@app.errorhandler(404)
def not_found(error):
    return error_response(404, "NO_ENCONTRADO", "La ruta solicitada no existe")

@app.errorhandler(405)
def method_not_allowed(error):
    return error_response(405, "METODO_NO_PERMITIDO", f"El método {request.method} no está permitido en esta ruta")

@app.errorhandler(Exception)
def unexpected_error(error):
    if isinstance(error, HTTPException):
        return error_response(error.code, "ERROR_HTTP", error.description)
    logger.exception("Error inesperado correlation_id=%s", g.get("correlation_id"))
    return error_response(500, "ERROR_INTERNO", "Ocurrió un error inesperado en el servicio de compras")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
