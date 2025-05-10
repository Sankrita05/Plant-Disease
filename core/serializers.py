from rest_framework import serializers
from .models import DiseaseHistory, FeedbackRating, EditHistory, DeleteHistory

class DiseaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseHistory
        fields = '__all__'


class FeedbackRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackRating
        fields = '__all__'



class EditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EditHistory
        fields = '__all__'


class DeleteHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeleteHistory
        fields = '__all__'


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, image):
        valid_mime_types = ['image/jpeg', 'image/png']
        if image.content_type not in valid_mime_types:
            raise serializers.ValidationError("Unsupported file format")
        return image