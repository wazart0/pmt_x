import requests
from lib.pmtx_client.pmtx_base import request_dql_query
import re




def get_root_and_children_ids(url: str, project_baseline_root_id: str) -> list:
    project_baseline_ids = []

    query = """
query getRootAndChildren($project_baseline_root_id: string) {
  q (func: uid($project_baseline_root_id)) @recurse(loop: false) {
    uid
    ProjectBaseline.children
  }
}
    """

    variables = {
        "$project_baseline_root_id": project_baseline_root_id
    }

    response = request_dql_query(url, query, variables)

    pattern = re.compile(r"'uid': '.+?'")
    found_ids = pattern.findall(str(response))

    pattern = re.compile(r"'uid': '(?P<id>.+)'")
    for id in found_ids:
        match = pattern.match(id)
        project_baseline_ids.append(match.group('id'))

    # print(str(response))


    return project_baseline_ids




if __name__ == "__main__":

    url = "http://192.168.5.20:8080/"

    project_baseline_root_id = "0x2715"

    ids = get_root_and_children_ids(url, project_baseline_root_id)

    print(ids)
