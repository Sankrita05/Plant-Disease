import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage

from .email_utils import send_detection_report_email
from .models import *
from .serializers import *
from .model_utils import *


model = load_model()

class PredictImageView(APIView):
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)

        if serializer.is_valid():
            image = serializer.validated_data['image']

            # Save image
            filename = default_storage.save(f"detection/{image.name}", image)
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            image_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

            # Check Quality of Image
            if not is_image_quality_sufficient(image_path):
                return Response(
                    {"error": "Image quality insufficient, please upload a clearer image."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Predict disease
            try:
                img_tensor = preprocess_image(image_path)
                prediction = predict_image(img_tensor, model)

                # Parse the prediction into crop and disease
                parsed_prediction = parse_prediction(prediction)
                crop = parsed_prediction["crop"]
                disease = parsed_prediction["disease"]

                # Determine health condition and message
                if disease == "Healthy":
                    health_status = "Healthy"
                    disease_name = None
                    message = "The plant is healthy."
                elif disease == "Unknown":
                    health_status = "Unhealthy"
                    disease_name = None
                    message = "The plant is not healthy, but the disease could not be identified."
                else:
                    health_status = "Unhealthy"
                    disease_name = disease
                    message = f"The plant is not healthy and is affected by {disease}."

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Save the detection to history
            DiseaseHistory.objects.create(
                user = request.user,
                plantID=1,
                diseaseID= 1 ,
                status = health_status,
            )

            send_detection_report_email(
                user=request.user,
                
                crop=crop,
                disease_name=disease_name,
                health_status=health_status,
                message=message,
                image_url=image_url
            )
            return Response({
                'condition_status': health_status,
                'disease_name': disease_name,
                'prediction_raw': prediction,
                'message': message,
                'image_url': image_url
            }) 
         
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ---- DiseaseHistory ----
class DiseaseHistoryListCreateAPIView(APIView):
    def get(self, request):
        records = DiseaseHistory.objects.all()
        serializer = DiseaseHistorySerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DiseaseHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiseaseHistoryDetailAPIView(APIView):
    def get(self, request, pk):
        record = get_object_or_404(DiseaseHistory, pk=pk)
        serializer = DiseaseHistorySerializer(record)
        return Response(serializer.data)

    def put(self, request, pk):
        record = get_object_or_404(DiseaseHistory, pk=pk)
        serializer = DiseaseHistorySerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        record = get_object_or_404(DiseaseHistory, pk=pk)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- FeedbackRating ----
class FeedbackRatingListCreateAPIView(APIView):
    def get(self, request):
        feedbacks = FeedbackRating.objects.all()
        serializer = FeedbackRatingSerializer(feedbacks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedbackRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackRatingDetailAPIView(APIView):
    def get(self, request, pk):
        feedback = get_object_or_404(FeedbackRating, pk=pk)
        serializer = FeedbackRatingSerializer(feedback)
        return Response(serializer.data)

    def put(self, request, pk):
        feedback = get_object_or_404(FeedbackRating, pk=pk)
        serializer = FeedbackRatingSerializer(feedback, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        feedback = get_object_or_404(FeedbackRating, pk=pk)
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- EditHistory ----
class EditHistoryListCreateAPIView(APIView):
    def get(self, request):
        edits = EditHistory.objects.all()
        serializer = EditHistorySerializer(edits, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EditHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditHistoryDetailAPIView(APIView):
    def get(self, request, pk):
        edit = get_object_or_404(EditHistory, pk=pk)
        serializer = EditHistorySerializer(edit)
        return Response(serializer.data)

    def delete(self, request, pk):
        edit = get_object_or_404(EditHistory, pk=pk)
        edit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- DeleteHistory ----
class DeleteHistoryListCreateAPIView(APIView):
    def get(self, request):
        deletes = DeleteHistory.objects.all()
        serializer = DeleteHistorySerializer(deletes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeleteHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteHistoryDetailAPIView(APIView):
    def get(self, request, pk):
        delete = get_object_or_404(DeleteHistory, pk=pk)
        serializer = DeleteHistorySerializer(delete)
        return Response(serializer.data)

    def delete(self, request, pk):
        delete = get_object_or_404(DeleteHistory, pk=pk)
        delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
