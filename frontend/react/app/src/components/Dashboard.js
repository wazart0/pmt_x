import React, { Component } from "react"
import {ProjectList, ProjectListRenderer} from "./ProjectListRenderer"
import { sortByWBS } from "./ProjectListTreeManager"
import * as demo from "./tmpData"
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import TasksListCallbacks from "./TasksListCallbacks"
import TasksListMessages from "./TasksListMessages"




const ProjectDetailsComponent = (data, project, closeDetails) => {

    function markedjs(markdown) { 
        if (markdown === null) return null
        return {__html: DOMPurify.sanitize(marked.parse(markdown))} 
    }
    const markup = markedjs(project.description);

    function updateDescription(e) {
        console.log('onBlur: description')
        console.log(e)
        console.log(e.target.attributes.projectid.value)
        // data[Number(e.target.attributes.projectid.value)].description = e.target.textContent
    }

    return (
        <div className="projectDetails">
            <div>{project.wbs ? project.wbs + '. ' : null}{project.name}</div>
            <textarea projectid={project.id} rows="6" cols="50" onBlur={updateDescription}>
            </textarea>
            <div dangerouslySetInnerHTML={markup}></div>
            <button onClick={closeDetails}>CLOSE</button>
        </div>
    )
}


class Dashboard extends Component {
    constructor({console}) {
        super()
        this.state = {
            'data': []
        }

        this.columns = structuredClone(demo.columns)

        this.tasksList = new TasksListMessages("ws://localhost:8000/taskslist")
        this.tasksList.onmessage = this.newTasksList
        this.tasksListCallbacks = new TasksListCallbacks(this.tasksList)

        this.console = console
        this.details = null
    }


    newTasksList = (e) => {
        let data = JSON.parse(e.data)
        sortByWBS(data)
        this.setState({ 'data': data })
    }


    sendMessage = (message) => {
        this.tasksList.send(JSON.stringify(message))
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
                <button onClick={() => this.sendMessage({})}>GET DATA</button>
                {/* <div display='flex' flexDirection='row'> */}
                    {/* <ProjectList state={this.state} columns={this.columns} showProjectDetails={this.showProjectDetails} /> */}
                    <ProjectListRenderer state={this.state} columns={this.columns} callbacks={this.tasksListCallbacks} />
                    {this.details}
                {/* </div> */}
                <div>{this.console.render()}</div>
            </div>
        )
    }
}


export default Dashboard