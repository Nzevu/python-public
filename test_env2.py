import os
# Access the secret from environment variables
my_secret = os.environ.get('API_KEY_TEST1')
if my_secret:
   print("Secret retrieved successfully!")
else:
   print("Failed to retrieve the secret.")
