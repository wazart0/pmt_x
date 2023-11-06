import * as Validate from "./ProjectListInputs"



class TasksListCallbacks {
    constructor(tasksMessages) {
        this.tasksMessages = tasksMessages
    }

    
    addTask = (e) => {
        if (!Validate.addTaskInputValidate(e.target.textContent)) return
        this.tasksMessages.addTask(Validate.addTaskInputTransform(e.target.textContent))
        e.target.textContent = '' //          why is it needed??!! 
    }


    addTaskToBaseline = (taskId) => {
        this.tasksMessages.addTaskToBaseline(taskId)
    }

}

export default TasksListCallbacks

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



    
