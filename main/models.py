from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from main import db


phone_volunteers = db.Table('phone_vs_volunteers',
                    db.Column('phone_number', db.Integer, db.ForeignKey('phone_number.phone_number'), primary_key=True),
                    db.Column('vol_id', db.Integer, db.ForeignKey('volunteer.id'), primary_key=True))


areas_volunteers = db.Table('areas_vs_volunteers',
                 db.Column('area', db.String(80), db.ForeignKey('area.area'), primary_key=True),
                 db.Column('vol_id', db.Integer, db.ForeignKey('volunteer.id'), primary_key=True))


class Clinic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    name = db.Column(db.String(250), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    phone_numbers = db.relationship('PhoneNumber', backref='clinic', lazy='subquery')
    area_name = db.Column(db.String(80), db.ForeignKey('area.area'), nullable=False)

    def __repr__(self):
        return '<Clinic %r>' % self.name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80))
    lname = db.Column(db.String(100))
    contact_numbers = db.relationship('PhoneNumber', secondary=phone_volunteers, lazy='subquery', backref=db.backref('volunteers', lazy=True))
    areas = db.relationship('Area', secondary=areas_volunteers, lazy='subquery', backref=db.backref('volunteers', lazy=True))
    last_contacted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    black_listed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Volunteer %r>' % self.fname+' '+self.lname


class PhoneNumber(db.Model):
    phone_number = db.Column(db.Integer, primary_key=True)
    # Foreignkey to connect to Clinic, nullable to connect to Volunteer (via helper table)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'), nullable=True)


class Area(db.Model):
    area = db.Column(db.String(80), primary_key=True)
    clinics = db.relationship('Clinic', backref=db.backref('area', lazy='subquery'), lazy=True, )

