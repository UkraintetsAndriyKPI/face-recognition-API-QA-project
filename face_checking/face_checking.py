from PIL import Image
import face_recognition

def open_image(image_path):
    return Image.open(image_path)

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

def compare_faces(face_img1, face_img2):
    image1 = face_recognition.load_image_file(face_img1)
    image2 = face_recognition.load_image_file(face_img2)
    try:
        image1_encoding = face_recognition.face_encodings(image1)[0]
        image2_encoding = face_recognition.face_encodings(image2)[0]
    except IndexError:
        print("I wasn't able to locate any faces in at least one of the images. \
              Check the image files. Aborting...")
        return False
    return face_recognition.compare_faces(image1_encoding, image2_encoding)
