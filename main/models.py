from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from main import db, login


# Helper tables for ManyToMany relationships, no class needed
areas_volunteers = db.Table('areas_vs_volunteers',
                            db.Column('area', db.String(80), db.ForeignKey('area.area'), primary_key=True),
                            db.Column('vol_id', db.Integer, db.ForeignKey('volunteer.id'), primary_key=True))


volunteers_species = db.Table('volunteers_vs_species',
                              db.Column('vol_id', db.Integer, db.ForeignKey('volunteer.id'), primary_key=True),
                              db.Column('foster_species', db.String(20), db.ForeignKey('foster_species.species'), primary_key=True))


class Clinic(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    name = db.Column(db.String(250), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone_numbers = db.relationship('PhoneNumber', backref='clinic', lazy='subquery')
    area_name = db.Column(db.String(80), db.ForeignKey('area.area'), nullable=True)
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Clinic %r>' % self.name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Used by Flask-Login, will pass id as String so must be cast to int to be read by db
    @login.user_loader
    def load_user(id):
        return Clinic.query.get(int(id))


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80))
    lname = db.Column(db.String(100))
    phone_numbers = db.relationship('PhoneNumber', lazy='subquery', backref=db.backref('volunteer', lazy=True))
    areas = db.relationship('Area', secondary=areas_volunteers, lazy='subquery',
                            backref=db.backref('volunteers', lazy=True))
    species = db.relationship('FosterSpecies', secondary=volunteers_species, lazy='subquery',
                              backref=db.backref('volunteers', lazy=True))
    last_contacted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    black_listed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return '<Volunteer %r>' % self.fname+' '+self.lname


class PhoneNumber(db.Model):
    dial_code = db.Column(db.String(3), primary_key=True)
    phone_number = db.Column(db.String(7), primary_key=True)
    primary_contact = db.Column(db.Boolean, default=False)
    # Foreignkey to connect to either Clinic or Volunteer as ManyToOne
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'), nullable=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=True)

    def __repr__(self):
        return str(self.dial_code) + "-" + str(self.phone_number)

    # Used in routes to check for empty phone numbers with other attributes before saving to db.
    def not_empty(self):
        if not self.dial_code and not self.phone_number:
            return False
        else:
            return True

    def edit(self, new_data):
        self.dial_code = new_data.dial_code
        self.phone_number = new_data.phone_number
        self.primary_contact = new_data.primary_contact
        self.clinic_id = new_data.clinic_id
        self.volunteer_id = new_data.volunteer_id


class Area(db.Model):
    area = db.Column(db.String(80), primary_key=True)
    # OneToMany connection with Clinic. Connection with Volunteer is ManyToMany and defined with helper table
    clinics = db.relationship('Clinic', backref=db.backref('areas', lazy='subquery'), lazy=True, )

    def __repr__(self):
        return self.area


class FosterSpecies(db.Model):
    species = db.Column(db.String(20), primary_key=True)

    def __repr__(self):
        return self.species
