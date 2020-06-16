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
    form.area.choices = [(i.areas, i.areas) for i in choices]
    if form.validate_on_submit():
        clinic = Clinic(email=form.email.data, name=form.name.data, area_name=form.area.data)
        # Password is set after constructor for encryption.
        clinic.set_password(form.password.data)

        # Generates PhoneNumber(s) from form and assigns them to the new clinic
        main_number = PhoneNumber(dial_code=form.main_number.dial_code.data,
                                  phone_number=form.main_number.phone_number.data,
                                  primary_contact=True)
        emergency_number = PhoneNumber(dial_code=form.emergency_number.dial_code.data,
                                       phone_number=form.emergency_number.phone_number.data,
                                       primary_contact=False)

        clinic.phone_numbers.append(main_number)
        clinic.phone_numbers.append(emergency_number)
        db.session.add(clinic)
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

    if request.method == 'POST':
        if form.validate_on_submit():
            vol = Volunteer(fname=form.fname.data, lname=form.lname.data)
            # Adds the selected areas to the vol object
            for area in form.areas.data:
                # Appends the areas as queried from the db (db.relationship represents a List)
                vol.areas.append(Area.query.filter_by(area=area).first())

            # Adds the selected species to the vol object
            for species in form.species.data:
                # Appends the species as queried from the db (db.relationship represents a List)
                vol.species.append(FosterSpecies.query.filter_by(species=species).first())

            # Generates PhoneNumber(s) from form and assigns them to the new volunteer
            number1 = PhoneNumber(dial_code=form.phone1.dial_code.data,
                                  phone_number=form.phone1.phone_number.data,
                                  primary_contact=form.phone1.primary_contact.data)
            number2 = PhoneNumber(dial_code=form.phone2.dial_code.data,
                                  phone_number=form.phone2.phone_number.data,
                                  primary_contact=form.phone2.primary_contact.data)

            vol.phone_numbers.append(number1)
            vol.phone_numbers.append(number2)
            db.session.add(vol)
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
    # Queries volunteer object through id to populate non-foreignkey fields
    vol_edit = Volunteer.query.filter_by(id=id).first()
    form = EditVolunteerForm(obj=vol_edit)
    #form.areas.data = vol_edit.areas
    #form.species.default = vol_edit.species

    # Queries the phone numbers through volunteer object (by primary true/false) to populate phone fields
    phone1 = PhoneNumber.query.filter_by(volunteer_id=vol_edit.id, primary_contact=True).first()
    phone2 = PhoneNumber.query.filter_by(volunteer_id=vol_edit.id, primary_contact=False).first()

    if request.method == 'POST':
        if form.validate_on_submit():
            vol_edit.fname = form.fname.data
            vol_edit.lname = form.lname.data
            vol_edit.active = form.active.data
            vol_edit.black_listed = form.black_listed.data
            vol_edit.notes = form.notes.data

            # Replaces old vol_edit.areas with new areas list
            new_areas = []
            for area in form.areas.data:
                # Appends the areas as queried from the db (db.relationship represents a List)
                new_areas.append(Area.query.filter_by(area=area).first())

            vol_edit.areas = new_areas

            # Replaces old vol_edit.species with new species list
            new_species = []
            for species in form.species.data:
                # Appends the species as queried from the db (db.relationship represents a List)
                new_species.append(FosterSpecies.query.filter_by(species=species).first())

            vol_edit.species = new_species

            # Generates PhoneNumber(s) from form and assigns them to the volunteer
            new_number1 = PhoneNumber(dial_code=form.phone1.dial_code.data,
                                      phone_number=form.phone1.phone_number.data,
                                      volunteer_id=vol_edit.id,
                                      primary_contact=form.phone1.primary_contact.data)
            new_number2 = PhoneNumber(dial_code=form.phone2.dial_code.data,
                                      phone_number=form.phone2.phone_number.data,
                                      volunteer_id=vol_edit.id,
                                      primary_contact=form.phone2.primary_contact.data)

            # Checks for changes and updates the phone objects accordingly
            if phone1 != new_number1 and phone1 is not None:
                phone1.edit(new_number1)
            if phone2 != new_number2 and phone2 is not None:
                phone2.edit(new_number2)

            db.session.commit()
            flash('Volunteer '+vol_edit.fname + ' ' + vol_edit.lname + ' registered successfully.')
            return render_template('edit_volunteer.html', title='Add Volunteer', form=form)

        else:
            flash(form.errors)
            return render_template('edit_volunteer.html', title='Add Volunteer', form=form)

    else:

        if phone1 is not None:
            form.phone1.dial_code.data = phone1.dial_code
            form.phone1.phone_number.data = phone1.phone_number
            form.phone1.primary_contact.data = phone1.primary_contact

        if phone2 is not None:
            form.phone2.dial_code.data = phone2.dial_code
            form.phone2.phone_number.data = phone2.phone_number
            form.phone2.primary_contact.data = phone2.primary_contact

        return render_template('edit_volunteer.html', title='Add Volunteer', form=form)
