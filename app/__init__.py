from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from flask_migrate import Migrate
import os



# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config.from_object(Config)

from app.db import db  # Ensure db is imported after app is created
db.init_app(app)  # Register SQLAlchemy with Flask
migrate = Migrate(app, db)  # ✅ Initialize Flask-Migrate

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Import and register routes AFTER initializing db
from app.routes.auth_routes import auth_routes 
from app.routes.expenses_routes import expenses_routes  # ✅ Import expense routes
from app.routes.income_routes import income_routes  # ✅ Import expense routes
from app.routes.ai_routes import ai_routes
from app.routes.budget_routes import budget_routes

app.register_blueprint(auth_routes, url_prefix="/api/auth")
app.register_blueprint(expenses_routes, url_prefix="/api")
app.register_blueprint(income_routes, url_prefix="/api")
app.register_blueprint(ai_routes, url_prefix="/api")
app.register_blueprint(budget_routes, url_prefix="/api")

# Define a Default Route
def home():
    return {"message": "Welcome to the Expense Tracker API!"}, 200

app.add_url_rule("/", "home", home)


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(os.getcwd(), "static"), filename)  # ✅ Ensures Flask finds the correct folder


# Create the database inside app context
def create_database():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_database()
    app.run(debug=True)