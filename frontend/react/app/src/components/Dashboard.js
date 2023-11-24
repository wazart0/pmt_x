import React, { Component } from "react"
import {ProjectListRenderer} from "./ProjectListRenderer"
// import { sortByWBS } from "./ProjectListTreeManager"
import * as demo from "./tmpData"
// import { marked } from 'marked'
// import DOMPurify from 'dompurify'
import TasksListCallbacks from "./TasksListCallbacks"




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


class Dashboard extends Component {
    constructor({messaging, console}) {
        super()
        this.state = {}

        this.tasks = { 'data': [] }

        this.userList = []
        this.userCurrentId = null

        this.viewList = {}

        this.dashboardData = {
            'viewId': null,
            'baselineId': null,
            'tasks': {},
            'tasksList': [],
            'baseline': {},
            'baselines': {},
            'userView': {}
        }

        this.columns = structuredClone(demo.columns)

        this.tasksMessages = messaging
        this.tasksMessages['websocket'].onmessage = this.newTasksList

        this.tasksCallbacks = new TasksListCallbacks(this.tasksMessages, this.tasks)

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
                this.dashboardData['tasks'] = data['data']['tasks']
                this.dashboardData['baseline'] = data['data']['baseline']
                this.dashboardData['baselines'] = data['data']['baselines']
                this.dashboardData['userView'] = data['data']['userView']

                this.dashboardData['tasksList'] = Object.keys(this.dashboardData['tasks'])
                if (!this.dashboardData['userView']['doc']) this.dashboardData['userView']['doc'] = {}
                if (!this.dashboardData['userView']['doc']['tasks']) this.dashboardData['userView']['doc']['tasks'] = {}
                this.dashboardData['tasksList'].forEach((taskId) => {
                    if (!this.dashboardData['userView']['doc']['tasks'][taskId]) { // check if parent, etc...
                        this.dashboardData['userView']['doc']['tasks'][taskId] = {
                            'hidden': false,
                            'hasChildren': false,
                            'hiddenChildren': false
                        }
                    }
                })
                // sortByWBS(this.dashboardData['baseline'])
                break

            case 'userList':
                this.userList = Object.keys(data['data'])
                if (Object.keys(data['data'])[0]) {
                    this.userCurrentId = Object.keys(data['data'])[0]
                    this.tasksMessages['websocket'].getViews(this.userCurrentId)
                }
                break

            case 'userViewList':
                this.viewList = data['data']
                if (Object.keys(data['data'])[0]) {
                    this.dashboardData['viewId'] = Object.keys(data['data'])[0]
                    this.tasksMessages['websocket'].getDashboard(this.userCurrentId, this.dashboardData['viewId'])
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

            default:
                return
        }

        this.setState({})
    }


    sendMessage = (message) => {
        this.tasksMessages['websocket'].send(JSON.stringify(message))
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
        return (
            <div className="mainContainer">
                <button onClick={() => this.sendMessage({'name': 'get_users'})}>GET USERS</button>
                <select onChange={(e) => {
                    this.userCurrentId = e.target.value
                    this.tasksMessages.getViews(this.userCurrentId)
                }} name="user_id_selector" id="user_id_selector">
                    {this.userList.map((user_id, index) => (
                        <option key={index} value={user_id}>{user_id}</option>
                    ))}
                </select>
                <br/>
                <select onChange={(e) => {
                    this.dashboardData['viewId'] = e.target.value
                    this.tasksMessages['websocket'].getDashboard(this.userCurrentId, this.dashboardData['viewId'])
                }} name="view_id_selector" id="view_id_selector">
                    {Object.keys(this.viewList).map((viewId, index) => (
                        <option key={index} value={viewId}>{this.viewList[viewId]['name']}</option>
                    ))}
                </select>
                {/* <select name="primary_baseline_id_selector" id="primary_baseline_id_selector">
                    <option value="0">Baseline 0</option>
                    <option value="1">Baseline 1</option>
                    <option value="2">Baseline 2</option>
                    <option value="3">Baseline 3</option>
                </select>
                <select name="secondary_baseline_id_selector" id="secondary_baseline_id_selector" multiple>
                    <option value="0">Baseline 0</option>
                    <option value="1">Baseline 1</option>
                    <option value="2">Baseline 2</option>
                    <option value="3">Baseline 3</option>
                </select> */}
                <button onClick={() => this.sendMessage({'name': 'add_view', 'args': {'user_id': this.userCurrentId}})}>ADD VIEW</button>
                <br/>
                {/* <div display='flex' flexDirection='row'> */}
                    {/* <ProjectList state={this.state} columns={this.columns} showProjectDetails={this.showProjectDetails} /> */}
                    <ProjectListRenderer dashboard={this.dashboardData} columns={this.columns} callbacks={this.tasksCallbacks} />
                    {this.details}
                {/* </div> */}
                <div>{this.console.render()}</div>
            </div>
        )
    }
}


export default Dashboard