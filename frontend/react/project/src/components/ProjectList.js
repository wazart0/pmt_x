import React, { Component, Fragment } from "react"
import { addProject, sortByWBS, resetIDs } from "./ProjectVars"
import { hideSubTree, showSubTree, changeParent } from "./ProjectListTreeManager"
// import Modal from "./Modal"
import { isString } from "./utils.js"






class ProjectList extends Component {
    constructor({data, columns, showProjectDetails}) {
        super()

        this.data = data
        this.columns = columns

        this.showProjectDetails = showProjectDetails
    }
  

    hideChildren = (id) => {
        hideSubTree(this.data, id)
        this.setState({})
    }

    showChildren = (id) => {
        showSubTree(this.data, id)
        this.setState({})
    }

    updateValueFromCell = (e, id, column) => {
        e.target.textContent = e.target.textContent.trim()
        if (e.target.textContent === String(this.data[id][column])) return
        switch (column) {
            case 'name':
                if (!e.target.textContent) { e.target.textContent = this.data[id][column]; return; }
                this.data[id][column] = e.target.textContent;
                break

            case 'parent':
                let result = changeParent(this.data, id, e.target.textContent !== '' ? Number(e.target.textContent) : null)
                e.target.textContent = this.data[id][column]
                if (!result) return
                break

            case 'predecessors':
                this.data[id][column] = e.target.textContent;
                break

            default:
                this.data[id][column] = e.target.textContent;
        }
        // if (column === 'name' && !e.target.textContent) { e.target.textContent = this.data[id][column]; return; }
        // if (column === 'parent') {
        //     let result = changeParent(this.data, id, e.target.textContent !== '' ? Number(e.target.textContent) : null)
        //     e.target.textContent = this.data[id][column]
        //     if (!result) return  
        // }
        // if (column === 'predecessors') {
// validate format
// regex: ((([0-9]*[sfSF]{2}\s*\+\s*[0-9]+)|([0-9]*[sfSF]{2})),\s*)|(([0-9]*[sfSF]{2}\s*\+\s*[0-9]+)|([0-9]*[sfSF]{2})) https://regexr.com/
// asdf
// 2fs
// 2FS
// 2SF
// 3SS
// 2ss
// 3ff
// 234sf
// 23435ffsdf
// 23435ff+12
// 23435ff + 12
// 23435ff+12, 34sf
// 23435ff + 12, 234ff+24
// send to BE on que
        //     e.target.textContent = this.data[id][column]
        //     if (!result) return  
        // } else {
        //     this.data[id][column] = e.target.textContent;
        //     console.log("Updated task: [" + String(id) + "] column: [" + column + "] to: [" + this.data[id][column]+ "] ")
        // }
        console.log("Updated task: [" + String(id) + "] column: [" + column + "] to: [" + this.data[id][column]+ "] ")
        console.log("TODO: Implement data update in DB.")
        this.setState({})
    }

    addNewProject = (e) => {
        if (!e.target.textContent.trim()) return
        let id = addProject(this.data, e.target.textContent.trim())
        e.target.textContent = ''                                     //                                      TODO:         why is it needed!?
        console.log("TODO: Implement data update in DB.")
        console.log("Created task: [" + String(id) + "] to: [" + this.data[id].name+ "] ")
        this.setState({})
    }

    addToBaseline = (id) => {
        let no_of_new_siblings = 1
        for (let index in this.data) {
            if (this.data[index].parent === null && this.data[index].wbs) {
                no_of_new_siblings = no_of_new_siblings + 1
            }
        }
        this.data[id].wbs = String(no_of_new_siblings)
        sortByWBS(this.data)
        resetIDs(this.data)
        console.log("TODO: Implement data update in DB.")
        this.setState({})
    }
    

    render() {
        return (
            <div className="projectList">
                <ProjectListComponent 
                    data={this.data}
                    columns={this.columns}
                    showProjectDetails={this.showProjectDetails}
                    hideChildren={this.hideChildren}
                    showChildren={this.showChildren}
                    updateValueFromCell={this.updateValueFromCell}
                    addNewProject={this.addNewProject}
                    addToBaseline={this.addToBaseline}
                />
            </div>
        )
    }
}






const ProjectListComponent = ({data, columns, showProjectDetails, hideChildren, showChildren, updateValueFromCell, addNewProject, addToBaseline}) => {

    function incTabs(wbs) {
        // let doc = document.getElementById("td"); TODO: check how to retireve left padding from CSS (now it is hardcoded: 5)
        // let standardPadding = doc.style.paddingLeft;
        let  amount = String(wbs).match(/\./g)
        if (!amount) return String(5)
        return String(5 + 25 * amount.length)
    }

    function divEditable(id, column, value) {
        return <div suppressContentEditableWarning='true' contentEditable='true' onBlur={(e) => updateValueFromCell(e, id, column)}>{value}</div>
    }

    function td(project, number_of_baselines, column) {
        if (column === 'id') return <td rowSpan={number_of_baselines}>{project.id}</td>;
        if (column === 'wbs') return <td rowSpan={number_of_baselines}>{project.wbs ? project.wbs : <button onClick={() => addToBaseline(project.id)}>ADD</button>} {project.hasChildren ? project.hiddenChildren ? <button onClick={() => showChildren(project.id)}>[+]</button> : <button onClick={() => hideChildren(project.id)}>[-]</button> : null}</td>
        if (column === 'name') return <td rowSpan={number_of_baselines} style={{marginLeft: incTabs(project.wbs) + 'px'}}>{divEditable(project.id, column, project[column])}</td>
        if (column === 'details') return <td rowSpan={number_of_baselines}><button onClick={() => showProjectDetails(project.id)}>OPEN</button></td>
        if (column === 'description') return <td rowSpan={number_of_baselines}>{divEditable(project.id, column, project[column])}</td>

        if (column === 'worktime') return <td style={{textAlign: 'center'}}>{divEditable(project.id, column, project[column])}</td>
        if (column === 'parent') return <td style={{textAlign: 'center'}}>{divEditable(project.id, column, project[column])}</td>
        if (column === 'predecessors') return <td>{divEditable(project.id, column, project[column])}</td>
        if (column === 'start') return <td style={{textAlign: 'center'}}>{project.start}</td>
        if (column === 'finish') return <td style={{textAlign: 'center'}}>{project.finish}</td>
        return <td></td>
    }

    function tdLast(column) {
        if (column === 'id') return <td>{data.length}</td>
        if (column === 'name') return <td><div suppressContentEditableWarning='true' contentEditable='true' onBlur={addNewProject}>{null}</div></td>
        return <td></td>
    }

    function tdBaseline(baseline, column) {
        // TODO: check how to retrieve styles and adjust the original one
        if (column === 'worktime') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.worktime}</td>
        if (column === 'parent') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.parent}</td>
        if (column === 'predecessors') return <td style={{borderTop: '1px solid black'}}>{!isString(baseline.predecessors) ? JSON.stringify(baseline.predecessors) : null}</td>
        if (column === 'start') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.start}</td>
        if (column === 'finish') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.finish}</td>
        return (null)
    }
    

    return (
        <div className="projectTable">
            <table>
                <thead>
                    <tr>
                        {Object.values(columns).map(header => {
                            return <th>{header}</th>
                        })}
                    </tr>
                </thead>
                <tbody>
                    {data.map((project) => {
                        if (project.hidden) return (null);
                        let number_of_baselines = project.baselines.length + 1;
                        return (
                            <Fragment>
                                <tr key={project.id}>
                                    {Object.keys(columns).map(column => (
                                        td(project, number_of_baselines, column)
                                    ))}
                                </tr>
                                {project.baselines.map(baseline => (
                                    <tr style={{fontSize: '75%'}}>
                                        {Object.keys(columns).map(column => (
                                            tdBaseline(baseline, column)
                                        ))}
                                    </tr>
                                ))}
                            </Fragment>
                        );
                    })}
                    <tr>
                        {Object.keys(columns).map(column => (
                            tdLast(column)
                        ))}
                    </tr>
                </tbody>
            </table>
        </div>
    )
}




export default ProjectList
