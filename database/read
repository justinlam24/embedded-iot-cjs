import requests, time
db = "https://candjs-bb4db-default-rtdb.europe-west1.firebasedatabase.app/"

path = "timeseries.json" # the key where we are storing the data in the firebase 

# query depends on how we want to categorize or sort it
# query = "?orderBy=\"$key\"&startAt=\"{}\"&endAt=\"{}\"".format(1738331900, int(time.time()))
# query = "?orderBy=\"rnd\"&startAt=0.5&endAt=1.0"
query = "?orderBy=\"$key\"&limitToLast=100"

response = requests.get(db+path+query)
if response.ok:
    print(response.json())
else:
    raise ConnectionError("Could not access database: {}".format(response.text))
