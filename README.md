# Foster_Finder

Foster Finder is a Flask application designed to help veterinary clinics and animal shelters find willing foster homes, while also reducing the call frequency for individuals willing to foster.
The application creates a shared list of volunteers between clinics and shelters and cycles volunteers to the end of the list once they have been contacted. The more volunteers added to the pool, the lower the frequency every individual will be contacted.


## Status
Foster Finder is currently under development. The vast majority of core systems are complete and functional.
TO DO:
* Clinic activation request
* Error handling
* Internationalization
* UI\UX


## Overview

#### Primary Models and Their Functionality
The application holds two primary models: Volunteer refers to potential foster homes and Clinic refers to veterinary clinics and animal shelters.

A Volunteer holds first and last name, phone numbers, areas they are willing reach, species they are willing to foster (currently dog, cat and other), the time they were last contacted and a general text with any additional notes.

The only end-user is the Clinic, which holds a name, email, password, phone numbers and the area it is located in.
The Clinic end-user can cycle through a list of active Volunteers filtered by the areas they are willing  to reach (default to Clinic's area) and the species they are willing to foster. Critically, the list is sorted by last time each Volunteer was contacted with recently contacted Volunteers (by any Clinic) at the bottom of the list.
After contacting a Volunteer the user is prompted to either move the Volunteer to the bottom of the list (setting their last contacted time to current time) or to keep the Volunteer's position in the list (in case of no reply, or at Volunteer's request).

#### Additional Functionality
The end-user (Clinic) may also edit its own details as well as register new Volunteers and edit existing Volunteers' details, including setting active\inactive state and setting a Volunteer as black-listed (see below). For editing purposes, a secondary search by name\phone number exists that will include inactive Volunteers.

#### Admins
A Clinic can also be marked as admin, allowing it to edit black-listed Volunteers (including un-setting the black-list option) as well as other Clinics, including sending password resets and giving them the admin status themselves.

#### Black-Listing
A Volunteer marked as black-listed will be treated as inactive for all search purposes and can only be edited by admins.
This option should only be reserved for cases where a Volunteer has been found unfit to foster any animals. Currently users are encouraged to add a note explaining the black-listing, further options to document black-listings may be added in the future.

#### Abuse Prevention
In order to prevent the abuse of this application by anyone who might not have the best interests of animals in mind, Volunteers cannot register directly, but rather have to be added by a Clinic user. The intent of this is using the clinics and shelters as filters, trusting the employees not to add any suspicious or untrustworthy Volunteers.
Similarly, Clinics must be set to active by an admin who will verify their authenticity, in order to register and edit Volunteers (but will have access to passive search features immediately).
Additionally, addresses and fostering records are not saved so Volunteers cannot be targeted by anyone.


## Technologies
* Foster Finder was written with python 3.8 using the Flask framework.
* DB of choice is MySQL for the sole reason that I already had Workbench on my machine.
* ORM of choice is SQLAlchemy for simple and extensive documentation.
* Flask-Migrate is an alembic wrapper for migration management.
* Flask-WTF is a WTForms wrapper, chosen for simple and flexible forms management.


## Installation and Launch
Requires Python 3.8. All dependencies should be available with CLI command `pip install -r requirements.txt`.
Make sure to set your own environment variables in `config.py` for email and recaptcha.
The ADMIN value in `config.py` can be set to a list either manually or with something like python-decouple.
To run development server use CLI command `flask run` in root directory.
For migration management refer to Flask-Migrate [documentation](https://flask-migrate.readthedocs.io/en/latest/).