from lib.pmtx_client.pmtx_base import request_dql_query, request_gql






def get_default_baseline(url: str, filter = "regexp(Project.name, //i)") -> dict:
    query = """
query {
  var(func: type(Project)) @filter({filter}) {
    PROJECTS_IDS as uid
  }
  
  projects (func: uid(PROJECTS_IDS)) @normalize {
    id: uid
    name: Project.name
    description: Project.description
    Project.baseline {
      actualStart: ProjectBaseline.start
      actualEnd: ProjectBaseline.finish
      wbs: ProjectBaseline.wbs
      actualWorktime: ProjectBaseline.worktime
      ProjectBaseline.parent { ProjectBaseline.project { parent: uid } }
    }
  }
    
#   predecessors (func: uid(PROJECTS_IDS)) @normalize @cascade {
#     project_id: uid
#     Project.baseline { 
#       ProjectBaseline.predecessors {
#         Predecessor.project { ProjectBaseline.project { predecessor_id: uid } }
#         type: Predecessor.type
#     	} 
#     }
#   }
}
    """.replace("{filter}", filter)
    return request_dql_query(url, query, {})



# def form_anychart_json(baseline: dict, baseline_compare: dict) -> dict:
#     anychart_data = []

#     for project in baseline:
#         project_formated = {
#             "id": project['project']['id'],
#             "name": project['project'],
#             "description":
#         }

#     return anychart_data








if __name__ == "__main__":

    url = "http://192.168.5.20:8080/"



    baseline = get_default_baseline(url)
    print(baseline['data'])

