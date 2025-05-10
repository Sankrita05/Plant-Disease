# models.py
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class DiseaseHistory(models.Model):
    permission_classes = [IsAuthenticated]
    historyID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plantID = models.IntegerField()
    diseaseID = models.IntegerField()
    date_detected = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"History {self.historyID} for User {self.user.userID}"


class FeedbackRating(models.Model):
    feedbackID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedbackText = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Feedback {self.feedbackID} by User {self.user.userID}"


class EditHistory(models.Model):
    editID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    history = models.ForeignKey(DiseaseHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f"Edit {self.editID} by User {self.user.userID}"


class DeleteHistory(models.Model):
    deleteID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    history = models.ForeignKey(DiseaseHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f"Delete {self.deleteID} by User {self.user.userID}"