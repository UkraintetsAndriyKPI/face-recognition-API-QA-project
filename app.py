from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize the app and load config
app = Flask(__name__)
app.config.from_object('config.Config')  # Ensure config.py exists and is correctly configured

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Import the Blueprint and register it
from views import auth_bp  # Make sure auth_bp is defined in views.py
app.register_blueprint(auth_bp)  # Register the blueprint

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
