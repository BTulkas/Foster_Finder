from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import redirect

from main import app, db
from flask import render_template, flash, url_for, request

from main.forms import LoginForm, RegistrationForm, AddVolunteerForm, EditVolunteerForm
from main.models import Clinic, Area, Volunteer, PhoneNumber, FosterSpecies


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title="Made It")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Checks that a logged user didn't somehow reach the login page.
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form_to_render = LoginForm()

    # Checks user credentials on a submitted form.
    if form_to_render.validate_on_submit():
        clinic = Clinic.query.filter_by(email=form_to_render.email.data).first()
        # If the user doesn't exist or the password doesn't match, throws error and returns to login.
        if clinic is None or not clinic.check_password(form_to_render.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))

        # If everything checks out, log the user in (saves details to current_user).
        login_user(clinic, remember=form_to_render.remember_me.data)
        next_page = request.args.get('next')
        # Checks that next_page was not set to an absolute URL to prevent cross-site attacks
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    # If the request is GET, renders the login template.
    return render_template('login.html', title='Sign In', form=form_to_render)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    # Generate raw list of all areas to choose)
    choices = Area.query.all()
    # Turns choices into touples (i.title, i.value) (title and value identical in this case)
    form.area.choices = [(i.area, i.area) for i in choices]
    if form.validate_on_submit():
        clinic = Clinic(email=form.email.data, name=form.name.data, area_name=form.area.data)
        # Password is set after constructor for encryption.
        clinic.set_password(form.password.data)

        # Generates PhoneNumber(s) from form and assigns them to the new clinic
        main_number = PhoneNumber(dial_code=form.main_number.dial_code.data,
                                  phone_number=form.main_number.phone_number.data,
                                  volunteer_id=current_user.id)
        emergency_number = PhoneNumber(dial_code=form.emergency_number.dial_code.data,
                                       phone_number=form.emergency_number.phone_number.data,
                                       volunteer_id=current_user.id)

        db.session.add(clinic)
        db.session.add(main_number)
        db.session.add(emergency_number)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)


@app.route('/add_volunteer', methods=['GET', 'POST'])
@login_required
def add_volunteer():
    form = AddVolunteerForm()

    # Generate choices for SelectFields
    # Query all areas\species and converts into touples (i.title, i.value) (title and value identical in this case)
    form.area.choices = [(i.area, i.area) for i in Area.query.all()]
    form.species.choices = [(j.species, j.species) for j in FosterSpecies.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            vol = Volunteer(fname=form.fname.data, lname=form.lname.data)
            # Adds the selected areas to the vol object
            for area in form.area.data:
                # Appends the areas as queried from the db (db.relationship represents a List)
                vol.areas.append(Area.query.filter_by(area=area).first())

            # Adds the selected species to the vol object
            for species in form.species.data:
                # Appends the species as queried from the db (db.relationship represents a List)
                vol.species.append(FosterSpecies.query.filter_by(species=species).first())

            db.session.add(vol)

            # Generates PhoneNumber(s) from form and assigns them to the new volunteer
            number1 = PhoneNumber(dial_code=form.phone1.dial_code.data,
                                  phone_number=form.phone1.phone_number.data,
                                  volunteer_id=vol.id)
            number2 = PhoneNumber(dial_code=form.phone2.dial_code.data,
                                  phone_number=form.phone2.phone_number.data,
                                  volunteer_id=vol.id)

            db.session.add(number1)
            db.session.add(number2)
            db.session.commit()
            flash('Volunteer '+vol.fname + ' ' + vol.lname + ' registered successfully.')
            return render_template('add_volunteer.html', title='Add Volunteer', form=form)

        else:
            flash(form.errors)
            return render_template('add_volunteer.html', title='Add Volunteer', form=form)

    else:
        return render_template('add_volunteer.html', title='Add Volunteer', form=form)


@app.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_volunteer(id):
    form = EditVolunteerForm()
    vol_edit = Volunteer.query.filter_by(id=id).first()

    # Generate choices for SelectFields
    # Query all areas\species and converts into touples (i.title, i.value) (title and value identical in this case)
    form.area.choices = [(i.area, i.area) for i in Area.query.all()]
    form.species.choices = [(j.species, j.species) for j in FosterSpecies.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            vol = Volunteer(fname=form.fname.data, lname=form.lname.data)
            # Adds the selected areas to the vol object
            for area in form.area.data:
                # Appends the areas as queried from the db (db.relationship represents a List)
                vol.areas.append(Area.query.filter_by(area=area).first())

            # Adds the selected species to the vol object
            for species in form.species.data:
                # Appends the species as queried from the db (db.relationship represents a List)
                vol.species.append(FosterSpecies.query.filter_by(species=species).first())

            db.session.add(vol)

            # Generates PhoneNumber(s) from form and assigns them to the new volunteer
            number1 = PhoneNumber(dial_code=form.phone1.dial_code.data,
                                  phone_number=form.phone1.phone_number.data,
                                  volunteer_id=vol.id)
            number2 = PhoneNumber(dial_code=form.phone2.dial_code.data,
                                  phone_number=form.phone2.phone_number.data,
                                  volunteer_id=vol.id)

            db.session.add(number1)
            db.session.add(number2)
            db.session.commit()
            flash('Volunteer '+vol.fname + ' ' + vol.lname + ' registered successfully.')
            return render_template('edit_volunteer.html', title='Add Volunteer', form=form)

        else:
            flash(form.errors)
            return render_template('edit_volunteer.html', title='Add Volunteer', form=form)

    else:
        form.fname.data = vol_edit.fname
        form.lname.data = vol_edit.lname
        #form.phone1.data = PhoneNumber.query.filter_by(volunteer_id=vol_edit.id, primary_contact=True).first()
        form.phone1.dial_code.data = PhoneNumber.query.filter_by(volunteer_id=vol_edit.id).first().dial_code
        #form.phone2.data = PhoneNumber.query.filter_by(volunteer_id=vol_edit.id)[1]
        form.area.data = vol_edit.areas
        form.species.data = vol_edit.can_foster
        form.active.data = vol_edit.active
        form.black_list.data = vol_edit.black_listed
        form.notes.data = vol_edit.notes
        return render_template('edit_volunteer.html', title='Add Volunteer', form=form)
