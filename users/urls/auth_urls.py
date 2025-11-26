from django.urls import path
from users.views.auth_views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView, 
    LoginView, 
    GoogleAuthView, 
    OTPValidationView,
    RequestOTPView
)

urlpatterns = [
    # Rutas tradicionales
    path('user/register/', RegisterView.as_view(), name='register'),
    path('user/login/', LoginView.as_view(), name='login'),
    
    # Rutas para el flujo de seguridad
    path('user/otp/validate/', OTPValidationView.as_view(), name='otp_validate'),
    path('user/otp/request/', RequestOTPView.as_view(), name='otp_request'),

    # Ruta de autenticación social
    path('user/google/', GoogleAuthView.as_view(), name='google_auth'),
    
    # Rutas para restablecimiento de contraseña
    path('user/password/request-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    # Puedes reutilizar 'otp/validate/' o crear una nueva para mayor claridad.
    path('user/password/confirm-reset/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]