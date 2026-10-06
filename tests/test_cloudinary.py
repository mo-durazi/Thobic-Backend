import os

from fastapi.testclient import TestClient

from main import app
from services.cloudinary_service import upload_image


client = TestClient(app)


def test_upload_image():
    image_path = "tests/test-image.jpg"

    assert os.path.exists(image_path)

    image_url = upload_image(image_path)

    assert image_url
    assert image_url.startswith("https://res.cloudinary.com/")


def test_upload_material_image():
    image_path = "tests/test-image.jpg"

    assert os.path.exists(image_path)

    with open(image_path, "rb") as image_file:
        response = client.post(
            "/api/materials/upload-image",
            files={
                "image": (
                    "test-image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 401