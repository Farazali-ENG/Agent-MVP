# your_app/utils.py

import os
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import Customer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
import uuid
import hashlib


# jwt authentication here
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Authorization header missing.")

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid token header format.")

        token = auth_header.split(" ")[1]

        try:
            # Decode the token
            payload = AccessToken(token).payload
            user_id = payload.get("user_id")
            
            if not user_id:
                raise AuthenticationFailed("Invalid token payload.")

            # Check if user exists in database
            user = Customer.objects.get(id=user_id)
        except (Customer.DoesNotExist, Exception) as e:
            raise AuthenticationFailed("Invalid token or user does not exist.")
        
        return user, token


# generate jwt token here
def generate_jwt_tokens(user):
    try:
        # Create a refresh token
        refresh = RefreshToken.for_user(user)

        # Add the user_id into the token payload
        refresh["user_id"] = user.id
        print("Generated token payload with user_id:", refresh)

        # Return tokens
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    except Exception as e:
        print("Failed to generate JWT token:", e)
        return {
            "access": None,
            "refresh": None,
        }



# function to validate the extension of file
def validate_file_extension(file):
    """
    Validates that a file has a .docx or .pdf extension.
    
    Args:
        file: The uploaded file to validate.
    
    Returns:
        bool: True if the file has a valid extension, False otherwise.
    """
    allowed_extensions = ['.docx', '.pdf']
    # Extract the file extension
    extension = os.path.splitext(file.name)[1].lower()  # Get file extension in lowercase
    
    return extension in allowed_extensions


def generate_uuid_from_ip(public_ip):
    # Create a hash of the IP
    hash_object = hashlib.md5(public_ip.encode())
    # Use the hash to create a UUID
    return uuid.UUID(hash_object.hexdigest())
