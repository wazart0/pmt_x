from typing import Optional

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel



app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"Hello": "World"}



class TaskAllocatorInput(BaseModel):
    url: str
    baseline_id: str
    project_id: str

@app.post("/allocate_single_task/")
def allocate_single_task(item: TaskAllocatorInput):
    input_json = jsonable_encoder(item)

    import allocate_single_task_to_resource as t

    dfp, dfd, dfr = t.get_dfp_dfd(input_json['url'], input_json['baseline_id'])
    solver, err_msg = t.assign_project(dfp, dfd, dfr, input_json['project_id'])
    if err_msg:
        return {"project_id": input_json['project_id'], "error": err_msg}

    t.send_to_pmtx(input_json['url'], solver, input_json['baseline_id'])

    index = solver.projects[solver.projects.project_id == input_json['project_id']].index[0]
    return {"project_id": input_json['project_id'], "start": solver.projects.loc[index, 'start'], "finish": solver.projects.loc[index, 'finish']}



@app.post("/baseline_merge/{item_id}")
def update_item(item_id: int, item: TaskAllocatorInput):
    return {"item_name": item.name, "item_id": item_id}





class CreateBaseline(BaseModel):
    url: str
    src_baseline_id: str
    trg_baseline_name: str

@app.post("/create_baseline/")
def create_baseline(item: CreateBaseline):
    
    return {"new_baseline_id": ""}




class JiraSynchronizer(BaseModel):
    url: str
    project_id: str
    jiraUrl: str
    jql: str

@app.post("/import_missing_issues_from_jira/")
def import_missing_issues_from_jira(item: JiraSynchronizer):
    
    return {"new_projects": ""}
