from rest_framework import generics, permissions, status, serializers, parsers
from rest_framework.response import Response
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import random
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle
from .models import CustomUser, UserProfile
from .serializers import UserSerializer, LoginSerializer, ProfileSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'register'
    throttle_classes = [ScopedRateThrottle]

    
    def perform_create(self, serializer):
        code = f"{random.randint(1000, 9999)}"
        user = serializer.save(is_active=False, verification_code=code)
        UserProfile.objects.create(user=user)
        from .tasks import send_verification_code_email
        send_verification_code_email(user.email, code)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'login'
    throttle_classes = [ScopedRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        logout(request)
        return Response(status=status.HTTP_200_OK)

class ActivateAccountView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'status': 'account activated'})
        return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.GET.get('email')
        code = request.GET.get('code')
        return self._verify(email, code)

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        return self._verify(email, code)

    def _verify(self, email, code):
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        if user.verification_code != code:
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.verification_code = ''
        user.save()
        return Response({'status': 'account activated'})



class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_200_OK)
        code = f"{random.randint(1000, 9999)}"
        user.reset_code = code
        user.save(update_fields=["reset_code"])
        from .tasks import send_password_reset_code_email
        send_password_reset_code_email(user.email, code)
        return Response(status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        if not all([email, code, password]):
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        try:
                        user = CustomUser.objects.get(email=email, reset_code=code)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer()
        try:
            password = serializer.validate_password(password)
        except serializers.ValidationError as exc:
            return Response({'error': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.reset_code = ''
        user.save()
        return Response({'status': 'password reset'})
    
class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]
    

    def get_object(self):
        return self.request.user.userprofile

    def delete(self, request, *args, **kwargs):
        password = request.data.get('password')
        if not password or not request.user.check_password(password):
            return Response({'error': 'Неверный пароль'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        logout(request)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)