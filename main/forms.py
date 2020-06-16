from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, \
    SelectMultipleField, FormField, widgets, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from main.models import Clinic, Area, FosterSpecies


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PhoneForm(FlaskForm):
    dial_code = IntegerField('Phone')
    phone_number = IntegerField('Number')
    primary_contact = BooleanField('Primary Phone Number')
    # I have no idea if this is actually needed
    # TODO: check
    submit = SubmitField('Add')

    # Need to override the constructor of nested forms to disable csrf
    # Because for some fucking reason they aren't validated by the parent form
    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(PhoneForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)

    """
    def validate_phone_number(self, dial_code, phone_number):
        number = PhoneNumber.query.filter_by(dial_code=dial_code.data, phone_number=phone_number.data)
        if number is not None:
            raise ValidationError('This phone number already exists in the system.')
    """


class RegistrationForm(FlaskForm):
    name = StringField('Organisation Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    main_number = FormField(PhoneForm)
    emergency_number = FormField(PhoneForm)
    area = SelectField('Area', validators=[DataRequired()])
    submit = SubmitField('Register')

    # Called by default with pattern validate_<field_name>
    def validate_email(self, email):
        clinic = Clinic.query.filter_by(email=email.data).first()
        if clinic is not None:
            raise ValidationError('This email has already been registered.')


class AddVolunteerForm(FlaskForm):
    fname = StringField('First name', validators=[DataRequired()])
    lname = StringField('Last name', validators=[DataRequired()])
    phone1 = FormField(PhoneForm)
    phone2 = FormField(PhoneForm)
    areas = SelectMultipleField('Area', validators=[DataRequired()],
                                choices=[(i.area, i.area) for i in Area.query.all()],
                                widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    species = SelectMultipleField('Can Foster:', validators=[DataRequired()],
                                  choices=[(j.species, j.species) for j in FosterSpecies.query.all()],
                                  widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    notes = TextAreaField('Notes')
    submit = SubmitField('Add')


# Same as AddVolunteer but with extra arguments for deactivation and blacklisting
class EditVolunteerForm(FlaskForm):
    fname = StringField('First name', validators=[DataRequired()])
    lname = StringField('Last name', validators=[DataRequired()])
    phone1 = FormField(PhoneForm)
    phone2 = FormField(PhoneForm)
    areas = SelectMultipleField('Area', validators=[DataRequired()],
                                # Query all areas and converts to touples (i.title, i.value) (here title=value)
                                choices=[(i.area, i.area) for i in Area.query.all()],
                                widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    species = SelectMultipleField('Can Foster:', validators=[DataRequired()],
                                  # Query all species and converts to touples (i.title, i.value) (here title=value)
                                  choices=[(j.species, j.species) for j in FosterSpecies.query.all()],
                                  widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    notes = TextAreaField('Notes')
    active = BooleanField('Active')
    black_list = BooleanField('Black List')
    submit = SubmitField('Add')
