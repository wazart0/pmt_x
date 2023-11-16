import React, { Component, Fragment } from "react"
import { addProject, sortByWBS, resetIDs } from "./ProjectVars.js"
import { hideSubTree, showSubTree, changeParent, arePredecesorsLooped } from "./ProjectListTreeManager.js"
// import Modal from "./Modal"
import { isString } from "./utils.js"




export const ProjectListRenderer = ({state, columns, callbacks, showProjectDetails, updateValueFromCell}) => {
    const data = state.data

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
        switch (column) {
            case 'id':
                return <td rowSpan={number_of_baselines}>{project.id}</td>;
            case 'wbs':
                return <td rowSpan={number_of_baselines}>{project.wbs ? project.wbs : <button onClick={() => callbacks.addTaskToBaseline(project.id)}>ADD</button>} {project.hasChildren ? project.hiddenChildren ? <button onClick={() => callbacks.showSubTree(project.id)}>[+]</button> : <button onClick={() => callbacks.hideSubTree(project.id)}>[-]</button> : null}</td>
            case 'name':
                return <td rowSpan={number_of_baselines} style={{marginLeft: incTabs(project.wbs) + 'px'}}>{divEditable(project.id, column, project[column])}</td>
            case 'details':
                return <td rowSpan={number_of_baselines}><button onClick={() => showProjectDetails(project.id)}>OPEN</button></td>
            case 'description':
                return <td rowSpan={number_of_baselines}>{divEditable(project.id, column, project[column])}</td>
    
            case 'worktime':
                return <td style={{textAlign: 'center'}}>{divEditable(project.id, column, project[column])}</td>
            case 'parent':
                return <td style={{textAlign: 'center'}}>{divEditable(project.id, column, project[column])}</td>
            case 'predecessors':
                return <td>{divEditable(project.id, column, project[column])}</td>
            case 'start':
                return <td style={{textAlign: 'center'}}>{project.start}</td>
            case 'finish':
                return <td style={{textAlign: 'center'}}>{project.finish}</td>
            
            default:
                return <td></td>
        }
    }

    function tdLast(column) {
        switch (column) {
            case 'id': 
                return <td>{data.length}</td>
            case 'name': 
                return <td><div suppressContentEditableWarning='true' contentEditable='true' onBlur={callbacks.addTask}>{null}</div></td>
            default: 
                return <td></td>
        }
    }

    function tdBaseline(baseline, column) {
        switch (column) {
            // TODO: check how to retrieve styles and adjust the original one
            case 'worktime':
                return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.worktime}</td>
            case 'parent':
                return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.parent}</td>
            case 'predecessors':
                return <td style={{borderTop: '1px solid black'}}>{!isString(baseline.predecessors) ? JSON.stringify(baseline.predecessors) : null}</td>
            case 'start':
                return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.start}</td>
            case 'finish':
                return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.finish}</td>
            
            default:
                return (null)
        }
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



