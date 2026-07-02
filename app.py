from flask import Flask, redirect, url_for
from config import Config
from database.db import db
import os
from routes.auth import auth_bp, login_manager
from routes.dashboard import dashboard_bp
from routes.cases import cases_bp
from routes.evidence import evidence_bp
from routes.events import events_bp
from routes.timeline import timeline_bp
from modules.engine.incident_engine import build_incidents
from models.incident import Incident
from routes.incidents import incident_bp

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(incident_bp)
    with app.app_context():
        db.create_all()

    # IMPORTANT: root route MUST redirect
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=1337)