

export const columns = {
    'id': 'ID',
    'wbs': 'WBS',
    'name': 'Name',
    'details': 'Details',
    'description': 'Description',
    'worktime': 'Worktime',
    'parent': 'Parent',
    'predecessors': 'Predecessors',
    'start': 'Start',
    'finish': 'Finish'
};



export const data = [
    {
        'id': 0,
        'name': 'task one',
        'description': 'some desc',

        'wbs': '1',
        'worktime': '80',
        'start': '2023-09-12',
        'finish': '2023-09-26',
        'parent': null,
        'predecessors': '2FS',
        // [
        //     {
        //         'project': { 'id': '2'},
        //         'type': 'FS'
        //     }
        // ],

        'baselines': [
            {
                'wbs': '1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': null,
                'predecessors': '2FS',
                // [
                //     {
                //         'project': { 'id': '2'},
                //         'type': 'FS'
                //     }
                // ]
            },
            {
                'wbs': '1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': null
            }
        ],

        'hidden': false,
        'hasChildren': true,
        'hiddenChildren': false
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
        ],
        
        'hidden': false,
        'hasChildren': false,
        'hiddenChildren': false
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

        'baselines': [
            {
                'wbs': '2',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': null
            }
        ],

        'hidden': false,
        'hasChildren': false,
        'hiddenChildren': false
    },
    {
        'id': 3,
        'name': 'task three',
        'description': 'some desc',

        'wbs': null,
        'worktime': null,
        'start': null,
        'finish': null,
        'parent': null,

        'baselines': [],

        'hidden': false,
        'hasChildren': false,
        'hiddenChildren': false
    },
    {
        'id': 4,
        'name': 'task four',
        'description': 'some desc',
        'baselines': [],

        'wbs': null,
        'worktime': null,
        'start': null,
        'finish': null,
        'parent': null,

        'hidden': false,
        'hasChildren': false,
        'hiddenChildren': false
    }
];
