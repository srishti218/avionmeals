from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config import get_config
from database import db  # SQLAlchemy instance

from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager

# Load .env
load_dotenv()


def create_app():
    app = Flask(__name__)

    # ----------------------------
    # Load config
    # ----------------------------
    app.config.from_object(get_config())

    # ----------------------------
    # Enable CORS
    # ----------------------------
    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    # ----------------------------
    # Initialize DB
    # ----------------------------
    db.init_app(app)
    print("DB initilisation done")
    jwt = JWTManager(app)
    # ----------------------------
    # Swagger Configuration
    # ----------------------------
    SWAGGER_URL = "/docs"
    API_URL = "/swagger.yaml"

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "AvionMeals API"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route("/swagger.yaml")
    def swagger_yaml():
        with open("swagger.yaml", "r") as f:
            return f.read(), 200, {"Content-Type": "text/yaml"}
    
    # ----------------------------
    # Blueprint imports
    # ----------------------------
    from auth.routes import auth_bp
    from user.routes import user_bp
    from meals.routes import meals_bp
    from recipes.routes import recipes_bp
    from ai.routes import ai_bp
    from subscription.routes import subscription_bp
    from notifications.routes import notifications_bp
    from usage.routes import usage_bp
    from analytics.routes import analytics_bp
    from system.routes import system_bp
    from credits.routes import credits_bp

    # ----------------------------
    # Register Blueprints
    # ----------------------------
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(meals_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(subscription_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(usage_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(credits_bp)

    with app.app_context():
        db.create_all()   # ✅ THIS creates tables
    # ----------------------------
    # Health check shortcut
    # ----------------------------
    @app.route("/")
    def root():
        return jsonify({"status": "AvionMeals Backend Running"}), 200

    # ----------------------------
    # Error handlers
    # ----------------------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=os.getenv("FLASK_ENV") == "development"
    )
