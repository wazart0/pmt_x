import React, { Fragment } from "react"
// import { addProject, sortByWBS, resetIDs } from "./ProjectVars.js"
// import { hideSubTree, showSubTree, changeParent, arePredecesorsLooped } from "./ProjectListTreeManager.js"
// import Modal from "./Modal"
import { isString } from "./utils.js"




export const ProjectListRenderer = ({dashboard, columns, callbacks, showProjectDetails, updateValueFromCell}) => {

    function incTabs(wbs) {
        // let doc = document.getElementById("td"); TODO: check how to retireve left padding from CSS (now it is hardcoded: 5)
        // let standardPadding = doc.style.paddingLeft;
        let  amount = String(wbs).match(/\./g)
        if (!amount) return String(5)
        return String(5 + 25 * amount.length)
    }

    function td(index, taskId, number_of_baselines, column) {
        switch (column) {
            case 'id':
                return <td rowSpan={number_of_baselines}>{index}</td>

            case 'wbs':
                return <td rowSpan={number_of_baselines}>
                    {dashboard['baseline'][taskId] ? dashboard['baseline'][taskId][column] : <button onClick={() => callbacks.addTaskToBaseline(taskId)}>ADD</button>}
                        {/* {project.wbs ? project.wbs : <button onClick={() => callbacks.addTaskToBaseline(index)}>ADD</button>}
                        {project.hasChildren ? project.hiddenChildren ? <button onClick={() => callbacks.showSubTree(index)}>[+]</button> : <button onClick={() => callbacks.hideSubTree(index)}>[-]</button> : null} */}
                </td>

            case 'name':
                return <td rowSpan={number_of_baselines} style={{marginLeft: incTabs('') + 'px'}}>
                    <div 
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateTaskName(e, taskId)}>
                            {dashboard['tasks'][taskId][column]}
                    </div>
                </td>

            case 'details':
                return <td rowSpan={number_of_baselines}>
                    <button onClick={() => showProjectDetails(taskId)}>OPEN</button>
                </td>

            case 'description':
                return <td rowSpan={number_of_baselines}>
                    <div 
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateTaskDescription(e, taskId)}>{
                            dashboard['tasks'][taskId]['doc'][column] ? dashboard['tasks'][taskId]['doc'][column] : ''
                    }</div>
                </td>
    
            case 'worktime':
                return <td style={{textAlign: 'center'}}>
                    <div 
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateWorktime(e, taskId)}>{
                            dashboard['baseline'][taskId] ? dashboard['baseline'][taskId][column] : ''
                    }</div>
                </td>

            case 'parent':
                return <td style={{textAlign: 'center'}}>
                    <div 
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateParent(e, index)}>{
                            dashboard['baseline'][taskId] ? dashboard['baseline'][taskId][column] : ''
                    }</div>
                </td>

            case 'predecessors':
                return <td>
                    <div 
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updatePredecessors(e, index)}>{
                            dashboard['baseline'][taskId] ? dashboard['baseline'][taskId][column] : ''
                    }</div>                    
                </td>

            case 'start':
                return <td style={{textAlign: 'center'}}>{
                    dashboard['baseline'][taskId] ? dashboard['baseline'][taskId][column] : ''
                }</td>

            case 'finish':
                return <td style={{textAlign: 'center'}}>{
                    dashboard['baseline'][taskId] ? dashboard['baseline'][taskId][column] : ''
                }</td>
            
            default:
                return <td></td>
        }
    }

    function tdLast(column) {
        switch (column) {
            case 'id': 
                return <td></td>
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
                    {dashboard['tasksList'].map((taskId, index) => {
                        if (dashboard['userView']['doc']['tasks'][taskId]['hidden']) return (null);
                        let number_of_baselines = Object.keys(dashboard['baselines']).length + 1;
                        return (
                            <Fragment>
                                <tr key={index}>
                                    {Object.keys(columns).map(column => (
                                        td(index, taskId, number_of_baselines, column)
                                    ))}
                                </tr>
                                {Object.keys(dashboard['baselines']).map(baselineId => (
                                    <tr style={{fontSize: '75%'}}>
                                        {Object.keys(columns).map(column => (
                                            tdBaseline(baselineId, column)
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



