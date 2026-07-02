from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from models.case import Case
from database.db import db

cases_bp = Blueprint("cases", __name__)


# -------------------------
# LIST ALL CASES
# -------------------------
@cases_bp.route("/cases", methods=["GET"])
@login_required
def list_cases():

    cases = Case.query.all()

    # ❌ FIX: removed undefined case_id
    return render_template("cases.html", cases=cases)


# -------------------------
# CREATE NEW CASE
# -------------------------
@cases_bp.route("/cases/create", methods=["POST"])
@login_required
def create_case():

    name = request.form.get("case_name")
    desc = request.form.get("description")

    new_case = Case(
        case_name=name,
        description=desc
    )

    db.session.add(new_case)
    db.session.commit()

    return redirect(url_for("cases.list_cases"))