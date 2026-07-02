import os
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from werkzeug.utils import secure_filename

from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from database.db import db

from modules.parser.hayabusa import run_hayabusa
from modules.engine.incident_engine import build_incidents
from config import Config


evidence_bp = Blueprint("evidence", __name__)


# -------------------------
# GET PAGE (FIXED - WAS MISSING)
# -------------------------
@evidence_bp.route("/evidence/<int:case_id>", methods=["GET"])
@login_required
def evidence_page(case_id):

    return render_template("evidence.html", case_id=case_id)


# -------------------------
# UPLOAD + PROCESS EVIDENCE
# -------------------------
@evidence_bp.route("/evidence/upload/<int:case_id>", methods=["POST"])
@login_required
def upload_evidence(case_id):

    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "No file provided"}), 400

        # -------------------------
        # SAVE FILE
        # -------------------------
        filename = secure_filename(file.filename)
        filename = f"{case_id}_{filename}"   # prevent overwrite

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        save_path = os.path.join(Config.UPLOAD_FOLDER, filename)

        file.save(save_path)

        # -------------------------
        # SAVE EVIDENCE TO DB
        # -------------------------
        evidence = Evidence(
            case_id=case_id,
            filename=filename,
            filepath=save_path
        )

        db.session.add(evidence)
        db.session.commit()

        # -------------------------
        # RUN HAYABUSA PARSER
        # -------------------------
        output_dir = os.path.join(Config.OUTPUT_FOLDER, str(case_id))
        os.makedirs(output_dir, exist_ok=True)

        tool_path = os.path.join(Config.TOOL_FOLDER, "hayabusa.exe")

        events = run_hayabusa(save_path, output_dir, tool_path)

        if not events:
            return jsonify({
                "message": "No events parsed",
                "events_count": 0,
                "incidents_count": 0
            })

        # -------------------------
        # STORE EVENTS
        # -------------------------
        event_objects = []

        for e in events:
            event_objects.append(
                Event(
                    case_id=case_id,
                    timestamp=e.get("timestamp"),
                    computer=e.get("computer"),
                    channel=e.get("channel"),
                    event_id=str(e.get("event_id", "")),
                    record_id=e.get("record_id"),
                    rule_title=e.get("rule_title"),
                    rule_id=e.get("rule_id"),
                    severity=e.get("severity"),
                    details=e.get("details"),
                    extra_info=e.get("extra_info")
                )
            )

        db.session.bulk_save_objects(event_objects)
        db.session.commit()

        # -------------------------
        # INCIDENT ENGINE
        # -------------------------
        incidents = build_incidents(events)

        incident_objects = []

        for i in incidents:
            incident_objects.append(
                Incident(
                    case_id=case_id,
                    title=i.get("title"),
                    severity=i.get("severity"),
                    rule=i.get("rule"),
                    event_count=i.get("event_count", 0),
                    first_seen=i.get("first_seen"),
                    last_seen=i.get("last_seen")
                )
            )

        db.session.bulk_save_objects(incident_objects)
        db.session.commit()

        # -------------------------
        # RESPONSE
        # -------------------------
        return jsonify({
            "message": "Evidence processed successfully",
            "events_count": len(event_objects),
            "incidents_count": len(incident_objects)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": str(e)
        }), 500