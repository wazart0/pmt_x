import React, { Fragment } from "react";


const columns = {
    'id': 'ID',
    'wbs': 'WBS',
    'name': 'Name',
    'description': 'Description',
    'worktime': 'Worktime',
    'start': 'Start',
    'finish': 'Finish',
    'parent': 'Parent',
    'predecessors': 'Predecessors'
}

const data = [
    {
        'id': 0,
        'name': 'task one',
        'description': 'some desc',
        'baselines': [
            {
                'wbs': '1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': null,
                'predecessors': [
                    {
                        'project': { 'id': '2'},
                        'type': 'FS'
                    }
                ]
            },
            {
                'wbs': '1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': null
            }
        ]
    },
    {
        'id': 1,
        'name': 'task one one',
        'description': 'some desc',
        'baselines': [
            {
                'wbs': '1.1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': 0
            },
            {
                'wbs': '1.1',
                'worktime': '45',
                'start': '2023-09-15',
                'finish': '2023-09-23',
                'parent': 0
            },
            {
                'wbs': '1.1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': 0
            }
        ]
    },
    {
        'id': 2,
        'name': 'task two',
        'description': 'some desc',
        'baselines': [
            {
                'wbs': '2',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': null
            }
        ]
    },
    {
        'id': 3,
        'name': 'task three',
        'description': 'some desc',
        'baselines': []
    },
    {
        'id': 4,
        'name': 'task four',
        'description': 'some desc',
        'baselines': []
    }
]

// function create_table(data) {
//     var body = document.getElementsByTagName('body')[0];
//     var tbl = document.createElement('table');
//     tbl.style.width = '100%';
//     tbl.setAttribute('border', '1');
//     var tbdy = document.createElement('tbody');
//     for (var i = 0; i < 3; i++) {
//       var tr = document.createElement('tr');
//       for (var j = 0; j < 2; j++) {
//         if (i == 2 && j == 1) {
//           break
//         } else {
//           var td = document.createElement('td');
//           td.appendChild(document.createTextNode('\u0020'))
//           i == 1 && j == 1 ? td.setAttribute('rowSpan', '2') : null;
//           tr.appendChild(td)
//         }
//       }
//       tbdy.appendChild(tr);
//     }
//     tbl.appendChild(tbdy);
//     body.appendChild(tbl)
// }

function App() {
    let headers_names = Object.values(columns);
    return (
        <div className="table">
            <table>
                <thead>
                    <tr>
                        {
                            headers_names.map(header => {
                                return <th>{header}</th>
                            })
                        }
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
                                    <td rowSpan={number_of_baselines}>{project.name}</td>
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

export default App;