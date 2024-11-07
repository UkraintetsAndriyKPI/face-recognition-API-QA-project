from PIL import Image
import face_recognition

def get_face_amount(image_file):
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)
    return len(face_locations)

def process_face_image(image_file):
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)

    top, right, bottom, left = face_locations[0]
    face_image_array = image[top:bottom, left:right]
    face_image = Image.fromarray(face_image_array)
    return (face_image, len(face_locations))
