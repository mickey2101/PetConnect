# authentication.py

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows login with either username or email
    and provides more detailed logging for authentication issues.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Try to find the user by username or email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            
            # Check the password
            if user.check_password(password):
                return user
            
            # Log password failure
            print(f"Authentication failed: Wrong password for user {username}")
            return None
            
        except User.DoesNotExist:
            # Log user not found
            print(f"Authentication failed: No user found with username or email {username}")
            return None
        except Exception as e:
            # Log other errors
            print(f"Authentication error: {str(e)}")
            return None
    
    def get_user(self, user_id):
        """
        Override get_user to add better logging
        """
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            print(f"Error fetching user with ID {user_id}: User does not exist")
            return None
        except Exception as e:
            print(f"Error fetching user with ID {user_id}: {str(e)}")
            return None