import logging
from rest_framework import serializers
from .models import DiseaseHistory, FeedbackRating, EditHistory, DeleteHistory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiseaseHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the DiseaseHistory model.
    Handles the conversion between DiseaseHistory model instances and JSON representations.
    """
    class Meta:
        model = DiseaseHistory
        fields = '__all__'  # Include all fields from the DiseaseHistory model

    def validate(self, data):
        """Custom validation for DiseaseHistory model fields."""
        logging.info("Validating DiseaseHistory data")
        # You can add more custom validation logic here if needed
        return data


class FeedbackRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for the FeedbackRating model.
    Converts FeedbackRating model instances to and from JSON format.
    """
    class Meta:
        model = FeedbackRating
        fields = '__all__'  # Include all fields from the FeedbackRating model

    def validate(self, data):
        """Custom validation for FeedbackRating fields."""
        logging.info("Validating FeedbackRating data")
        # Custom logic for feedback validation can go here
        return data


class EditHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the EditHistory model.
    Converts EditHistory model instances to and from JSON format.
    """
    class Meta:
        model = EditHistory
        fields = '__all__'  # Include all fields from the EditHistory model

    def validate(self, data):
        """Custom validation for EditHistory model fields."""
        logging.info("Validating EditHistory data")
        # Custom validation for the EditHistory model can go here
        return data


class DeleteHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the DeleteHistory model.
    Converts DeleteHistory model instances to and from JSON format.
    """
    class Meta:
        model = DeleteHistory
        fields = '__all__'  # Include all fields from the DeleteHistory model

    def validate(self, data):
        """Custom validation for DeleteHistory model fields."""
        logging.info("Validating DeleteHistory data")
        # Custom logic for validating delete history fields
        return data


class ImageUploadSerializer(serializers.Serializer):
    """
    Serializer for handling image uploads.
    Validates uploaded image files and ensures the correct format.
    """
    image = serializers.ImageField()

    def validate_image(self, image):
        """
        Custom validation for uploaded images:
        - Ensures the image is either JPEG or PNG.
        - Logs invalid image formats for further review.
        """
        valid_mime_types = ['image/jpeg', 'image/png']

        # Log the type of image being validated
        logging.info(f"Validating image with MIME type: {image.content_type}")

        # Check if the image content type is valid
        if image.content_type not in valid_mime_types:
            # Log the error if the MIME type is invalid
            logging.error(f"Unsupported image format: {image.content_type} (only JPEG and PNG are supported)")
            raise serializers.ValidationError("Unsupported file format")

        # Log successful validation
        logging.info(f"Image validated successfully: {image.name}")
        return image
