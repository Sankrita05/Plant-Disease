from django.urls import path
from .views import *

urlpatterns = [
    path('predict/', PredictImageView.as_view(), name='predict-image'),
    
    path('disease-history/', DiseaseHistoryListCreateAPIView.as_view(), name='disease-history-list'),
    path('disease-history/<int:pk>/', DiseaseHistoryDetailAPIView.as_view(), name='disease-history-detail'),

    path('feedback/', FeedbackRatingListCreateAPIView.as_view(), name='feedback-list'),
    path('feedback/<int:pk>/', FeedbackRatingDetailAPIView.as_view(), name='feedback-detail'),

    path('edit-history/', EditHistoryListCreateAPIView.as_view(), name='edit-history-list'),
    path('edit-history/<int:pk>/', EditHistoryDetailAPIView.as_view(), name='edit-history-detail'),

    path('delete-history/', DeleteHistoryListCreateAPIView.as_view(), name='delete-history-list'),
    path('delete-history/<int:pk>/', DeleteHistoryDetailAPIView.as_view(), name='delete-history-detail'),
]
