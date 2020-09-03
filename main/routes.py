from datetime import datetime

from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import or_
from werkzeug.urls import url_parse
from werkzeug.utils import redirect

from main import app, db
from flask import render_template, flash, url_for, request

from main.forms import LoginForm, ClinicForm, VolunteerForm, QueryForm, SearchVolunteerForm, SearchClinicForm
from main.models import Clinic, Area, Volunteer, PhoneNumber, FosterSpecies


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    search_form = SearchVolunteerForm(prefix='search_form')
    param_form = QueryForm(prefix='param_form')

    # Calls the search function when form is submitted
    if search_form.validate_on_submit() and search_form.data:
        return search_volunteers(search_form.fname.data, search_form.lname.data,
                                 search_form.dial_code.data, search_form.phone_number.data)

    if param_form.validate_on_submit():
        # Resets page on search
        page = 1
    else:
        # Sets page from args for next\prev
        page = request.args.get('page', 1, type=int)

    if param_form.is_submitted() and param_form.species.data:
        # Called when submitting search form
        # Initializes species args for query.filter by user search parameters
        vol_species = [s for s in param_form.species.data]
    elif request.args.get('species'):
        # Called when using next\prev url
        # (P)re-populates form field and initializes species args for query.filter from args passed in next\prev url
        param_form.species.data = request.args.getlist('species')
        vol_species = request.args.getlist('species')
    else:
        # Called when passing empty form
        # Initializes species args for query.filter to all species as default
        vol_species = [s.species for s in FosterSpecies.query.all()]

    if param_form.is_submitted() and param_form.areas.data:
        # Called when submitting search form
        # Initializes areas args for query.filter by user search parameters
        vol_areas = [a for a in param_form.areas.data]
    elif request.args.getlist('areas'):
        # Called when using next\prev url
        # (P)re-populates form field and initializes species args for query.filter from args passed in next\prev url
        param_form.areas.data = request.args.getlist('areas')
        vol_areas = request.args.getlist('areas')
    else:
        # Called when passing empty form
        # Initializes areas args for query.filter to clinic area as default
        vol_areas = current_user.area_name if current_user.area_name else [a.area for a in Area.query.all()]
        param_form.areas.data = vol_areas

    volunteers = Volunteer.query\
        .join(Volunteer.species)\
        .join(Volunteer.areas)\
        .filter(FosterSpecies.species.in_(vol_species))\
        .filter(Area.area.in_(vol_areas))\
        .filter(Volunteer.active)\
        .filter(Volunteer.black_listed.is_(False))\
        .distinct()\
        .order_by(Volunteer.last_contacted)\
        .paginate(page, 1, False)

    next_url = url_for('index', page=volunteers.next_num, species=param_form.species.data, areas=param_form.areas.data)\
        if volunteers.has_next else None
    prev_url = url_for('index', page=volunteers.prev_num, species=param_form.species.data, areas=param_form.areas.data)\
        if volunteers.has_prev else None
    return render_template('index.html', param_form=param_form, search_form=search_form, title="Made It",
                           volunteers=volunteers.items, next_url=next_url, prev_url=prev_url)


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

    form = ClinicForm()
    # Generate raw list of all areas to choose)
    choices = Area.query.all()
    # Turns choices into tuples (i.title, i.value) (title and value identical in this case)
    form.area.choices = [(i.area, i.area) for i in choices]
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


@app.route('/edit-profile', methods=['GET', 'POST'])
@app.route('/<id>/edit-clinic', methods=['GET', 'POST'])
@login_required
def edit_clinic(id):
    if id:
        form = ClinicForm(obj=Clinic.query.filter_by(id=int(id)))
    else:
        form = ClinicForm(obj=current_user)

    # Removes email field, as it is pk and password change happens in specific page
    del form.email
    del form.password
    del form.password2
    # Queries phone numbers for use in pre-population and comparison
    main_number = PhoneNumber.query.filter_by(clinic_id=current_user.id, primary_contact=True).first()
    emergency_number = PhoneNumber.query.filter_by(clinic_id=current_user.id, primary_contact=False).first()

    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.area = form.area.data
            # Setter used for encryption
            # current_user.set_password(form.password.data)

            # Generates PhoneNumber(s) from form
            new_main_number = PhoneNumber(dial_code=form.main_number.dial_code.data,
                                          phone_number=form.main_number.phone_number.data,
                                          clinic_id=current_user.id,
                                          primary_contact=True)
            new_emergency_number = PhoneNumber(dial_code=form.emergency_number.dial_code.data,
                                               phone_number=form.emergency_number.phone_number.data,
                                               clinic_id=current_user.id,
                                               primary_contact=False)

            # Prevents duplicates that can't be caught by PhoneForm.validate
            if new_main_number == new_emergency_number:
                new_emergency_number = None

            # Checks for changes and updates the phone objects accordingly
            if new_main_number.not_empty():
                # Checks if there is a number to update
                if main_number:
                    main_number.edit(new_main_number)
                # Else adds it
                else:
                    db.session.add(new_main_number)
            else:
                form.main_number.phone_number.errors.append("Must have a contact number.")
                flash(form.errors)
                return render_template('edit_clinic.html', title='Edit Profile', form=form)

            if new_emergency_number.not_empty():
                if emergency_number:
                    emergency_number.edit(new_emergency_number)
                else:
                    db.session.add(new_emergency_number)
            # Given empty field will delete previous number if there is one
            else:
                if emergency_number:
                    db.session.delete(emergency_number)

            db.session.commit()
            flash('Edit successful')
            return redirect(url_for('index'))

        else:
            flash(form.errors)
            return render_template('edit_clinic.html', title='Edit Profile', form=form)
    else:
        # Pre-populates phone numbers manually because nested forms have no equivalent Clinic attribute
        if main_number is not None:
            form.main_number.dial_code.data = main_number.dial_code
            form.main_number.phone_number.data = main_number.phone_number
            form.main_number.clinic_id.data = current_user.id
            form.main_number.primary_contact.data = main_number.primary_contact

        if emergency_number is not None:
            form.emergency_number.dial_code.data = emergency_number.dial_code
            form.emergency_number.phone_number.data = emergency_number.phone_number
            form.emergency_number.clinic_id.data = current_user.id
            form.emergency_number.primary_contact.data = emergency_number.primary_contact

        return render_template('edit_clinic.html', title='Edit Profile', form=form)


@app.route('/add-volunteer', methods=['GET', 'POST'])
@login_required
def add_volunteer():
    form = VolunteerForm()
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

    # Queries volunteer object through id to populate most fields
    vol_edit = Volunteer.query.filter_by(id=id).first()
    # obj=vol_edit pre-populates fields with volunteer data
    form = VolunteerForm(obj=vol_edit)

    # Queries the phone numbers through volunteer object (by primary true/false) to pre-populate phone fields
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

            # Generates PhoneNumber(s) from form
            new_number1 = PhoneNumber(dial_code=form.phone1.dial_code.data,
                                      phone_number=form.phone1.phone_number.data,
                                      volunteer_id=int(vol_edit.id),
                                      primary_contact=form.phone1.primary_contact.data)
            new_number2 = PhoneNumber(dial_code=form.phone2.dial_code.data,
                                      phone_number=form.phone2.phone_number.data,
                                      volunteer_id=int(vol_edit.id),
                                      primary_contact=form.phone2.primary_contact.data)

            # Prevents duplicates that can't be caught by PhoneForm.validate
            if new_number1 == new_number2:
                new_number2 = None

            # Default to phone1 being primary if both numbers are marked as either primary or not
            if new_number1.primary_contact == new_number2.primary_contact:
                new_number1.primary_contact = True
                new_number2.primary_contact = False

            # Checks for changes and updates the phone objects accordingly
            if new_number1.not_empty():
                # Updates the old phone number if there was one.
                if phone1:
                    phone1.edit(new_number1)
                # Adds a new phone number if there is no original number to edit.
                else:
                    # Saves new_number1 to variable for use in new_number2 validation
                    phone1 = new_number1
                    db.session.add(phone1)
            elif not new_number1.not_empty() and new_number2.not_empty():
                # Deletes phone number if fields are cleared after making sure it exits.
                if phone1:
                    db.session.delete(phone1)
                # Changes the remaining number to be primary_contact
                # Uses new_number2 because it was not yet passed to phone2
                new_number2.primary_contact = True
            else:
                form.phone1.phone_number.errors.append("Must have at least one phone number.")
                # Stops the form from being processed. Will not raise this error unless all other errors are fixed.
                return render_template('edit_volunteer.html', title='Edit Volunteer', form=form)

            if new_number2.not_empty():
                # Updates the old phone number if there was one.
                if phone2:
                    phone2.edit(new_number2)
                # Adds a new phone number if there is no original number to edit.
                else:
                    db.session.add(new_number2)
            # Deletes phone number if fields are cleared
            elif not new_number2.not_empty() and new_number1.not_empty():
                # First checks that phone2 existed in the first place
                if phone2:
                    db.session.delete(phone2)
                # Ensures the remaining number is primary_contact
                # Uses phone1 because new_number1 was already passed to it
                phone1.primary_contact = True

            db.session.commit()
            flash('Volunteer '+vol_edit.fname + ' ' + vol_edit.lname + ' updated successfully.')
            return render_template('edit_volunteer.html', title='Edit Volunteer', form=form)

        else:
            flash(form.errors)
            return render_template('edit_volunteer.html', title='Edit Volunteer', form=form)

    else:

        # Pre-populates phone numbers manually because nested forms have no equivalent Volunteer attribute
        if phone1 is not None:
            form.phone1.dial_code.data = phone1.dial_code
            form.phone1.phone_number.data = phone1.phone_number
            form.phone1.primary_contact.data = phone1.primary_contact

        form.phone1.volunteer_id.data = vol_edit.id

        if phone2 is not None:
            form.phone2.dial_code.data = phone2.dial_code
            form.phone2.phone_number.data = phone2.phone_number
            form.phone2.primary_contact.data = phone2.primary_contact

        form.phone2.volunteer_id.data = vol_edit.id

        return render_template('edit_volunteer.html', title='Edit Volunteer', id=int(id), form=form)


@login_required
def search_volunteers(fname, lname, dial_code, phone_num):

    search_form = SearchVolunteerForm(prefix='search_form')

    # Resets the search page on search from inside the search page
    if search_form.validate_on_submit() and search_form.data:
        return search_volunteers(search_form.fname.data, search_form.lname.data,
                                 search_form.dial_code.data, search_form.phone_number.data)

    if search_form.validate_on_submit():
        # Sets pagination to 1 on new search
        page = 1
    else:
        # Sets page from args for next\prev
        page = request.args.get('page', 1, type=int)

    # Search by phone if provided
    query = Volunteer.query\
        .join(Volunteer.phone_numbers)\
        .filter(PhoneNumber.dial_code == dial_code)\
        .filter(PhoneNumber.phone_number == phone_num)\
        .distinct() if dial_code and phone_num else None

    # Search by fname and\or lname if phone not provided or not found
    if not query or not query.first():
        if not fname or not lname:
            query = Volunteer.query\
                .filter(or_(Volunteer.fname.ilike(fname), Volunteer.lname.ilike(lname)))\
                .distinct()
        else:
            query = Volunteer.query\
                .filter(Volunteer.fname.ilike(fname))\
                .filter(Volunteer.lname.ilike(lname))\
                .distinct()

    search_results = query.paginate(page, 10, False)

    next_url = url_for('search_volunteers', page=search_results.next_num)\
        if search_results.has_next else None
    prev_url = url_for('search_volunteers', page=search_results.prev_num)\
        if search_results.has_prev else None

    return render_template('search_volunteer.html', search_form=search_form, search_results=search_results.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def search_clinics():

    form = SearchClinicForm()
    email = form.email.data
    name = form.name.data
    dial_code = form.dial_code.data
    phone_num = form.phone_number.data

    if form.validate_on_submit():
        # Sets pagination to 1 on new search
        page = 1
    else:
        # Sets page from args for next\prev
        page = request.args.get('page', 1, type=int)

    # Search by phone separately to filter with dial_code and phone_number
    query = Clinic.query\
        .join(Clinic.phone_numbers)\
        .filter(PhoneNumber.dial_code == dial_code)\
        .filter(PhoneNumber.phone_number == phone_num)\
        .distinct() if dial_code and phone_num else None

    # If phone is not provided or not found searches by name and email, defaults to all
    if not query or not query.first():
        query = Clinic.query\
            .filter(or_(Clinic.name.ilike(name), Clinic.email.ilike(email)))\
            .distinct() if name else Clinic.query

    search_results = query.paginate(page, 10, False)

    next_url = url_for('search_clinics', page=search_results.next_num)\
        if search_results.has_next else None
    prev_url = url_for('search_clinics', page=search_results.prev_num)\
        if search_results.has_prev else None

    return render_template('search_clinic.html', form=form, search_results=search_results.items,
                           next_url=next_url, prev_url=prev_url)


# Endpoint for updating volunteer's last_contacted
@app.route('/<id>/cycle', methods=['GET', 'POST'])
@login_required
def cycle_to_bottom(id):
    volunteer = Volunteer.query.filter_by(id=id).first()
    volunteer.last_contacted = datetime.utcnow()
    db.session.commit()
    return '', 204
