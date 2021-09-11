
import requests
import json




def request_gql(url: str, query: str, variables: dict) -> dict:
    r = requests.post(url=url + 'graphql', json={"query": query, "variables": variables})
    if r.status_code != 200 or "errors" in r.json():
        # print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(query))
        print("ERROR:")
        print("Problem occured while sending to PMT X:")
        print("URL:", url)
        print("QUERY:", query)
        print("VARIABLES:")
        print(json.dumps(variables, indent=4))
        print("RESPONSE:")
        print(json.dumps(r.json(), indent=4))
        raise Exception("Problem occured while sinding to PMT X")
    return r.json()


def request_dql_query(url: str, query: str, variables: dict) -> dict:
    r = requests.post(url=url + 'query', json={"query": query, "variables": variables})
    if r.status_code != 200 or "errors" in r.json():
        # print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(query))
        print("ERROR:")
        print("Problem occured while sending to PMT X:")
        print("URL:", url)
        print("QUERY:", query)
        print("VARIABLES:")
        print(json.dumps(variables, indent=4))
        print("RESPONSE:")
        print(json.dumps(r.json(), indent=4))
        raise Exception("Problem occured while sinding to PMT X")
    return r.json()


def request_dql_mutate(url: str, mutation: dict):
    r = requests.post(url=url + 'mutate?commitNow=true', json=mutation)
    if r.status_code != 200 or "errors" in r.json():
        # print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(query))
        print("ERROR:")
        print("Problem occured while sending to PMT X:")
        print("URL:", url)
        print("MUTATION:")
        print(json.dumps(mutation, indent=4))
        print("RESPONSE:")
        print(json.dumps(r.json(), indent=4))
        raise Exception("Problem occured while sinding to PMT X")
    return r.json()

