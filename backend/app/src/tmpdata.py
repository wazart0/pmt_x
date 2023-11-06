

demo_data = [
            {
                'id': 0,
                'name': 'task one',
                'description': 'some desc',

                'wbs': '1',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': None,
                'predecessors': '2FS',
                # // [
                # //     {
                # //         'project': { 'id': '2'},
                # //         'type': 'FS'
                # //     }
                # // ],

                'baselines': [
                    {
                        'wbs': '1',
                        'worktime': '80',
                        'start': '2023-09-12',
                        'finish': '2023-09-26',
                        'parent': None,
                        'predecessors': '2FS',
                        # // [
                        # //     {
                        # //         'project': { 'id': '2'},
                        # //         'type': 'FS'
                        # //     }
                        # // ]
                    },
                    {
                        'wbs': '1',
                        'worktime': '80',
                        'start': '2023-09-12',
                        'finish': '2023-09-26',
                        'parent': None
                    }
                ],

                'hidden': False,
                'hasChildren': True,
                'hiddenChildren': False
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
                
                'hidden': False,
                'hasChildren': False,
                'hiddenChildren': False
            },
            {
                'id': 2,
                'name': 'task two',
                'description': 'some desc',
                
                'wbs': '2',
                'worktime': '80',
                'start': '2023-09-12',
                'finish': '2023-09-26',
                'parent': None,

                'baselines': [
                    {
                        'wbs': '2',
                        'worktime': '80',
                        'start': '2023-09-12',
                        'finish': '2023-09-26',
                        'parent': None
                    }
                ],

                'hidden': False,
                'hasChildren': False,
                'hiddenChildren': False
            },
            {
                'id': 3,
                'name': 'task three',
                'description': 'some desc',

                'wbs': None,
                'worktime': None,
                'start': None,
                'finish': None,
                'parent': None,

                'baselines': [],

                'hidden': False,
                'hasChildren': False,
                'hiddenChildren': False
            },
            {
                'id': 4,
                'name': 'task four',
                'description': 'some desc',
                'baselines': [],

                'wbs': None,
                'worktime': None,
                'start': None,
                'finish': None,
                'parent': None,

                'hidden': False,
                'hasChildren': False,
                'hiddenChildren': False
            }
        ]