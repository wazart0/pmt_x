import React from "react";
import { Fragment, useState } from "react";



// class ProjectTable extends React.Component {
//     renderListItem(ingredient, i) {
//       return React.createElement("li", { key: i }, ingredient)
//     }
  
//     render() {
//         return (
//             <div className="projectTable">
//                 <button onClick={remove}>[-]</button>
//                 <button onClick={reset}>[+]</button>
//                 <table>
//                     <thead>
//                         <tr>
//                             {headers_names.map(header => {
//                                 return <th>{header}</th>
//                             })}
//                         </tr>
//                     </thead>
//                     <tbody>
//                         {data.map((project) => {
//                             if (project.hide) return (null);
//                             let number_of_baselines = project.baselines.length + 1;
//                             let wbs = (project.baselines && project.baselines.length) ? project.baselines[0].wbs : "";
//                             return (
//                                 <Fragment>
//                                     <tr>
//                                         <td rowSpan={number_of_baselines}>{project.id}</td>
//                                         <td rowSpan={number_of_baselines}>{wbs} </td>
//                                         <td rowSpan={number_of_baselines} style={{paddingLeft: incTabs(wbs) + 'px'}}>{project.name}</td>
//                                         {/* <td rowSpan={number_of_baselines}><button onClick={sayHello}>+</button> {project.name}</td> */}
//                                         <td rowSpan={number_of_baselines}>{project.description}</td>
//                                     </tr>
//                                     {project.baselines.map(baseline => (
//                                         <tr>
//                                             <td>{baseline.worktime}</td>
//                                             <td>{baseline.start}</td>
//                                             <td>{baseline.finish}</td>
//                                             <td>{baseline.parent}</td>
//                                             <td>{(baseline.predecessors) ? JSON.stringify(baseline.predecessors) : ""}</td>
//                                         </tr>
//                                     ))}
//                                 </Fragment>
//                             );
//                         })}
//                     </tbody>
//                 </table>
//             </div>
//         );
//     }
// }

function hideSubTree(treeData, parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let children_list = [parent_id];
    treeData[parent_id].hiddenChildren = true;
    for (let item in treeData) {
        // console.log("for loop");
        // console.log(treeData[item]);
        if (children_list.includes(treeData[item].parent)) {
            // console.log("parent found");
            // console.log(treeData[item]);
            treeData[item]['hidden'] = true;
            if (treeData[item].hasChildren) children_list.append(treeData[item].id);
            // console.log(treeData[item]);
        }
    }
}

function showSubTree(treeData, parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let children_list = [parent_id];
    let children_keep_hidden = [];
    treeData[parent_id].hiddenChildren = false;
    for (let item in treeData) {
        // console.log("for loop");
        // console.log(treeData[item]);
        if (children_list.includes(treeData[item].parent)) {
            // console.log("parent found");
            // console.log(treeData[item]);
            if (children_keep_hidden.includes(treeData[item].parent)) {
                if (treeData[item].hasChildren) children_keep_hidden.append(treeData[item].id);
            }
            else {
                treeData[item]['hidden'] = false;
            }
            if (treeData[item].hasChildren) children_list.append(treeData[item].id);
            // console.log(treeData[item]);
        }
    }
}

function incTabs(wbs) {
    // let doc = document.getElementById("td"); TODO: check how to retireve left padding from CSS (now it is hardcoded: 5)
    // let standardPadding = doc.style.paddingLeft;
    let  amount = String(wbs).match(/\./g)
    if (!amount) return String(5);
    return String(5 + 25 * amount.length);
}



function ProjectTable(props) {
    const [, updateState] = useState();

    let columns = props.columns;
    let data = props.data;
    let headers_names = Object.values(columns);


    function hideChildren(parent_id) {
        hideSubTree(data, data[parent_id].id)
        updateState({});
    }

    function showChildren(parent_id) {
        showSubTree(data, data[parent_id].id)
        updateState({});
    }

    function updateValueFromCell(e, id, field) {
        if (data[id][field] !== e.target.textContent) {
            data[id][field] = e.target.textContent;
            console.log("TODO: Implement data update in DB.");
        }
        console.log("Update " + String(id) + " " + data[id].name + " ");
    }

    // function generateColumns(column_key) {

    // }

    return (
        <div className="projectTable">
            <table>
                <thead>
                    <tr>
                        {headers_names.map(header => {
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
                                    <td rowSpan={number_of_baselines}>{project.id}</td>
                                    <td rowSpan={number_of_baselines}>{project.wbs} {project.hasChildren ? project.hiddenChildren ? <button onClick={() => showChildren(project.id)}>[+]</button> : <button onClick={() => hideChildren(project.id)}>[-]</button> : null}</td>
                                    {/* <td rowSpan={number_of_baselines} style={{paddingLeft: incTabs(project.wbs) + 'px'}}>{project.name}</td> */}
                                    <td rowSpan={number_of_baselines} style={{paddingLeft: incTabs(project.wbs) + 'px'}}><div suppressContentEditableWarning='true' contentEditable='true' onBlur={(e) => updateValueFromCell(e, project.id, "name")}>{project.name}</div></td>
                                    <td rowSpan={number_of_baselines}>{project.description}</td>

                                    <td style={{textAlign: 'center'}}>{project.worktime}</td>
                                    <td style={{textAlign: 'center'}}>{project.parent}</td>
                                    <td>{project.predecessors ? JSON.stringify(project.predecessors) : null}</td>
                                    <td style={{textAlign: 'center'}}>{project.start}</td>
                                    <td style={{textAlign: 'center'}}>{project.finish}</td>

                                </tr>
                                {project.baselines.map(baseline => (
                                    <tr style={{fontSize: '75%'}}>
                                        <td style={{textAlign: 'center'}}>{baseline.worktime}</td>
                                        <td style={{textAlign: 'center'}}>{baseline.parent}</td>
                                        <td>{baseline.predecessors ? JSON.stringify(baseline.predecessors) : null}</td>
                                        <td style={{textAlign: 'center'}}>{baseline.start}</td>
                                        <td style={{textAlign: 'center'}}>{baseline.finish}</td>
                                    </tr>
                                ))}
                            </Fragment>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}




export default ProjectTable;