from database.db import db
from datetime import datetime


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), index=True)

    title = db.Column(db.String(255))
    severity = db.Column(db.String(50))

    rule = db.Column(db.String(255))

    event_count = db.Column(db.Integer, default=0)

    first_seen = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)