import React, { Component } from "react"
import {ProjectListRenderer} from "./ProjectListRenderer"
// import { sortByWBS } from "./ProjectListTreeManager"
import * as demo from "./tmpData"
// import { marked } from 'marked'
// import DOMPurify from 'dompurify'
import TasksListCallbacks from "./TasksListCallbacks"
import TasksListMessages from "./TasksListMessages"




// const ProjectDetailsComponent = (data, project, closeDetails) => {
//     function markedjs(markdown) { 
//         if (markdown === null) return null
//         return {__html: DOMPurify.sanitize(marked.parse(markdown))} 
//     }
//     const markup = markedjs(project.description);
//     function updateDescription(e) {
//         console.log('onBlur: description')
//         console.log(e)
//         console.log(e.target.attributes.projectid.value)
//         // data[Number(e.target.attributes.projectid.value)].description = e.target.textContent
//     }
//     return (
//         <div className="projectDetails">
//             <div>{project.wbs ? project.wbs + '. ' : null}{project.name}</div>
//             <textarea projectid={project.id} rows="6" cols="50" onBlur={updateDescription}>
//             </textarea>
//             <div dangerouslySetInnerHTML={markup}></div>
//             <button onClick={closeDetails}>CLOSE</button>
//         </div>
//     )
// }




export const ViewComponent = ({viewList, dashboard, selectViewCallback, createViewCallback}) => {
    let viewName = dashboard.userView['name'] !== undefined ? dashboard.userView['name'] : ''
    return (
        <div className="view_management_component">
            Select view:
            &nbsp;
            <select onChange={selectViewCallback} name="view_id_selector" id="view_id_selector">
                {Object.keys(viewList).map((viewId, index) => (
                    <option key={index} value={viewId}>{viewList[viewId]}</option>
                ))}
            </select>
            &nbsp;
            Save as new view:
            &nbsp;
            <div id="new_view_name_input_field" name="new_view_name_input_field"
                suppressContentEditableWarning='true' 
                contentEditable='true' 
                style={{border: "1px solid blue", display: "inline-block", width: '100px'}}
                onBlur={(e) => viewName=e.target.textContent.trim()}>{
                    viewName
            }</div>
            &nbsp;
            <button onClick={createViewCallback}>SAVE VIEW</button>
        </div>
    )
}


export const FilterComponent = ({dashboard, searchButtonCallback}) => {
    let filter = dashboard.userView['filter'] !== undefined ? dashboard.userView['filter'] : ''
    return (
        <div className="filter_component">
            Filter:
            &nbsp;
            <div id="filter_input_field" name="filter_input_field"
                suppressContentEditableWarning='true' 
                contentEditable='true' 
                style={{border: "1px solid blue", display: "inline-block", width: '900px'}}
                onBlur={(e) => filter = e.target.textContent.trim()}>{
                    filter
            }</div>
            &nbsp;
            <button onClick={() => searchButtonCallback(filter)}>SEARCH</button>
        </div>
    )
}


export const BaselineComponent = ({dashboard, sendMessage}) => {
    let baselineName = dashboard.getPrimaryBaselineId() !== null ? dashboard.baselines[dashboard.getPrimaryBaselineId()]['name'] : ''
    return (
        <div className="baseline_component">
            Select baseline:
            &nbsp;
            <select onChange={(e) => {dashboard.setPrimaryBaselineId(e.target.value)}} name="primary_baseline_selector" id="primary_baseline_selector">
                <option key='0' value='None'>None</option>
                {Object.keys(dashboard.baselines).map((baselineId, index) => (
                    <option key={index+1} value={baselineId}>{dashboard.baselines[baselineId]['name']}</option>
                ))}
            </select>
            &nbsp;
            Create new baseline:
            &nbsp;
            <input 
                type="text" 
                onChange={(e) => baselineName=e.target.value} 
                name="new_baseline_name" 
                defaultValue={baselineName}
            />
            &nbsp;
            <button onClick={() => sendMessage({'name': 'upsert_baseline', 'args': {'name': baselineName}})}>CREATE BASELINE</button>
            &nbsp;
            <button onClick={() => {
                if (dashboard.getPrimaryBaselineId() === null) return
                let baseline = structuredClone(dashboard.baselines[dashboard.getPrimaryBaselineId()])
                delete baseline['id']
                baseline['name'] = baselineName
                sendMessage({'name': 'upsert_baseline', 'args': baseline})
            }}>DUPLICATE BASELINE</button>
        </div>
    )
}



class Tasks {
    constructor(rerender) {
        this.init()
        this.rerender = rerender
    }

    init = () => {
        this.tasksList = []
        this.tasks = {}
        this.baselines = {}
        this.userView = {}
    }

    getPrimaryBaselineId = () => (this.userView['doc'] !== undefined && this.userView['doc']['primaryBaselineId'] !== undefined ? this.userView['doc']['primaryBaselineId'] : null)

    getName = (id) => (this.tasks[id]['name'])
    getDescription = (id) => (this.tasks[id]['description'])

    getWBS = (id, baselineId = this.getPrimaryBaselineId()) => 
        (this.baselines[baselineId] !== undefined ? this.baselines[baselineId][id]['wbs'] : null)
    getWorktime = (id, baselineId = this.getPrimaryBaselineId()) => 
        (this.baselines[baselineId] !== undefined ? this.baselines[baselineId][id]['worktime'] : null)
    getParent = (id, baselineId = this.getPrimaryBaselineId()) => 
        (this.baselines[baselineId] !== undefined ? this.baselines[baselineId][id]['parent'] : null)
    getPredecessors = (id, baselineId = this.getPrimaryBaselineId()) => 
        (this.baselines[baselineId] !== undefined ? this.baselines[baselineId][id]['predecessors'] : null)
    getStart = (id, baselineId = this.getPrimaryBaselineId()) => 
        (this.baselines[baselineId] !== undefined ? this.baselines[baselineId][id]['start'] : null)
    getFinish = (id, baselineId = this.getPrimaryBaselineId()) => 
        (this.baselines[baselineId] !== undefined ? this.baselines[baselineId][id]['finish'] : null)

    getHidden = (id) => (this.userView['doc']['tasks'][id]['hidden'])
    getHiddenChildren = (id) => (this.userView['doc']['tasks'][id]['hiddenChildren'])
    getHasChildren = (id) => (this.userView['doc']['tasks'][id]['hasChildren'])

    setPrimaryBaselineId = (id) => {
        if (this.userView['id'] === undefined) return
        this.userView['doc']['primaryBaselineId'] = id === 'None' ? null : id
        this.rerender()
    }

    insertTask = (task) => {
        if (this.userView['doc'] === undefined) this.userView['doc'] = {}
        if (this.userView['doc']['tasks'] === undefined) this.userView['doc']['tasks'] = {}
        this.tasks[task['id']] = task
        this.userView['doc']['tasks'][task['id']] = {
            'hidden': false,
            'hasChildren': false,
            'hiddenChildren': false
        }
        this.tasksList.push(task['id'])
    }
}



class Dashboard extends Component {
    constructor({console}) {
        super()
        this.state = {}

        this.new_view_name_field = 'default'

        this.userList = {}
        this.userCurrentId = null

        this.viewList = {}

        this.dashboardData = new Tasks(this.rerender)


        this.columns = structuredClone(demo.columns)

        this.tasksMessages = new TasksListMessages("ws://localhost:8000/taskslist")
        this.tasksMessages.onmessage = this.newTasksList

        this.tasksCallbacks = new TasksListCallbacks(this.tasksMessages, this.dashboardData)

        this.console = console
        this.details = null
    }


    newTasksList = (e) => {
        let data = JSON.parse(e.data)
        if (data['error']) {
            this.console.log(data['error'])
            console.log(data['error'])
            return
        }
        switch (data['type']) {
            case 'dashboard':
                this.dashboardData.tasks = data['data']['tasks']
                this.dashboardData.baselines = data['data']['baselines']
                this.dashboardData.userView = data['data']['userView']

                this.dashboardData.tasksList = Object.keys(this.dashboardData['tasks'])
                if (!this.dashboardData.userView['doc']) this.dashboardData.userView['doc'] = {}
                if (!this.dashboardData.userView['doc']['tasks']) this.dashboardData.userView['doc']['tasks'] = {}
                this.dashboardData.tasksList.forEach((taskId) => {
                    if (!this.dashboardData.userView['doc']['tasks'][taskId]) { // check if parent, etc...
                        this.dashboardData.userView['doc']['tasks'][taskId] = {
                            'hidden': false,
                            'hasChildren': false,
                            'hiddenChildren': false
                        }
                    }
                })

                // sortByWBS(this.dashboardData['baseline'])
                break

            case 'userList':
                this.userList = data['data']
                this.dashboardData.init()
                if (Object.keys(data['data'])[0]) {
                    this.userCurrentId = Object.keys(data['data'])[0]
                    this.tasksMessages.getViews(this.userCurrentId)
                }
                break

            case 'userViewList':
                this.viewList = data['data']
                if (Object.keys(this.viewList).length === 0) this.dashboardData.init()
                if (Object.keys(data['data'])[0]) {
                    this.dashboardData['viewId'] = Object.keys(data['data'])[0]
                    this.tasksMessages.getDashboard(this.userCurrentId, this.dashboardData['viewId'])
                }
                break

            case 'tasks':
                if (!this.dashboardData['userView']['doc']) this.dashboardData['userView']['doc'] = {}
                if (!this.dashboardData['userView']['doc']['tasks']) this.dashboardData['userView']['doc']['tasks'] = {}
                Object.keys(data['data']).forEach((key) => {
                    this.dashboardData['tasks'][key] = data['data'][key]
                    if (!this.dashboardData['userView']['doc']['tasks'][key]) { // check if parent, etc...
                        this.dashboardData['userView']['doc']['tasks'][key] = {
                            'hidden': false,
                            'hasChildren': false,
                            'hiddenChildren': false
                        }
                    }
                })
                this.dashboardData['tasksList'] = Object.keys(this.dashboardData['tasks'])
                break

                case 'task':
                    this.dashboardData.insertTask(data['data'])
                    break

            case 'baselines':
                Object.keys(data['data']).forEach((key) => {
                    this.dashboardData['baselines'][key] = data['data'][key]
                })
                break

            default:
                return
        }

        this.setState({})
    }

    rerender = () => this.setState({})

    sendMessage = (message) => {
        this.tasksMessages.send(JSON.stringify(message))
    }


    showPrimaryBaseline = (e) => {
        this.dashboardData.userView['doc']['primaryBaseline'] = e.target.value ? e.target.value !== 'null' : null
        this.setState({})
    }


    applyNewFilter = (filter) => {
        if (this.dashboardData.userView['id'] === undefined) return
        filter = filter.trim()
        if (filter === String(this.dashboardData.userView['filter'])) return
        this.dashboardData.userView['filter'] = filter
        this.sendMessage({'name': 'upsert_view', 'args': {'id': this.dashboardData.userView['id'], 'filter': this.dashboardData.userView['filter']}})
        this.tasksMessages.getDashboard(this.userCurrentId, this.dashboardData.userView['id'])
    }


    createNewView = () => {
        if (this.userCurrentId === null) return
        this.sendMessage({
            'name': 'upsert_view', 
            'args': {
                'user_id': this.userCurrentId, 
                'name': this.new_view_name_field, 
                'filter': ''
            }})
    }


    selectView = (e) => {
        if (this.userCurrentId === null) return
        this.tasksMessages.getDashboard(this.userCurrentId, e.target.value)
    }

    // showProjectDetails = (id) => {
    //     this.details = ProjectDetailsComponent(this.data, this.data[id], this.closeProjectDetails)
    //     this.setState({})
    // }


    // closeProjectDetails = () => {
    //     this.details = null
    //     this.setState({})
    // }


    render() {
        console.log('Dashboard rendering')
        return (
            <div className="mainContainer">

                TEMP SECTION:&nbsp;
                <button onClick={() => this.sendMessage({'name': 'get_users'})}>GET USERS</button>
                <select onChange={(e) => {
                    this.userCurrentId = e.target.value
                    this.tasksMessages.getViews(this.userCurrentId)
                }} name="user_id_selector" id="user_id_selector">
                    {Object.keys(this.userList).map((user_id, index) => (
                        <option key={index} value={user_id}>{this.userList[user_id]['username']}</option>
                    ))}
                </select>
                <br/>


                <ViewComponent viewList={this.viewList} dashboard={this.dashboardData} selectViewCallback={this.selectView} createViewCallback={this.createNewView} />

                <FilterComponent dashboard={this.dashboardData} searchButtonCallback={this.applyNewFilter} />

                <BaselineComponent dashboard={this.dashboardData} sendMessage={this.sendMessage} />

                {/* <div display='flex' flexDirection='row'> */}
                    {/* <ProjectList state={this.state} columns={this.columns} showProjectDetails={this.showProjectDetails} /> */}
                    <ProjectListRenderer dashboard={this.dashboardData} columns={this.columns} callbacks={this.tasksCallbacks} />
                    {this.details}
                {/* </div> */}
                {/* <div>{this.console.render()}</div> */}
            </div>
        )
    }
}


export default Dashboard
