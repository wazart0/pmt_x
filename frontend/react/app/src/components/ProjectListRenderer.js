import React, { Fragment } from "react"
// import { addProject, sortByWBS, resetIDs } from "./ProjectVars.js"
// import { hideSubTree, showSubTree, changeParent, arePredecesorsLooped } from "./ProjectListTreeManager.js"
// import Modal from "./Modal"
import { isString } from "./utils.js"




export const ProjectListRenderer = ({dashboard, columns, callbacks, showProjectDetails}) => {

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
                return <td key={column} rowSpan={number_of_baselines}>{index}</td>

            case 'wbs':
                if (dashboard.getPrimaryBaselineId() === null) return <td key={column} rowSpan={number_of_baselines}></td> 
                if (!dashboard.getWBS()) 
                    return <td key={column} rowSpan={number_of_baselines}>
                        <button onClick={() => callbacks.addTaskToBaseline(taskId)}>ADD</button>
                    </td>
                if (!dashboard.getHasChildren(taskId))
                    return <td key={column} rowSpan={number_of_baselines}>
                        {dashboard.getWBS()}
                    </td>
                if (!dashboard.getHiddenChildren(taskId))
                    return <td key={column} rowSpan={number_of_baselines}>
                        {dashboard.getWBS()}
                        <button onClick={() => callbacks.hideSubTree(index)}>[-]</button>
                    </td>
                if (dashboard.getHiddenChildren(taskId))
                    return <td key={column} rowSpan={number_of_baselines}>
                        {dashboard.getWBS()}
                        <button onClick={() => callbacks.showSubTree(index)}>[+]</button>
                    </td>
                return <td key={column} rowSpan={number_of_baselines}></td>                

            case 'name':
                return <td key={column} rowSpan={number_of_baselines} style={{marginLeft: incTabs('') + 'px'}}>
                    <div key={column}
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateTaskName(e, taskId)}>
                            {dashboard.getName(taskId)}
                    </div>
                </td>

            case 'details':
                return <td key={column} rowSpan={number_of_baselines}>
                    <button onClick={() => showProjectDetails(taskId)}>OPEN</button>
                </td>

            case 'description':
                return <td key={column} rowSpan={number_of_baselines}>
                    <div key={column}
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateTaskDescription(e, taskId)}>{
                            dashboard.getDescription(taskId)
                    }</div>
                </td>
    
            case 'worktime':
                return <td key={column} style={{textAlign: 'center'}}>
                    <div key={column}
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateWorktime(e, taskId)}>{
                            dashboard.getWorktime(taskId)
                    }</div>
                </td>

            case 'parent':
                return <td key={column} style={{textAlign: 'center'}}>
                    <div key={column}
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updateParent(e, index)}>{
                            dashboard.getParent(taskId)
                    }</div>
                </td>

            case 'predecessors':
                return <td key={column}>
                    <div key={column}
                        suppressContentEditableWarning='true' 
                        contentEditable='true' 
                        onBlur={(e) => callbacks.updatePredecessors(e, index)}>{
                            dashboard.getPredecessors(taskId)
                    }</div>                    
                </td>

            case 'start':
                return <td key={column} style={{textAlign: 'center'}}>{
                    dashboard.getStart(taskId)
                }</td>

            case 'finish':
                return <td key={column} style={{textAlign: 'center'}}>{
                    dashboard.getFinish(taskId)
                }</td>
            
            default:
                return <td key={column}></td>
        }
    }

    function tdLast(column) {
        switch (column) {
            case 'id': 
                return <td key={column}></td>
            case 'name': 
                return <td key={column}><div key={column} suppressContentEditableWarning='true' contentEditable='true' onBlur={callbacks.addTask}>{null}</div></td>
            default: 
                return <td key={column}></td>
        }
    }

    function tdBaseline(baseline, column) {
        switch (column) {
            // TODO: check how to retrieve styles and adjust the original one
            case 'worktime':
                return <td key={column} style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.worktime}</td>
            case 'parent':
                return <td key={column} style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.parent}</td>
            case 'predecessors':
                return <td key={column} style={{borderTop: '1px solid black'}}>{!isString(baseline.predecessors) ? JSON.stringify(baseline.predecessors) : null}</td>
            case 'start':
                return <td key={column} style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.start}</td>
            case 'finish':
                return <td key={column} style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.finish}</td>
            
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
                        return <th key={header}>{header}</th>
                    })}
                </tr>
            </thead>
            <tbody>
                {dashboard.tasksList.map((taskId, index) => {
                    if (dashboard.getHidden(taskId)) return (null);
                    let numberOfBaselines = Object.keys(dashboard.baselines).length
                    if (!dashboard.defaultBaselineId) numberOfBaselines += 1
                    return (
                        <Fragment key={index}>
                            <tr key={index}>
                                {Object.keys(columns).map(column => (
                                    td(index, taskId, numberOfBaselines, column)
                                ))}
                            </tr>
                            {Object.keys(dashboard.baselines).map(baselineId => (
                                dashboard.defaultBaselineId === baselineId ? 
                                null : 
                                (<tr key={baselineId} style={{fontSize: '75%'}}>
                                    {Object.keys(columns).map(column => (
                                        tdBaseline(baselineId, column)
                                    ))}
                                </tr>)
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



