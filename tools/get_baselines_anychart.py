from lib.pmtx_client.pmtx_base import request_dql_query





def get_projects_and_baselines_anychart(url: str, baseline_filter: str, baseline_compare_filter: str, project_filter = "regexp(Project.name, //i)") -> dict:

    baseline = "" if not baseline_filter else """
    baseline: Project.projectBaselines @filter({filter}) {
      actualStart: ProjectBaseline.start
      actualEnd: ProjectBaseline.finish
      wbs: ProjectBaseline.wbs
      actualWorktime: ProjectBaseline.worktime
      ProjectBaseline.parent { ProjectBaseline.project { parent: uid } }
    }
    """.replace("{filter}", baseline_filter)
    
    baseline_compare = "" if not baseline_compare_filter else """
    baseline_compare: Project.projectBaselines @filter({filter}) {
      baselineStart: ProjectBaseline.start
      baselineEnd: ProjectBaseline.finish
      baselineWorktime: ProjectBaseline.worktime
    }
    """.replace("{filter}", baseline_compare_filter)

    query = """
query {
  var(func: type(Project)) @filter({filter}) {
    PROJECTS_IDS as uid
  }
  
  projects (func: uid(PROJECTS_IDS), orderdesc: ProjectBaseline.start) @normalize {
    id: uid
    name: Project.name
    description: Project.description
    {baseline}
    {baseline_compare}
  }
}
    """.replace("{filter}", project_filter).replace("{baseline}", baseline).replace("{baseline_compare}", baseline_compare)

    return request_dql_query(url, query, {})['data']['projects']






def form_anychart_json(url: str, filter: str, baseline_id: str, baseline_compare_id: str) -> dict:
    filter = "regexp(Project.name, /{0}/i)".format(filter)

    if baseline_id:
        baseline_filter = "uid_in(ProjectBaseline.baseline, {0})".format(baseline_id)
    else:
        baseline_filter = "NOT has(ProjectBaseline.baseline)"

    if baseline_compare_id:
        baseline_compare_filter = "uid_in(ProjectBaseline.baseline, {0})".format(baseline_compare_id)
    elif baseline_id:
        baseline_compare_filter = "NOT has(ProjectBaseline.baseline)"
    else:
        baseline_compare_filter = ""

    return get_projects_and_baselines_anychart(url, baseline_filter, baseline_compare_filter, filter)








if __name__ == "__main__":
    url = "http://192.168.5.20:8080/"

    projects = form_anychart_json(url, "", "", "")
    print(projects)

