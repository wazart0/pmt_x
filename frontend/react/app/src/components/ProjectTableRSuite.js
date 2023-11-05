import React from "react";
import { Table } from 'rsuite';



const demoData = [
    {
        'id': 0,
        'name': 'task one',
        'description': 'some desc',

        'wbs': '1',
        'worktime': '80',
        'start': '2023-09-12',
        'finish': '2023-09-26',
        'parent': null,
        'predecessors':  JSON.stringify([
            {
                'project': { 'id': '2'},
                'type': 'FS'
            }
        ]),

        'rowSpan': 2,

        'rowKey': 0,
        'children': [
            {
                'id': 1,
                'name': 'task one one',
                'description': 'some desc',
                
                'wbs': '1.1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': 0,
        
                'rowSpan': 3,
        
                'rowKey': 2
            },
            {
                'id': 1,
                'name': 'task one one',
                'description': 'some desc',
                
                'wbs': '1.1',
                'worktime': '45',
                'start': '2023-09-15',
                'finish': '2023-09-23',
                'parent': 0,
        
                'rowKey': 4
            },
            {
                'id': 1,
                'name': 'task one one',
                'description': 'some desc',
                
                'wbs': '1.1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': 0,
        
                'rowKey': 5
            }
        ]
    },
    {
        'id': 0,
        'name': 'task one',
        'description': 'some desc',

        'wbs': '1',
        'worktime': '80',
        'start': '2023-09-12',
        'finish': '2023-09-26',
        'parent': null,

        'rowKey': 1
    },
    {
        'id': 2,
        'name': 'task two',
        'description': 'some desc',
        
        'wbs': '2',
        'worktime': '80',
        'start': '2023-09-12',
        'finish': '2023-09-26',
        'parent': null,

        'rowKey': 6
    },
    {
        'id': 3,
        'name': 'task three',
        'description': 'some desc',

        'rowKey': 7
    },
    {
        'id': 4,
        'name': 'task four',
        'description': 'some desc',

        'rowKey': 8
    }
]


const { Column, HeaderCell, Cell } = Table;

function ProjectTable(props) {
    
    // const columns = props.columns;
    const data = (props.data) ? props.data : demoData;

    return (
        <div className="projectTable">
            <Table 
                isTree
                defaultExpandAllRows
                rowKey="rowKey"
                virtualized
                height={700}
                data={data}
            >
                
                <Column
                    // verticalAlign="middle"
                    rowSpan={rowData => { return rowData.rowSpan; }}
                >
                    <HeaderCell>ID</HeaderCell>
                    <Cell dataKey="id" />
                </Column>

                <Column 
                    fullText
                    // verticalAlign="middle"
                    rowSpan={rowData => { return rowData.rowSpan; }}
                >
                    <HeaderCell>WBS</HeaderCell>
                    <Cell dataKey="wbs" />
                </Column>

                <Column
                    treeCol
                    fullText
                    // verticalAlign="middle"
                    rowSpan={rowData => { return rowData.rowSpan; }}
                >
                    <HeaderCell>Name</HeaderCell>
                    <Cell dataKey="name" />
                </Column>

                <Column 
                    fullText
                    // verticalAlign="middle"
                    rowSpan={rowData => { return rowData.rowSpan; }}
                >
                    <HeaderCell>Description</HeaderCell>
                    <Cell dataKey="description" />
                </Column>

                <Column fullText>
                    <HeaderCell>Worktime</HeaderCell>
                    <Cell dataKey="worktime" />
                </Column>

                <Column fullText>
                    <HeaderCell>Start</HeaderCell>
                    <Cell dataKey="start" />
                </Column>

                <Column fullText>
                    <HeaderCell>Finish</HeaderCell>
                    <Cell dataKey="finish" />
                </Column>

                <Column fullText>
                    <HeaderCell>Parent</HeaderCell>
                    <Cell dataKey="parent" />
                </Column>

                <Column fullText>
                    <HeaderCell>Predecessors</HeaderCell>
                    <Cell dataKey="predecessors" />
                </Column>

            </Table>
        </div>
    );
}


export default ProjectTable;