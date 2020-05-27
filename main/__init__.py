from flask import Flask

from config import Config


app = Flask(__name__)
app.config.from_object(Config)


# import at bottom to avoid cyclic imports
from main import routes
