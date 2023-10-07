from lib.pmtx_client.pmtx_base import request_dql_query
import json
import pandas as pd




def get_projects_and_baselines_anychart(url: str, baseline_filter: str, baseline_compare_filter: str, project_filter = "regexp(Project.name, //i)") -> dict:

    baseline = "" if not baseline_filter else """
    baseline: Project.projectBaselines @filter({filter}) {
      pbID: uid
      actualStart: ProjectBaseline.start
      actualEnd: ProjectBaseline.finish
      wbs: ProjectBaseline.wbs
      actualWorktime: ProjectBaseline.worktime
      ProjectBaseline.parent { ProjectBaseline.project { parent: uid } }
    }
    """.replace("{filter}", baseline_filter)
    
    baseline_compare = "" if not baseline_compare_filter else """
    baseline_compare: Project.projectBaselines @filter({filter}) {
      pbcmpID: uid
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
    jira: Project.externalTool @filter(eq(ExternalTool.type, "Jira")) {
      extID: ExternalTool.externalID
      extURL: ExternalTool.url
	  extSubpath: ExternalTool.urlSubpath
      extFields: ExternalTool.customFields
    }
    {baseline}
    {baseline_compare}
  }
}
    """.replace("{filter}", project_filter).replace("{baseline}", baseline).replace("{baseline_compare}", baseline_compare)

    # print(query)

    return request_dql_query(url, query, {})['data']






def form_anychart_projects(url: str, filter: str, baseline_id: str, baseline_compare_id: str) -> dict:
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




def form_anychart_and_summary(url: str, filter: str, baseline_id: str, baseline_compare_id: str) -> dict:
    pmt_x_fe = form_anychart_projects(url, filter, baseline_id, baseline_compare_id)

    if len(pmt_x_fe['projects']) == 0: return pmt_x_fe

    df = pd.DataFrame(pmt_x_fe['projects'])
    if 'parent' in df.columns: df = df[~df.id.isin(df.parent)] # lowest level projects

    df['actualWorktime'] = pd.to_timedelta(df['actualWorktime'])

    if 'actualStart' not in df.columns: df['actualStart'] = None
    if 'actualEnd' not in df.columns: df['actualEnd'] = None
    if 'actualWorktime' not in df.columns: df['actualWorktime'] = None

    if 'baselineStart' not in df.columns: df['baselineStart'] = None
    if 'baselineEnd' not in df.columns: df['baselineEnd'] = None
    if 'baselineWorktime' not in df.columns: df['baselineWorktime'] = None

    # print(df)

    df_baseline = df[df.pbID.notnull()]
    pmt_x_fe['summary_baseline_total'] = 0
    pmt_x_fe['summary_baseline_total_hours'] = '{0:.2f}'.format(df_baseline.actualWorktime.sum().total_seconds()/3600.)
    pmt_x_fe['summary_baseline_awaits'] = 0
    pmt_x_fe['summary_baseline_awaits_hours'] = '{0:.2f}'.format(df_baseline[df_baseline.actualStart.isnull() & df_baseline.actualEnd.isnull()].actualWorktime.sum().total_seconds()/3600.)
    pmt_x_fe['summary_baseline_awaits_hours_percent'] = '{0:.1f}'.format(df_baseline[df_baseline.actualStart.isnull() & df_baseline.actualEnd.isnull()].actualWorktime.sum().total_seconds()/df_baseline.actualWorktime.sum().total_seconds()*100.)
    pmt_x_fe['summary_baseline_started'] = 0
    pmt_x_fe['summary_baseline_started_hours'] = '{0:.2f}'.format(df_baseline[df_baseline.actualStart.notnull() & df_baseline.actualEnd.isnull()].actualWorktime.sum().total_seconds()/3600.)
    pmt_x_fe['summary_baseline_started_hours_percent'] = '{0:.1f}'.format(df_baseline[df_baseline.actualStart.notnull() & df_baseline.actualEnd.isnull()].actualWorktime.sum().total_seconds()/df_baseline.actualWorktime.sum().total_seconds()*100.)
    pmt_x_fe['summary_baseline_finished'] = 0
    pmt_x_fe['summary_baseline_finished_hours'] = '{0:.2f}'.format(df_baseline[df_baseline.actualEnd.notnull()].actualWorktime.sum().total_seconds()/3600.)
    pmt_x_fe['summary_baseline_finished_hours_percent'] = '{0:.1f}'.format(df_baseline[df_baseline.actualEnd.notnull()].actualWorktime.sum().total_seconds()/df_baseline.actualWorktime.sum().total_seconds()*100.)
    
    if 'pbcmpID' in df.columns:
        df_baseline_cmp = df[df.pbcmpID.notnull()]
        df_baseline_cmp['baselineWorktime'] = pd.to_timedelta(df_baseline_cmp['baselineWorktime'])

    pmt_x_fe['summary_baseline_cmp_total'] = 0
    pmt_x_fe['summary_baseline_cmp_total_hours'] = '{0:.2f}'.format(df_baseline_cmp.baselineWorktime.sum().total_seconds()/3600.) if 'pbcmpID' in df.columns else 0
    pmt_x_fe['summary_baseline_cmp_awaits'] = 0
    pmt_x_fe['summary_baseline_cmp_awaits_hours'] = '{0:.2f}'.format(df_baseline_cmp[df_baseline_cmp.baselineStart.isnull() & df_baseline_cmp.baselineEnd.isnull()].baselineWorktime.sum().total_seconds()/3600.) if 'pbcmpID' in df.columns else 0
    pmt_x_fe['summary_baseline_cmp_awaits_hours_percent'] = '{0:.1f}'.format(df_baseline_cmp[df_baseline_cmp.baselineStart.isnull() & df_baseline_cmp.baselineEnd.isnull()].baselineWorktime.sum().total_seconds()/df_baseline_cmp.baselineWorktime.sum().total_seconds()*100.) if 'pbcmpID' in df.columns else 0
    pmt_x_fe['summary_baseline_cmp_started'] = 0
    pmt_x_fe['summary_baseline_cmp_started_hours'] = '{0:.2f}'.format(df_baseline_cmp[df_baseline_cmp.baselineStart.notnull() & df_baseline_cmp.baselineEnd.isnull()].baselineWorktime.sum().total_seconds()/3600.) if 'pbcmpID' in df.columns else 0
    pmt_x_fe['summary_baseline_cmp_started_hours_percent'] = '{0:.1f}'.format(df_baseline_cmp[df_baseline_cmp.baselineStart.notnull() & df_baseline_cmp.baselineEnd.isnull()].baselineWorktime.sum().total_seconds()/df_baseline_cmp.baselineWorktime.sum().total_seconds()*100.) if 'pbcmpID' in df.columns else 0
    pmt_x_fe['summary_baseline_cmp_finished'] = 0
    pmt_x_fe['summary_baseline_cmp_finished_hours'] = '{0:.2f}'.format(df_baseline_cmp[df_baseline_cmp.baselineEnd.notnull()].baselineWorktime.sum().total_seconds()/3600.) if 'pbcmpID' in df.columns else 0
    pmt_x_fe['summary_baseline_cmp_finished_hours_percent'] = '{0:.1f}'.format(df_baseline_cmp[df_baseline_cmp.baselineEnd.notnull()].baselineWorktime.sum().total_seconds()/df_baseline_cmp.baselineWorktime.sum().total_seconds()*100.) if 'pbcmpID' in df.columns else 0
    
    
    for project in pmt_x_fe['projects']:
        project['link'] = project['extURL'] + project['extSubpath']

        if 'extFields' in project:
            extfields = json.loads(project['extFields'])
            for field in extfields:
                project[field] = extfields[field]
            del project['extFields']

        if 'statusCategory' in project:
            # if project['statusCategory'] == "To Do": project['statusColor'] = "green"
            if project['statusCategory'] == "In Progress": project['statusColor'] = "#B3DBFF"
            if project['statusCategory'] == "Done": project['statusColor'] = "#80FF80"

        if "pbID" in project: 
            pmt_x_fe['summary_baseline_total'] += 1
            if "actualStart" not in project and "actualEnd" not in project: pmt_x_fe['summary_baseline_awaits'] += 1
            if "actualStart" in project and "actualEnd" not in project: pmt_x_fe['summary_baseline_started'] += 1 
            if "actualEnd" in project: pmt_x_fe['summary_baseline_finished'] += 1 
        
        if "pbcmpID" in project: 
            pmt_x_fe['summary_baseline_cmp_total'] += 1
            if "baselineStart" not in project and "baselineEnd" not in project: pmt_x_fe['summary_baseline_cmp_awaits'] += 1
            if "baselineStart" in project and "baselineEnd" not in project: pmt_x_fe['summary_baseline_cmp_started'] += 1 
            if "baselineEnd" in project: pmt_x_fe['summary_baseline_cmp_finished'] += 1 

    return pmt_x_fe





if __name__ == "__main__":
    url = "http://192.168.5.20:8080/"

    projects = form_anychart_and_summary(url, "", "", "")
    # print(projects)

