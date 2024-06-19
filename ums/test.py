import requests

# URL of the protected view
url = "http://yourdomain.com/your-protected-view/"

# Access token obtained from the authentication process
access_token = "youraccesstoken"

# Setting up the headers with the Authorization token
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Making the GET request to the protected view
response = requests.get(url, headers=headers)

# Handling the response
if response.status_code == 200:
    # If the request is successful, parse the JSON data
    data = response.json()
    print("Data received from the protected view:", data)
else:
    # If the request fails, print the status code and error message
    print(f"Request failed with status code {response.status_code}")
    print("Error:", response.text)
