import os

import cloudinary
import cloudinary.uploader


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_image(file):
    result = cloudinary.uploader.upload(
        file,
        folder="thobic",
        resource_type="image",
    )

    return result["secure_url"]


def upload_image_with_metadata(file):
    """Upload an image and return the persistent URL and Cloudinary ID."""
    result = cloudinary.uploader.upload(
        file,
        folder="thobic/shop-photos",
        resource_type="image",
    )
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
    }


def delete_image(public_id):
    """Delete a previously uploaded image by its Cloudinary public ID."""
    if public_id:
        return cloudinary.uploader.destroy(public_id, resource_type="image")
