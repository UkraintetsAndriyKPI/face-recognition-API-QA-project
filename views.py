import os

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import app, db, bcrypt
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    if db.User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user_image_dir = os.path.join("images", username)
    os.makedirs(user_image_dir, exist_ok=True)

    image_path = None

    if 'image' in request.files:
        image_file = request.files['image']

        if image_file.filename != '':
            safe_filename = f"{username}_image.png"
            image_path = os.path.join(user_image_dir, safe_filename)
            image_file.save(image_path)

    new_user = db.User(username=username, password=hashed_password, image=image_path)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "image": image_path}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = db.User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200

@auth_bp.route('/update_image', methods=['POST'])
@jwt_required()
def update_image():
    current_user_id = get_jwt_identity()
    user = db.User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "Користувача не знайдено"}), 404

    user_image_dir = os.path.join("images", user.username)

    if 'image' in request.files:
        image_file = request.files['image']

        # CHECK IF IMAGE HAVE ONLY ONE FACE DETECTED

        if image_file.filename != '':
            safe_filename = f"{user.username}_image.png"
            image_path = os.path.join(user_image_dir, safe_filename)

            os.makedirs(user_image_dir, exist_ok=True)

            image_file.save(image_path)

            user.image = image_path
            db.session.commit()

            return jsonify({"message": "Зображення успішно оновлено", "image": image_path}), 200

    return jsonify({"message": "Зображення не надано"}), 400


@auth_bp.route('/')
def home():
    return "Hello, Flask!"
