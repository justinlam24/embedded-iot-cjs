import requests, time
db = "https://candjs-bb4db-default-rtdb.europe-west1.firebasedatabase.app/"
path = "userdetails.json" 

# query = "?orderBy=\"$key\"&startAt=\"{}\"&endAt=\"{}\"".format(1738331900, int(time.time()))
# query = "?orderBy=\"rnd\"&startAt=0.5&endAt=1.0"
query = "?orderBy=\"$key\"&limitToLast=1000"

input_username = "steve"
input_password = "admin"

def check_credentials(username, password):
    """ Check if username & password exist in Firebase postlist. """
    response = requests.get(db + path + query)

    if response.ok:
        users = response.json()

        for key, user in users.items():
            if user.get("username") == username and user.get("password") == password:
                return True  # Credentials match

        return False  # No match found

    else:
        raise ConnectionError("Could not access database: {}".format(response.text))

# Run authentication check
is_authenticated = check_credentials(input_username, input_password)
print(f"Authentication Successful: {is_authenticated}")