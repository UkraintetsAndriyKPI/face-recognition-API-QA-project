import os
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db.init_app(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@app.route('/register', methods=['POST'])
def register():
    data = request.form  # Використовуємо request.form для прийому даних з форми
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Створюємо каталог для зображення
    user_image_dir = f"images/{username}"
    os.makedirs(user_image_dir, exist_ok=True)  # Створюємо каталог, якщо його немає

    # Зберігаємо файл зображення, якщо він є
    image_path = None  # Значення за замовчуванням для зображення

    if 'image' in request.files:
        image_file = request.files['image']
        
        if image_file.filename != '':
            # Зберігаємо зображення у вказаному каталозі
            image_path = os.path.join(user_image_dir, image_file.filename)
            image_file.save(image_path)

    # Зберігаємо інформацію про користувача
    new_user = User(username=username, password=hashed_password, image=image_path)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "image": image_path}), 201



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
