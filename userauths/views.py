from django.contrib.auth import authenticate
from django.utils.timezone import now

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *
from .models import *
from .utils import *

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone_no = serializer.validated_data['phone_no']
            email = serializer.validated_data['email']
            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "Email is already registered"}, status=400)
            if CustomUser.objects.filter(phone_no=phone_no).exists():
                return Response({"error": "This number is already registered"}, status=400)

            cleanup_temp_user(email, phone_no)
            temp_user = create_temp_user(serializer.validated_data)
            send_email_otp(temp_user.email, purpose='register')
            return Response({"message": "Email OTP sent"}, status=200)
        return Response(serializer.errors, status=400)


class SendEmailOTPView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = SendEmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # purpose = serializer.validated_data['purpose']
            send_email_otp(email)
            return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMobileOTPView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = SendMobileOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_no = serializer.validated_data['phone_no']
            send_mobile_otp(phone_no=phone_no)
            return Response({"message": "OTP sent to mobile."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailOTPView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")
        otp, error = verify_otp(email, otp_code, is_email=True)
        if error:
            return Response({"error": error}, status=400)
        
        try:
            temp_user = TemporaryUserData.objects.get(email=email)
        except TemporaryUserData.DoesNotExist:
            return Response({"error": "Temporary user not found."}, status=400)

        temp_user.is_email_verified = True
        temp_user.save()

        # Trigger mobile OTP
        send_mobile_otp(temp_user.phone_no)
        return Response({"message": "Email verified successfully. Mobile OTP sent."})

class VerifyMobileOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    def post(self, request):
        phone_no = request.data.get('phone_no')
        otp_code = request.data.get('otp_code')

        otp, error = verify_otp(phone_no, otp_code, is_email=False)
        if error:
            return Response({"error": error}, status=400)

        try:
            temp_user = TemporaryUserData.objects.get(phone_no=phone_no)
        except TemporaryUserData.DoesNotExist:
            return Response({"error": "No user data found for this mobile number."}, status=status.HTTP_400_BAD_REQUEST)

        # Create full user
        user = CustomUser(
            first_name=temp_user.first_name,
            last_name=temp_user.last_name,
            email=temp_user.email,
            phone_no=temp_user.phone_no,
            region=temp_user.region,
            is_email_verified=True,
            is_mobile_verified=True
        )

        user.set_password(temp_user.password)
        user.save()
        temp_user.delete()
        # Generate JWT tokens
        token = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(token),
            "access": str(token.access_token)
        }

        # Serialize user
        serializer = RegisterSerializer(user)
        data = serializer.data
        data["tokens"] = tokens

        return Response( {"message": "User successfully registered."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user:
                user.last_login = now()
                user.save(update_fields=['last_login'])
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({"error": "Invalid credentials"}, status=400)
        return Response(serializer.errors, status=400)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=205)
        except Exception:
            return Response(status=400)

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                # Check if the user exists
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Send the reset OTP to the user's email
            send_email_otp(email, purpose='reset')

            return Response({"message": "Password reset OTP sent to email."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            try:
                otp = OTP.objects.get(email=email, otp_code=otp_code)
                if otp.is_expired():
                    return Response({"error": "OTP expired"}, status=400)
                user = CustomUser.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password reset successful."})
            except:
                return Response({"error": "Invalid data"}, status=400)
        return Response(serializer.errors, status=400)
