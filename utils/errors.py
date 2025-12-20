from flask import jsonify


class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


def handle_api_error(error: APIError):
    return jsonify({
        "success": False,
        "error": error.message
    }), error.status_code
