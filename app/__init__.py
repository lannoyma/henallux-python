from flask import Flask
from .views import app
from . import models

models.db.init_app(app)
#with app.app_context():
#    models.init_db()
