from main import app
from main.models import *


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Clinic': Clinic,
            'Volunteer': Volunteer,
            'PhoneNumber': PhoneNumber,
            'Area': Area,
            'FosterSpecies': FosterSpecies,
            }
