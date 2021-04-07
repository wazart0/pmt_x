import json




class RDF():

    def __init__(self):
        self.rdf_string = ''
        self.root_id = ''
        self.baseline_id = ''
        self.root_id_planned = '_plan'
        self.baseline_id_planned = '_plan'


    def __str__(self):
        return self.rdf_string


    def add_root(self, name, **kwargs):
        self.rdf_string = RDF.generate_baseline(self.baseline_id, 'default', self.root_id)
        rdf, kwargs = RDF.generate_project_baseline(self.root_id, self.root_id, self.baseline_id)
        self.rdf_string = self.rdf_string + RDF.generate_project(self.root_id, name, **kwargs)
        self.rdf_string = self.rdf_string + rdf


    def add_project(self, id, name, **kwargs):
        if 'parent_id' in kwargs:
            rdf, kwargs = RDF.generate_project_baseline(id, id, self.baseline_id, **kwargs)
        else:
            rdf, kwargs = RDF.generate_project_baseline(id, id, self.baseline_id, parent_id=self.root_id, **kwargs)
        self.rdf_string = self.rdf_string + RDF.generate_project(id, name, **kwargs)
        self.rdf_string = self.rdf_string + rdf


    def add_baseline_planned(self, name):
        self.rdf_string = self.rdf_string + RDF.generate_baseline(self.baseline_id_planned, name, self.root_id)
        rdf, _ = RDF.generate_project_baseline(self.root_id, self.root_id_planned, self.baseline_id_planned)
        self.rdf_string = self.rdf_string + rdf


    def add_project_baseline_planned(self, id, **kwargs):
        if 'parent_id' in kwargs:
            kwargs['parent_id'] = kwargs['parent_id'] + self.root_id_planned
            rdf, _ = RDF.generate_project_baseline(id, id + self.root_id_planned, self.baseline_id_planned, **kwargs)
        else:
            rdf, _ = RDF.generate_project_baseline(id, id + self.root_id_planned, self.baseline_id_planned, parent_id=self.root_id_planned, **kwargs)
        self.rdf_string = self.rdf_string + rdf
        


    @staticmethod
    def generate_project(project_id, name, **kwargs):
        project_triple = '''
            _:p{0} <dgraph.type> "Project" .
            _:p{0} <Project.name> "{1}" .
        '''.format(project_id, name)

        if 'description' in kwargs:
            project_triple = project_triple + '''_:p{0} <Project.description> "{1}" .\n'''.format(project_id, kwargs['description'])
            del kwargs['description']
        
        if 'externalTool' in kwargs:
            project_triple = project_triple + '''_:p{0} <Project.externalTool> "{1}" .\n'''.format(project_id, kwargs['externalTool'])
            del kwargs['externalTool']

        if kwargs:
            project_triple = project_triple + '''_:p{0} <Project.customFields> "{1}" .\n'''.format(project_id, json.dumps(kwargs).replace('"', '\\\"'))
            
        return project_triple


    @staticmethod
    def generate_baseline(baseline_id, name, project_id):
        return '''
            _:bl{0} <dgraph.type> "Baseline" .
            _:bl{0} <Baseline.name> "{1}" .
            _:bl{0} <Baseline.root> _:p{2} .
            _:p <Project.baselines> _:bl{0} .
        '''.format(baseline_id, name, project_id)


    @staticmethod
    def generate_project_baseline(project_id, project_baseline_id, baseline_id, **kwargs):
        project_baseline_triple = '''
            _:pb{0} <dgraph.type> "ProjectBaseline" .
            _:pb{0} <ProjectBaseline.baseline> _:bl{1} .
            _:pb{0} <ProjectBaseline.project> _:p{2} .
            _:bl{1} <Baseline.projects> _:pb{0} .
        '''.format(project_baseline_id, baseline_id, project_id)

        if 'parent_id' in kwargs:
            project_baseline_triple = project_baseline_triple + '''_:pb{0} <ProjectBaseline.parent> _:pb{1} .
    _:pb{1} <ProjectBaseline.children> _:pb{0} .\n'''.format(project_baseline_id, kwargs['parent_id'])
            del kwargs['parent_id']

        if 'wbs' in kwargs:
            project_baseline_triple = project_baseline_triple + '''_:pb{0} <ProjectBaseline.wbs> "{1}" .\n'''.format(project_baseline_id, kwargs['wbs'])
            del kwargs['wbs']

        if 'worktime' in kwargs:
            project_baseline_triple = project_baseline_triple + '''_:pb{0} <ProjectBaseline.worktime> "{1}" .\n'''.format(project_baseline_id, kwargs['worktime'])
            del kwargs['worktime']

        if 'start' in kwargs:
            project_baseline_triple = project_baseline_triple + '''_:pb{0} <ProjectBaseline.start> "{1}"^^<xs:dateTime> .\n'''.format(project_baseline_id, kwargs['start'])
            del kwargs['start']

        if 'finish' in kwargs:
            project_baseline_triple = project_baseline_triple + '''_:pb{0} <ProjectBaseline.finish> "{1}"^^<xs:dateTime> .\n'''.format(project_baseline_id, kwargs['finish'])
            del kwargs['finish']
            
        # add predecessors 

        return (project_baseline_triple, kwargs)




def generate_triples(root_name, root_description, task_list):
    rdf = RDF.generate_project('', root_name, description=root_description) + \
        RDF.generate_project_baseline('', '', '')[0] + \
        RDF.generate_baseline('', 'default', '')
    for task in task_list['data']:
        rdf = rdf + \
            RDF.generate_project(
                task[task_list['columns'].index('id')],
                task[task_list['columns'].index('name')],
                description = task[task_list['columns'].index('description')],
                some_custom_column = task[task_list['columns'].index('some_custom_column')]
            ) + \
            RDF.generate_project_baseline(
                task[task_list['columns'].index('id')],
                task[task_list['columns'].index('id')],
                '',
                parent_id=task[task_list['columns'].index('parent_id')],
                worktime=task[task_list['columns'].index('timespent')],
                start=task[task_list['columns'].index('start')],
                finish=task[task_list['columns'].index('finish')],
            )[0]
    return rdf

    
def generate_triples_with_class(root_name, root_description, task_list):
    rdf = RDF()
    rdf.add_root(root_name, description=root_description)
    for task in task_list['data']:
        rdf.add_project(
            task[task_list['columns'].index('id')],
            task[task_list['columns'].index('name')],
            description = task[task_list['columns'].index('description')],
            parent_id = task[task_list['columns'].index('parent_id')],
            worktime = task[task_list['columns'].index('timespent')],
            start = task[task_list['columns'].index('start')],
            finish = task[task_list['columns'].index('finish')],
            some_custom_column = task[task_list['columns'].index('some_custom_column')],
            another_custom_field = 'troll'
        )

    return str(rdf)




### EXAMPLE ###

if __name__ == "__main__":


    url = 'localhost:9080'

    task_list = {
        "columns": ['id', 'name', 'description', 'parent_id', 'some_custom_column', 'timespent', 'start', 'finish'],
        "data": [
            ['1', 'task1', '1-st level', '', 'x', '5h', '2021-03-01', '2021-03-05'],
            ['1.1', 'subtask1', '2-st level', '1', 'y', '1h', '2021-03-01', '2021-03-02'],
            ['1.2', 'subtask2', '2-st level', '1', 'z', '9h', '2021-03-02', '2021-03-05'],
            ['2', 'task2', '1-st level', '', 'git', '15h', '2021-03-02', '2021-03-10']
        ]
    }


    # triples = generate_triples('some_test_project', 'description of root task', task_list)
    triples = generate_triples_with_class('some_test_project', 'description of root task', task_list)
    print(triples)

    # import pydgraph
    # client_stub = pydgraph.DgraphClientStub(url)
    # client = pydgraph.DgraphClient(client_stub)

    # txn = client.txn()

    # try:
    #     txn.mutate(set_nquads=triples)
    #     txn.commit()
    # except pydgraph.AbortedError:
    #     # Retry or handle exception.
    #     txn.discard()
    #     print(pydgraph.AbortedError)
    # finally:
    #     txn.discard()
    #     print('Data sent.')
