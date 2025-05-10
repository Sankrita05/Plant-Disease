from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.timezone import now


def send_detection_report_email(user, crop, disease_name, health_status, message, image_url):
    context = {
        'user': user,
        'datetime': now(),
        'crop': crop,
        'disease': disease_name if disease_name else "Not Identified",
        'health_status': health_status,
        'message': message,
        'image_url': image_url,
    }

    subject = "Plant Disease Detection Report"
    html_message = render_to_string(r"email/Analysis_Report.html", context)
    plain_message = strip_tags(html_message)
    recipient_list = [user.email]

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message
    )
