import React from "react";
import { Fragment, useState } from "react";
import { columns, data, addProject } from "./ProjectVars";
import { hideSubTree, showSubTree, changeParent } from "./ProjectListTreeManager";





function incTabs(wbs) {
    // let doc = document.getElementById("td"); TODO: check how to retireve left padding from CSS (now it is hardcoded: 5)
    // let standardPadding = doc.style.paddingLeft;
    let  amount = String(wbs).match(/\./g)
    if (!amount) return String(5);
    return String(5 + 25 * amount.length);
}

function ProjectList() {
    const [, updateProjectListState] = useState();

    function hideChildren(parent_id) {
        hideSubTree(data[parent_id].id)
        updateProjectListState({});
    }

    function showChildren(parent_id) {
        showSubTree(data[parent_id].id)
        updateProjectListState({});
    }

    function updateValueFromCell(e, id, column) {
        e.target.textContent = e.target.textContent.trim();
        if (!e.target.textContent || e.target.textContent === String(data[id][column])) return;
        console.log(column);
        if (column === 'parent') { 
            let result = changeParent(id, Number(e.target.textContent))
            e.target.textContent = data[id][column];
            if (!result) return  
        } else {
            data[id][column] = e.target.textContent;
        }
        console.log("TODO: Implement data update in DB.");
        console.log("Updated task: [" + String(id) + "] column: [" + column + "] to: [" + data[id][column]+ "] ");
        updateProjectListState({});
    }

    function addNewProject(e) {
        if (!e.target.textContent.trim()) return;
        let id = addProject(e.target.textContent.trim()); 
        e.target.textContent = '';                                     //                                      TODO:         why is it needed!?
        console.log("TODO: Implement data update in DB.");
        console.log("Created task: [" + String(id) + "] to: [" + data[id].name+ "] ");
        updateProjectListState({});
    }

    function divEditable(id, column, value) {
        return <div suppressContentEditableWarning='true' contentEditable='true' onBlur={(e) => updateValueFromCell(e, id, column)}>{value}</div>;
    }

    function td(project, number_of_baselines, column) {
        if (column === 'id') return <td rowSpan={number_of_baselines}>{project.id}</td>;
        if (column === 'wbs') return <td rowSpan={number_of_baselines}>{project.wbs} {project.hasChildren ? project.hiddenChildren ? <button onClick={() => showChildren(project.id)}>[+]</button> : <button onClick={() => hideChildren(project.id)}>[-]</button> : null}</td>;
        if (column === 'name') return <td rowSpan={number_of_baselines} style={{paddingLeft: incTabs(project.wbs) + 'px'}}>{divEditable(project.id, column, project[column])}</td>;
        if (column === 'description') return <td rowSpan={number_of_baselines}>{divEditable(project.id, column, project[column])}</td>;

        if (column === 'worktime') return <td style={{textAlign: 'center'}}>{divEditable(project.id, column, project[column])}</td>;
        if (column === 'parent') return <td style={{textAlign: 'center'}}>{divEditable(project.id, column, project[column])}</td>;
        if (column === 'predecessors') return <td>{divEditable(project.id, column, project.predecessors ? project.predecessors instanceof String ? project.predecessors : JSON.stringify(project.predecessors) : null)}</td>;
        if (column === 'start') return <td style={{textAlign: 'center'}}>{project.start}</td>;
        if (column === 'finish') return <td style={{textAlign: 'center'}}>{project.finish}</td>;
        return (null);
    }

    function tdLast(column) {
        if (column === 'id') return <td>{data.length}</td>;
        if (column === 'name') return <td><div suppressContentEditableWarning='true' contentEditable='true' onBlur={addNewProject}>{null}</div></td>;
        return <td></td>;
    }

    function tdBaseline(baseline, column) {
        // TODO: check how to retrieve styles and adjust the original one
        if (column === 'worktime') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.worktime}</td>;
        if (column === 'parent') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.parent}</td>;
        if (column === 'predecessors') return <td style={{borderTop: '1px solid black'}}>{baseline.predecessors ? JSON.stringify(baseline.predecessors) : null}</td>;
        if (column === 'start') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.start}</td>;
        if (column === 'finish') return <td style={{textAlign: 'center', borderTop: '1px solid black'}}>{baseline.finish}</td>;
        return (null);
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
    );
}




export default ProjectList;
