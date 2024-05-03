import * as Validate from "./ProjectListInputsHandler"



class TasksListCallbacks {
    constructor(tasksMessages, dashboard) {
        this.tasksMessages = tasksMessages
        this.dashboard = dashboard
    }

    
    addTask = (e) => {
        e.target.textContent = e.target.textContent.trim()
        if (e.target.textContent !== '') 
            this.tasksMessages.addTask(e.target.textContent)
        e.target.textContent = '' //          why is it needed??!! 
    }


    addTaskToBaseline = (taskId, baselineId) => this.tasksMessages.addTaskToBaseline(taskId, baselineId)


    hideSubTree = (index) => this.tasksMessages.hideSubTree(this.dashboard.tasks[index])


    showSubTree = (index) => this.tasksMessages.showSubTree(this.dashboard.tasks[index])


    updateTaskName = (e, taskId) => {
        e.target.textContent = e.target.textContent.trim()
        if (e.target.textContent === String(this.dashboard['tasks'][taskId]['name'])) return
        const r = Validate.taskNameInputValidate(e.target.textContent, this.dashboard['tasks'])

        if (r) this.tasksMessages.updateTaskName(taskId, e.target.textContent)
        e.target.textContent = this.dashboard['tasks'][taskId]['name']
    }


    changeParent = (e, taskId) => {
        e.target.textContent = e.target.textContent.trim()
        if (e.target.textContent === String(this.dashboard.tasks[taskId]['parent'])) return
        const r = Validate.changeParentInputValidate(index, e.target.textContent, this.dashboard.tasks)

        if (r) this.tasksMessages.changeParent(taskId, e.target.textContent)
        e.target.textContent = this.dashboard.tasks[taskId]['parent']
    }

}


export default TasksListCallbacks

//     updateValueFromCell = (e, id, column) => {
//         e.target.textContent = e.target.textContent.trim()
//         if (e.target.textContent === String(this.data[id][column])) return
//         switch (column) {

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



    
