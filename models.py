from flask_sqlalchemy import SQLAlchemy
from __main__ import app


db = SQLAlchemy(app)


class Ads(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    settlement = db.Column(db.String(50))
    under_construction = db.Column(db.Boolean)
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    oblast_district = db.Column(db.String(50))
    living_area = db.Column(db.Float)
    has_balcony = db.Column(db.Boolean)
    address = db.Column(db.String(100))
    construction_year = db.Column(db.Integer)
    rooms_number = db.Column(db.Integer)
    premise_area = db.Column(db.Float)
    active = db.Column(db.Boolean)
