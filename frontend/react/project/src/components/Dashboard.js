import React, { Component } from "react"
import ProjectList from "./ProjectList"
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

        this.console = console

        this.data = structuredClone(demo.data)
        this.columns = structuredClone(demo.columns)
        
        sortByWBS(this.data)

        this.details = null
    }


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
                {/* <div display='flex' flexDirection='row'> */}
                    <ProjectList data={this.data} columns={this.columns} showProjectDetails={this.showProjectDetails} />
                    {this.details}
                {/* </div> */}
                <div>{this.console.render()}</div>
            </div>
        )
    }
}


export default Dashboard