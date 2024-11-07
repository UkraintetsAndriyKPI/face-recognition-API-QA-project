import os
from face_checking.face_checking import process_face_image
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app import app, db, bcrypt

@app.route('/register', methods=['POST'])
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

            # CHECK IF IMAGE HAVE ONLY ONE FACE DETECTED ETC
            face_crop_image, amount_of_faces = process_face_image(image_file)

            if amount_of_faces > 1 :
                return jsonify({"message": "Too many faces"}), 400
            elif amount_of_faces == 0:
                return jsonify({"message": "No faces found"}), 400

            safe_filename = f"{username}_image.png"
            image_path = os.path.join(user_image_dir, safe_filename)
            face_crop_image.save(image_path)

    new_user = db.User(username=username, password=hashed_password, image=image_path)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "image": image_path}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid login data"}), 401

@app.route('/user/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = db.User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200

@app.route('/user/update_image', methods=['POST'])
@jwt_required()
def update_image():
    current_user_id = get_jwt_identity()
    user = db.User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    user_image_dir = os.path.join("images", user.username)

    if 'image' in request.files:
        image_file = request.files['image']

        if image_file.filename != '':

            # CHECK IF IMAGE HAVE ONLY ONE FACE DETECTED ETC
            face_crop_image, amount_of_faces = process_face_image(image_file)

            if amount_of_faces > 1 :
                return jsonify({"message": "Too many faces"}), 400
            elif amount_of_faces == 0:
                return jsonify({"message": "No faces found"}), 400

            # IMAGE PATH BUILDING
            safe_filename = f"{user.username}_image.png"
            image_path = os.path.join(user_image_dir, safe_filename)
            os.makedirs(user_image_dir, exist_ok=True)

            face_crop_image.save(image_path)

            user.image = image_path
            db.session.commit()

            return jsonify({"message": "Image updated successfully", "image": image_path}), 200

    return jsonify({"message": "No image provided"}), 400


@app.route('/')
def home():
    return "Hello, Flask!"
