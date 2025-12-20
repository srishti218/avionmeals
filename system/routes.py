from flask import Blueprint, jsonify
import os
import time

system_bp = Blueprint("system", __name__)


# ----------------------------------
# GET /health
# ----------------------------------
@system_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "avionmeals-backend",
        "timestamp": int(time.time())
    }), 200


# ----------------------------------
# GET /version
# ----------------------------------
@system_bp.route("/version", methods=["GET"])
def version():
    return jsonify({
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("FLASK_ENV", "production")
    }), 200
