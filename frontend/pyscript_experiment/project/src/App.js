import React from "react";
import ProjectTable from "./components/ProjectTable";

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





function App() {
    
    return (
        <div className="mainContainer">
            <ProjectTable data={data} columns={columns}/>
        </div>
    );
}

export default App;