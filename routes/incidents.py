from flask import Blueprint, render_template
from models.incident import Incident

incident_bp = Blueprint("incident", __name__)


@incident_bp.route("/incidents/<int:case_id>")
def incidents(case_id):

    data = Incident.query.filter_by(case_id=case_id).all()

    return render_template("incidents.html", incidents=data)