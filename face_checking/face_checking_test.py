from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
import face_checking
import unittest

class TestFaceRecognitionModule(unittest.TestCase):

    @patch('face_recognition.face_locations')
    @patch('face_recognition.load_image_file')
    def test_get_face_amount(self, mock_load_image, mock_face_locations):
        mock_image = MagicMock()
        mock_load_image.return_value = mock_image
        mock_face_locations.return_value = [(0, 0, 10, 10), (10, 10, 20, 20)]  # Two faces

        result = face_checking.get_face_amount("test_image.jpg")

        self.assertEqual(result, 2, "Expected 2 faces to be detected.")
        mock_load_image.assert_called_once_with("test_image.jpg")
        mock_face_locations.assert_called_once_with(mock_image)

    @patch('face_recognition.face_locations')
    @patch('face_recognition.load_image_file')
    def test_process_face_image(self, mock_load_image, mock_face_locations):
        mock_image_array = np.zeros((100, 100, 3), dtype=np.uint8)  # 100x100 pixels, 3 channels (RGB)
        mock_load_image.return_value = mock_image_array
        mock_face_locations.return_value = [(0, 20, 20, 0)]  # One face

        face_image, face_count = face_checking.process_face_image("test_image.jpg")

        self.assertIsInstance(face_image, Image.Image, "Returned face image should be an instance of PIL.Image.")
        self.assertEqual(face_count, 1, "Expected exactly one face.")


    @patch('face_recognition.face_encodings', side_effect=IndexError)
    @patch('face_recognition.load_image_file')
    def test_compare_faces_no_face(self, mock_load_image, mock_face_encodings):
        result = face_checking.compare_faces("face1.jpg", "face2.jpg")

        self.assertFalse(result, "Should return False when no faces are found.")
        mock_face_encodings.assert_called()

if __name__ == "__main__":
    unittest.main()
