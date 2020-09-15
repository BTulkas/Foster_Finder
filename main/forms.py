from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, \
    SelectMultipleField, FormField, widgets, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional, Regexp
from wtforms.widgets import HiddenInput

from main.models import Clinic, Area, FosterSpecies, PhoneNumber


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PhoneForm(FlaskForm):
    dial_code = StringField('Phone', validators=[Regexp("^[0-9]{2}$|^[0-9]{3}$", message="Not a valid dial code."), Optional()])
    phone_number = StringField('Number', validators=[Regexp("^[0-9]{7}$", message="Not a valid phone number."), Optional()])
    primary_contact = BooleanField('Primary Phone Number')
    # Must pass these hidden fields so validate can compare object IDs
    clinic_id = IntegerField(widget=HiddenInput())
    volunteer_id = IntegerField(widget=HiddenInput())
    # I have no idea if this is actually needed
    # TODO: check
    submit = SubmitField('Add')

    # Need to override the constructor of nested forms to disable csrf
    # Because for some fucking reason they aren't validated by the parent form
    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(PhoneForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)

    # Custom validator to check dial_code + phone_number together
    def validate(self):
        valid = FlaskForm.validate(self)
        if not valid:
            return False

        """
        if self.dial_code.data is not None and self.phone_number.data is None:
            self.phone_number.errors.append('Please enter phone number.')
            return False

        if self.dial_code.data is None and self.phone_number.data is not None:
            self.dial_code.errors.append('Please enter dial code.')
            return False
        """

        number = PhoneNumber.query.filter_by(dial_code=self.dial_code.data, phone_number=self.phone_number.data).first()

        if (number is not None) and (number.clinic_id != self.clinic_id.data) and (number.volunteer_id != self.volunteer_id.data):
            self.phone_number.errors.append('This phone number already exists in the system.')
            return False

        return True


class ClinicForm(FlaskForm):
    name = StringField('Organisation Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    main_number = FormField(PhoneForm)
    emergency_number = FormField(PhoneForm)
    area = SelectField('Area', validators=[DataRequired()], choices=[(i.area, i.area) for i in Area.query.all()])
    submit = SubmitField('Register')

    # Called on field by default with pattern validate_<field_name>
    def validate_email(self, email):
        clinic = Clinic.query.filter_by(email=email.data).first()
        if clinic is not None:
            raise ValidationError('This email has already been registered.')


class VolunteerForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    phone1 = FormField(PhoneForm)
    phone2 = FormField(PhoneForm)
    areas = SelectMultipleField('Area', validators=[DataRequired()],
                                # Query all areas and converts to tuples (i.title, i.value) (here title=value)
                                choices=[(i.area, i.area) for i in Area.query.all()],
                                widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    species = SelectMultipleField('Can Foster:', validators=[DataRequired()],
                                  # Query all species and converts to tuples (j.title, j.value) (here title=value)
                                  choices=[(j.species, j.species) for j in FosterSpecies.query.all()],
                                  widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    notes = TextAreaField('Notes')
    active = BooleanField('Active')
    black_listed = BooleanField('Black List')
    submit = SubmitField('Add')


class QueryForm(FlaskForm):
    species = SelectMultipleField('Will Foster:', validators=[],
                                  # Query all species and converts to tuples (j.title, j.value) (here title=value)
                                  choices=[(j.species, j.species) for j in FosterSpecies.query.all()],
                                  widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())

    areas = SelectMultipleField('Area', validators=[],
                                # Query all areas and converts to tuples (i.title, i.value) (here title=value)
                                choices=[(i.area, i.area) for i in Area.query.all()],
                                widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput()
                                )
    submit = SubmitField('Search')


class SearchVolunteerForm(FlaskForm):
    fname = StringField('Fist Name')
    lname = StringField('Last Name')
    dial_code = StringField('Phone', validators=[Regexp("^[0-9]{2}$|^[0-9]{3}$", message="Not a valid dial code."), Optional()])
    phone_number = StringField('Number', validators=[Regexp("^[0-9]{7}$", message="Not a valid phone number."), Optional()])
    submit = SubmitField('Search')


class SearchClinicForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    name = StringField('Clinic Name')
    dial_code = StringField('Phone', validators=[Regexp("^[0-9]{2}$|^[0-9]{3}$", message="Not a valid dial code."), Optional()])
    phone_number = StringField('Number', validators=[Regexp("^[0-9]{7}$", message="Not a valid phone number."), Optional()])
    submit = SubmitField('Search')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Email')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Set New Password')
