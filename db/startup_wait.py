import requests
import sys
import time



url = sys.argv[1]

query = '''
query {
  health {
	instance
	address
	version
	status
	lastEcho
	group
	uptime
	ongoing
	indexing
  }
}
'''

while (True):
	time.sleep(1)	 

	try:
		response = requests.post(url, json={"query": query})
	except Exception as e:
		response = None

	if response is None:
		print("Trying to connect to server under endpoint: " + url)
		continue

	if response.status_code == 200:
		isWorking = True
		for instance in response.json()["data"]["health"]:
			if instance["status"] != "healthy":
				isWorking = False
		if isWorking:
			print('Dgraph works fine on endpoint: ' + url)
			print(response.json())
			break

	print(response) 