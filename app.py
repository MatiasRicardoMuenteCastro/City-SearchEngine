from src.Controllers.searchController import searchBP

from flask import Flask
from flask_cors import CORS
from waitress import serve
import os

allowed_domain = '*'
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
cors = CORS(app, resources = {r'*':{'origins':allowed_domain}})

app.register_blueprint(searchBP)

serve(app, host = "0.0.0.0",port = port)
#app.run(port = port)

