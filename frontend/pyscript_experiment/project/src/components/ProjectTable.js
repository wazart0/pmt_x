import React, { Fragment } from "react";





function ProjectTable(props) {

    function sayHello() {
        alert('Hello!');
      }

    const columns = props.columns;
    const data = props.data;
    let headers_names = Object.values(columns);
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
                        let number_of_baselines = project.baselines.length + 1;
                        return (
                            <Fragment>
                                <tr>
                                    <td rowSpan={number_of_baselines}>{project.id}</td>
                                    <td rowSpan={number_of_baselines}>{(project.baselines && project.baselines.length) ? project.baselines[0].wbs : ""}</td>
                                    <td rowSpan={number_of_baselines}><button onClick={sayHello}>+</button> {project.name}</td>
                                    <td rowSpan={number_of_baselines}>{project.description}</td>
                                </tr>
                                {project.baselines.map(baseline => (
                                    <tr>
                                        <td>{baseline.worktime}</td>
                                        <td>{baseline.start}</td>
                                        <td>{baseline.finish}</td>
                                        <td>{baseline.parent}</td>
                                        <td>{(baseline.predecessors) ? JSON.stringify(baseline.predecessors) : ""}</td>
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