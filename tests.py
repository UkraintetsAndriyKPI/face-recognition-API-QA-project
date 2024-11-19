import pytest
from app import app, db, bcrypt
from models import User  # assuming the User model is in app/models.py
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    """Fixture to create a test client."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'testsecret'  # Secret key for JWT

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables
        yield client
        with app.app_context():
            db.drop_all()  # Drop tables after each test


def test_register(client):
    """Test for user registration."""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123'
    })
    json_data = response.get_json()
    assert response.status_code == 201
    assert json_data['message'] == "User registered successfully"
    assert json_data['image'] is None


def test_register_existing_user(client):
    """Test for registering an existing user."""
    user = User(username='existinguser', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'newpassword123'
    })
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data['message'] == "User already exists"


def test_login_success(client):
    """Test successful login."""
    user = User(username='testuser', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    json_data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in json_data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/login', json={
        'username': 'nonexistentuser',
        'password': 'wrongpassword'
    })
    json_data = response.get_json()
    assert response.status_code == 401
    assert json_data['message'] == "Invalid credentials"


@pytest.mark.parametrize('image, expected_message, status_code', [
    (None, "Зображення не надано", 400),
    ("test_image.png", "Зображення успішно оновлено", 200)
])
def test_update_image(client, image, expected_message, status_code):
    """Test updating the image for the logged-in user."""
    user = User(username='testuser', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    # Mock the jwt_required authentication
    with client.session_transaction() as session:
        session['user_id'] = user.id

    data = {}
    if image:
        data['image'] = (open(image, 'rb'), image)

    response = client.post('/update_image', data=data)
    json_data = response.get_json()

    assert response.status_code == status_code
    assert json_data['message'] == expected_message


def test_protected(client):
    """Test accessing a protected route."""
    user = User(username='testuser', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    # Mock the jwt_required authentication
    with client.session_transaction() as session:
        session['user_id'] = user.id

    response = client.get('/protected')
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data['logged_in_as'] == 'testuser'


def test_home(client):
    """Test the home route."""
    response = client.get('/')
    assert response.data == b'Hello, Flask!'
