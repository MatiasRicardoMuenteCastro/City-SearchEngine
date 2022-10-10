from src.Controllers.searchController import searchBP

from flask import Flask
from flask_cors import CORS

allowed_domain = '*'

app = Flask(__name__)
cors = CORS(app, resources = {r'*':{'origins':allowed_domain}})

app.register_blueprint(searchBP)

app.run(host = "0.0.0.0",port = "49184")

