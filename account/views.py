from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .permissions import IsActive
from .serializers import RegistrationSerializer,\
    CreateNewPasswordSerializer
from .utils import send_activation_code
class RegistrationView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('OK', 201)


class ActivationView(APIView):

    def get(self, request, code, email):
        user = User.objects.get(email=email, activation_code=code)
        msg = (
            'Пользователь не найден',
            'Аккаунт активирован'
        )
        if not user:
            return Response(msg[0], 400)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response(msg[-1], 200)





"""class APILogoutView(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get('all'):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})"""

class LogOutView(APIView):
    # permission_classes = [IsActive]
    def post(self, request):
        refresh_token = request.data['refresh_token']
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})

class ForgotPasswordView(APIView):
    def get(self, request, email):
        user = get_object_or_404(User, email=email)
        user.is_active = False
        user.create_activation_code()
        user.save()
        send_activation_code(
            email=user.email, code=user.activation_code, status='forgot_password'
        )
        return Response('Вам отправили письчо на почту', status=200)

class CompleteRestPasswordView(APIView):

    permission_classes = AllowAny

    def post(self, request):
        serializer = CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Вы успешно поменяли пароль', status=200)

