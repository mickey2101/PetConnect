from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer
import logging

logger = logging.getLogger(__name__)

# Define get_csrf_token function
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    View to get a CSRF token.
    This can be called by the React app on initialization to ensure a CSRF cookie is set.
    """
    token = get_token(request)
    logger.debug(f"CSRF token generated for user: {request.user}")
    return JsonResponse({'success': True, 'csrf_token': token})


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that doesn't enforce CSRF on direct API calls.
    USE WITH CAUTION!
    """
    def enforce_csrf(self, request):
        # Don't enforce CSRF tokens for this view
        return


class CurrentUserView(APIView):
    """
    View to get the current authenticated user
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Not authenticated"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LoginView(APIView):
    """
    View to handle user login
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        logger.info(f"Login attempt for user: {username}")
        
        if not username or not password:
            return Response(
                {"error": "Username and password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            
            # Set the CSRF token in the response
            response = Response(UserSerializer(user).data)
            response['X-CSRFToken'] = get_token(request)
            return response
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    View to handle user logout
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            logger.info(f"User {username} logged out")
        
        return Response({"success": True})


class RegisterView(APIView):
    """
    View to handle user registration
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.username}")
            
            # Automatically log in the user after registration
            login(request, user)
            
            # Set the CSRF token in the response
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response['X-CSRFToken'] = get_token(request)
            return response
        
        logger.warning(f"User registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPreferenceView(APIView):
    """
    View to handle user preferences
    """
    authentication_classes = [CsrfExemptSessionAuthentication]  # Use CSRF exempt here
    permission_classes = [IsAuthenticated]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        try:
            logger.info(f"Fetching preferences for user: {request.user.username}")
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching preferences: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        try:
            logger.info(f"Updating preferences for user: {request.user.username}")
            logger.debug(f"Preference data: {request.data}")
            
            # Get or create the user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Filter out any fields that don't exist in the model
            valid_fields = [field.name for field in UserProfile._meta.get_fields()]
            filtered_data = {k: v for k, v in request.data.items() if k in valid_fields}
            
            logger.debug(f"Filtered preference data: {filtered_data}")
            
            # Update with filtered data
            serializer = UserProfileSerializer(profile, data=filtered_data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Preferences updated successfully for user: {request.user.username}")
                return Response(serializer.data)
            else:
                logger.warning(f"Invalid preference data: {serializer.errors}")
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UpdateProfileView(APIView):
    """
    View to handle updating user profile information
    """
    authentication_classes = [CsrfExemptSessionAuthentication]  # Use CSRF exempt here
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Log request information
            logger.debug(f"UpdateProfileView called by user: {request.user.username}")
            logger.debug(f"Request data: {request.data}")
            
            # Get the current user
            user = request.user
            
            # Get the data to update
            username = request.data.get('username')
            email = request.data.get('email')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            
            # Check if username is being changed and if it's already taken
            if username and username != user.username:
                if User.objects.filter(username=username).exists():
                    logger.warning(f"Username {username} already taken")
                    return Response(
                        {"error": "Username is already taken"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                user.username = username
            
            # Check if email is being changed and if it's already taken
            if email and email != user.email:
                if User.objects.filter(email=email).exists():
                    logger.warning(f"Email {email} already taken")
                    return Response(
                        {"error": "Email is already taken"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                user.email = email
            
            # Update other fields
            if first_name is not None:
                user.first_name = first_name
            
            if last_name is not None:
                user.last_name = last_name
            
            # Save the user
            user.save()
            logger.info(f"Profile updated successfully for user: {user.username}")
            
            # Return updated user data
            serializer = UserSerializer(user)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )