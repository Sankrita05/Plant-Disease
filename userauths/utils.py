import random
from django.core.mail import send_mail
from .models import OTP
from .models import TemporaryUserData
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.conf import settings
from twilio.rest import Client

# To Clean up duplicate temporary entries
def cleanup_temp_user(email, phone_no):
    expiry_time = timezone.now() - timedelta(minutes=10)
    TemporaryUserData.objects.filter(
        Q(email=email) | Q(phone_no=phone_no),
        created_at__lt=expiry_time
    ).delete()
    
    # To delete current conflicting entries (e.g., failed attempts)
    TemporaryUserData.objects.filter(Q(email=email) | Q(phone_no=phone_no)).delete()

# Temporarily save the user data for email verification
def create_temp_user(validated_data):
    return TemporaryUserData.objects.create(
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        email=validated_data['email'],
        phone_no=validated_data['phone_no'],
        password=validated_data['password'],
        region=validated_data['region']
    )

# To generate otp
def generate_otp():
    return str(random.randint(100000, 999999))

# To send otp on email
def send_email_otp(email, purpose='register'):
    otp_code = generate_otp()
    # Optionally delete old OTPs for the same email and purpose
    if OTP.objects.filter(email=email, purpose=purpose).exists():
        OTP.objects.filter(email=email, purpose=purpose).delete()

    OTP.objects.create(email=email, otp_code=otp_code, purpose=purpose)
    try:
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {otp_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,  # Use settings for flexibility
            recipient_list=[email],
            fail_silently=False
        )
        return otp_code # Return success if email sent
    except Exception as e:
        print(f"Error sending email: {e}")
        return False  # Return failure if there was an error
    

# To send otp on mobile
def send_mobile_otp(phone_no, purpose='register'):
    otp_code = generate_otp()
    if OTP.objects.filter(phone_no=phone_no, purpose=purpose).exists():
        OTP.objects.filter(phone_no=phone_no, purpose=purpose).delete()
    
    OTP.objects.create(phone_no=phone_no, otp_code=otp_code, purpose=purpose)

    # try:
    #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #     message = client.messages.create(
    #         body=f"Your OTP is {otp_code}",
    #         from_=settings.TWILIO_PHONE_NUMBER,
    #         to=phone_no
    #     )
    #     print(f"OTP sent to {phone_no}")
    #     return True  # Return success if OTP sent
    # except Exception as e:
    #     print(f"Error sending OTP via SMS: {e}")
    #     return False  # Return failure if there was an error

    print(f"Sending SMS to {phone_no}: Your OTP is {otp_code}")
    return otp_code


def verify_otp(identifier, otp_code, is_email=True):
    try:
        if is_email:
            otp = OTP.objects.filter(email=identifier, otp_code=otp_code).latest('created_at')
        else:
            otp = OTP.objects.filter(phone_no=identifier, otp_code=otp_code).latest('created_at')
    
    except OTP.DoesNotExist:
        return None, "Invalid or expired OTP"

    if otp.is_verified:
        return None, "OTP already verified"

    if otp.is_expired():
        return None, "OTP has expired"

    otp.is_verified = True
    otp.save()
    return otp, None
