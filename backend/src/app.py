from Controllers.searchController import searchBP

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

app.register_blueprint(searchBP)

app.run(port = 5001,debug = True)

