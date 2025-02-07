import time,random
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

class Communication:

    def __init__(self)
        self.db = "https://candjs-bb4db-default-rtdb.europe-west1.firebasedatabase.app/"

        # Define the private key file (change to use your private key)
        self.keyfile = "candjs-bb4db-firebase-adminsdk-fbsvc-110a8751b6.json"

        # Define the required scopes
        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/firebase.database"
        ]

        # Authenticate a credential with the service account (change to use your private key)
        self.credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)

        # Use the credentials object to authenticate a Requests session.
        self.authed_session = AuthorizedSession(credentials)

        self.N = 20
        self.n = 

        self.skateboard_tricks = {
            1:"Kickflip",
            2: "Heelflip",
            3: "Shuv It",
            4: "Front Shuv",
            5: "360 Shuv It",
            6: "360 Shuv",
            7: "Ollie"
        }


    def write_and_limit_data(self, data):
        path = "postlist.json"

        print("Writing {} to {}".format(data, path))
        response = self.authed_session.post(self.db+path, json=data)

        if response.ok:
            print("Created new node named {}".format(response.json()["name"]))
        else:
            raise ConnectionError("Could not write to database: {}".format(response.text))

        fetch_response = self.authed_session.get(self.db+path)

        if fetch_response.ok:
            records = fetch_response.json()

            # If there are more than N records, delete the oldest
            if len(records) > N:
                oldest_key = min(records, key=lambda k: records[k]["time"])  # Find the oldest record
                del_path = f"postlist/{oldest_key}.json"
                del_response = self.authed_session.delete(self.db + del_path)

                if del_response.ok:
                    print(f"Deleted oldest record: {oldest_key}")
                else:
                    print(f"Failed to delete oldest record: {del_response.text}")

        else:
            print(f"Failed to fetch records: {fetch_response.text}")

#skateboard_tricks = {
    #1:"Kickflip",
    #2: "Heelflip",
    #3: "Shuv It",
    #4: "Front Shuv",
    #5: "360 Shuv It",
    #6: "360 Shuv",
    #7: "Ollie"
#}
#
#for n in range(7, 0, -1):
    #data = {"trick name": skateboard_tricks[n], "max height": random.random(), "max velocity": random.random(), "time": time.time()}
    #write_and_limit_data(data)
    #time.sleep(1)
