from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from sqlalchemy import or_

from database.db import db
from models.event import Event

import csv
import io

events_bp = Blueprint("events", __name__)


@events_bp.route("/events/<int:case_id>")
@login_required
def view_events(case_id):

    page = request.args.get("page", 1, type=int)

    search = request.args.get("search", "").strip()

    severity = request.args.get("severity", "").strip()

    computer = request.args.get("computer", "").strip()

    channel = request.args.get("channel", "").strip()

    rule = request.args.get("rule", "").strip()

    eventid = request.args.get("eventid", "").strip()

    sort = request.args.get("sort", "timestamp")

    order = request.args.get("order", "desc")

    query = Event.query.filter_by(case_id=case_id)

    # --------------------------
    # SEARCH
    # --------------------------

    if search:

        query = query.filter(

            or_(

                Event.details.ilike(f"%{search}%"),

                Event.rule_title.ilike(f"%{search}%"),

                Event.computer.ilike(f"%{search}%")

            )

        )

    # --------------------------
    # FILTERS
    # --------------------------

    if severity:
        query = query.filter(Event.severity == severity)

    if computer:
        query = query.filter(Event.computer == computer)

    if channel:
        query = query.filter(Event.channel == channel)

    if rule:
        query = query.filter(Event.rule_title == rule)

    if eventid:
        query = query.filter(Event.event_id == eventid)

    # --------------------------
    # SORTING
    # --------------------------

    sort_columns = {

        "timestamp": Event.timestamp,

        "severity": Event.severity,

        "computer": Event.computer,

        "eventid": Event.event_id

    }

    column = sort_columns.get(sort, Event.timestamp)

    if order == "asc":
        query = query.order_by(column.asc())
    else:
        query = query.order_by(column.desc())

    # --------------------------
    # STATS
    # --------------------------

    total = query.count()

    critical = query.filter(Event.severity.ilike("critical")).count()

    high = query.filter(Event.severity.ilike("high")).count()

    medium = query.filter(Event.severity.ilike("medium")).count()

    low = query.filter(Event.severity.ilike("low")).count()

    informational = query.filter(Event.severity.ilike("informational")).count()

    # --------------------------
    # DROPDOWNS
    # --------------------------

    computers = (

        db.session.query(Event.computer)

        .filter_by(case_id=case_id)

        .distinct()

        .order_by(Event.computer)

        .all()

    )

    channels = (

        db.session.query(Event.channel)

        .filter_by(case_id=case_id)

        .distinct()

        .order_by(Event.channel)

        .all()

    )

    rules = (

        db.session.query(Event.rule_title)

        .filter_by(case_id=case_id)

        .distinct()

        .order_by(Event.rule_title)

        .all()

    )

    # --------------------------
    # PAGINATION
    # --------------------------

    pagination = query.paginate(

        page=page,

        per_page=25,

        error_out=False

    )

    return render_template(

        "events.html",

        events=pagination.items,

        pagination=pagination,

        case_id=case_id,

        total=total,

        critical=critical,

        high=high,

        medium=medium,

        low=low,

        informational=informational,

        computers=computers,

        channels=channels,

        rules=rules,

        search=search,

        severity_filter=severity,

        computer_filter=computer,

        channel_filter=channel,

        rule_filter=rule,

        eventid_filter=eventid,

        sort=sort,

        order=order

    )


@events_bp.route("/events/export/<int:case_id>")
@login_required
def export_events(case_id):

    events = Event.query.filter_by(case_id=case_id).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([

        "Timestamp",

        "Computer",

        "Channel",

        "EventID",

        "Severity",

        "Rule",

        "Details"

    ])

    for e in events:

        writer.writerow([

            e.timestamp,

            e.computer,

            e.channel,

            e.event_id,

            e.severity,

            e.rule_title,

            e.details

        ])

    output.seek(0)

    return Response(

        output,

        mimetype="text/csv",

        headers={

            "Content-Disposition":

            f"attachment; filename=case_{case_id}_events.csv"

        }

    )