import time,random, requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

db = "https://candjs-bb4db-default-rtdb.europe-west1.firebasedatabase.app/"

# Define the private key file (change to use your private key)
keyfile = "candjs-bb4db-firebase-adminsdk-fbsvc-a669d958fb.json"

# Define the required scopes
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

# Authenticate a credential with the service account (change to use your private key)
credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)

# Use the credentials object to authenticate a Requests session.
authed_session = AuthorizedSession(credentials)
query = "?orderBy=\"$key\"&limitToLast=1000"

N = 1000
n = 1
def register_user(data):
    path = "userdetails.json"
    response = requests.get(db + path + query)

    if response.ok:
        users = response.json()

        for key, user in users.items():
            if user.get("username") == data["username"]:
                print("❌ Username already exists! Choose a different one.")
                return False  # Username is already taken

        print("Adding {} to {}".format(data, path))
        response = authed_session.post(db+path, json=data)

        if response.ok:
            print("Created new node named {}".format(response.json()["name"]))
        else:
            raise ConnectionError("Could not write to database: {}".format(response.text))

    fetch_response = authed_session.get(db+path)

    if fetch_response.ok:
        records = fetch_response.json()

        # If there are more than N records, delete the oldest
        if len(records) > N:
            oldest_key = min(records, key=lambda k: records[k]["time"])  # Find the oldest record
            del_path = f"postlist/{oldest_key}.json"
            del_response = authed_session.delete(db + del_path)

            if del_response.ok:
                print(f"Deleted oldest record: {oldest_key}")
            else:
                print(f"Failed to delete oldest record: {del_response.text}")

    else:
        print(f"Failed to fetch records: {fetch_response.text}")

username = "hi"
password = "test"
data = {"username": username, "password": password}
register_user(data)
time.sleep(1)