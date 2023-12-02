


class TasksListMessages extends WebSocket {

    addTask = (name) => {
        this.send(JSON.stringify({
            'name': 'upsert_task',
            'args': {
                'name': name
            }
        }))
    }


    addTaskToBaseline = (taskId) => {
        this.send(JSON.stringify({
            'name': 'add_task_to_baseline',
            'args': {
                'task_id': taskId
            }
        }))
    }


    // hideSubTree = (taskId) => {
    //     this.send(JSON.stringify({
    //         'name': 'hide_subtree',
    //         'args': {
    //             'task_id': taskId
    //         }
    //     }))
    // }


    // showSubTree = (taskId) => {
    //     this.send(JSON.stringify({
    //         'name': 'show_subtree',
    //         'args': {
    //             'task_id': taskId
    //         }
    //     }))
    // }


    updateTaskName = (taskId, name) => {
        this.send(JSON.stringify({
            'name': 'upsert_task',
            'args': {
                'id': taskId,
                'name': name
            }
        }))
    }


    changeParent = (taskId, parent) => {
        this.send(JSON.stringify({
            'name': 'change_parent',
            'args': {
                'task_id': taskId,
                'parent': parent
            }
        }))
    }


    getViews = (userId) => {
        this.send(JSON.stringify({
            'name': 'get_views',
            'args': {
                'user_id': userId
            }
        }))
    }


    getDashboard = (userId, viewId) => {
        this.send(JSON.stringify({
            'name': 'get_dashboard',
            'args': {
                'user_id': userId,
                'view_id': viewId
            }
        }))
    }

}



export default TasksListMessages



//     updateValueFromCell = (e, id, column) => {
//         e.target.textContent = e.target.textContent.trim()
//         if (e.target.textContent === String(this.data[id][column])) return
//         switch (column) {
//             case 'name':
//                 if (!e.target.textContent) {
//                     e.target.textContent = this.data[id][column]
//                     return
//                 }
//                 this.data[id][column] = e.target.textContent
//                 break

//             case 'parent':
//                 let result = changeParent(this.data, id, e.target.textContent !== '' ? Number(e.target.textContent) : null)
//                 e.target.textContent = this.data[id][column]
//                 if (!result) return
//                 break

//             case 'predecessors':
//                 if (!/^(([0-9]+([fFsS]{2})?(\s*\+\s*[0-9]+[hHwWmMdDsS]?)?)(\s*,\s*)?)+$/.test(e.target.textContent) & e.target.textContent !== '') {
//                     e.target.textContent = this.data[id][column]
//                     return
//                 }
//                 let predecessors = e.target.textContent.split(/\s*,\s*/g)
//                 let predecessorsIDs = []
//                 for (let index in predecessors)  {
//                     let predecessorID = predecessors[index].match(/^[0-9]+/g)
//                     if (predecessorID.length !== 1) {
//                         console.log("predecessor length: " + String(predecessorID.length))
//                         e.target.textContent = this.data[id][column]
//                         return
//                     }
//                     predecessorsIDs.push(parseInt(predecessorID[0], 10))
//                 }
//                 if (new Set(predecessorsIDs).size !== predecessorsIDs.length) {
//                     e.target.textContent = this.data[id][column]
//                     return
//                 }
//                 // check if parent or child
//                 // verify (no loops in a graph)
//                 if (arePredecesorsLooped(this.data, id, predecessorsIDs)) {
//                     e.target.textContent = this.data[id][column]
//                     return
//                 }

//                 this.data[id][column] = e.target.textContent
//                 break

//             case 'worktime':
//                 if (!/^[0-9]+[hHwWmMdDsS]?$/.test(e.target.textContent) & e.target.textContent !== '') {
//                     e.target.textContent = this.data[id][column]
//                     return
//                 }
//                 this.data[id][column] = e.target.textContent
//                 break

//             default:
//                 this.data[id][column] = e.target.textContent
//         }
//         console.log("Updated task: [" + String(id) + "] column: [" + column + "] to: [" + this.data[id][column]+ "] ")
//         console.log("TODO: Implement data update in DB.")
//         this.setState({})
//     }

//     addNewProject = (e) => {
//         if (!e.target.textContent.trim()) return
//         let id = addProject(this.data, e.target.textContent.trim())
//         e.target.textContent = ''                                     //                                      TODO:         why is it needed!?
        
//         console.log("TODO: Implement data update in DB.")
//         console.log("Created task: [" + String(id) + "] to: [" + this.data[id].name+ "] ")
//         this.setState({})
//     }

//     addToBaseline = (id) => {
//         let no_of_new_siblings = 1
//         for (let index in this.data) {
//             if (this.data[index].parent === null && this.data[index].wbs) {
//                 no_of_new_siblings = no_of_new_siblings + 1
//             }
//         }
//         this.data[id].wbs = String(no_of_new_siblings)
//         sortByWBS(this.data)
//         resetIDs(this.data)
//         console.log("TODO: Implement data update in DB.")
//         this.setState({})
//     }
    

//     render() {
//         return (
//             <div className="projectList">
//                 <ProjectListComponent 
//                     data={this.data}
//                     columns={this.columns}
//                     showProjectDetails={this.showProjectDetails}
//                     hideChildren={this.hideChildren}
//                     showChildren={this.showChildren}
//                     updateValueFromCell={this.updateValueFromCell}
//                     addNewProject={this.addNewProject}
//                     addToBaseline={this.addToBaseline}
//                 />
//             </div>
//         )
//     }
// }