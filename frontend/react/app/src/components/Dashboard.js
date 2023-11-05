import React, { Component } from "react"
import {ProjectList, ProjectListRenderer} from "./ProjectListRenderer"
import { sortByWBS } from "./ProjectVars"
import * as demo from "./tmpData"
import { marked } from 'marked'
import DOMPurify from 'dompurify'




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

        this.console = console

        this.data = this.state.data //structuredClone(demo.data)
        this.columns = structuredClone(demo.columns)

        this.websocket = new WebSocket("ws://localhost:8000/taskslist");
        this.websocket.onmessage = this.newTasksList
        
        // sortByWBS(this.data)

        this.details = null
    }

    newTasksList = (e) => {
        this.data = JSON.parse(e.data)
        this.setState({
            'data': this.data
        })
    }

    sendMessage = (message) => {
        this.websocket.send(JSON.stringify(message))
    }

    // ws.onmessage = function(event) {
    //     var messages = document.getElementById('messages')
    //     var message = document.createElement('li')
    //     var content = document.createTextNode(event.data)
    //     message.appendChild(content)
    //     messages.appendChild(message)
    // };

    // function sendMessage(event) {
    //     var input = document.getElementById("messageText")
    //     ws.send(input.value)
    //     input.value = ''
    //     event.preventDefault()
    // }

    showProjectDetails = (id) => {
        this.details = ProjectDetailsComponent(this.data, this.data[id], this.closeProjectDetails)
        this.setState({})
    }

    closeProjectDetails = () => {
        this.details = null
        this.setState({})
    }


    render() {
        return (
            <div className="mainContainer">
                <button onClick={() => this.sendMessage({})}>GET DATA</button>
                {/* <div display='flex' flexDirection='row'> */}
                    {/* <ProjectList state={this.state} columns={this.columns} showProjectDetails={this.showProjectDetails} /> */}
                    <ProjectListRenderer state={this.state} columns={this.columns}/>
                    {this.details}
                {/* </div> */}
                <div>{this.console.render()}</div>
            </div>
        )
    }
}


export default Dashboard