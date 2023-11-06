import { resetIDs } from "./ProjectVars";
import { isString } from "./utils.js"





export function hideSubTree(data, id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [id];
    data[id].hiddenChildren = true;
    for (let index in data) {
        if (subtree_IDs.includes(data[index].parent)) {
            data[index]['hidden'] = true;
            if (data[index].hasChildren) subtree_IDs.push(data[index].id);
        }
    }
}


export function showSubTree(data, id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [id]
    let children_keep_hidden = []
    data[id].hiddenChildren = false
    for (let index in data) {
        if (subtree_IDs.includes(data[index].parent)) {
            if (data[index].hasChildren) subtree_IDs.push(data[index].id)
            if ((children_keep_hidden.includes(data[index].parent) || data[index]['hiddenChildren'] === true) && data[index].hasChildren) {
                children_keep_hidden.push(data[index].id)
            }
            if (!children_keep_hidden.includes(data[index].parent)) data[index]['hidden'] = false
        }
    }
}


export function sortByWBS(data) {
    function compare(a, b) {
        if (a.wbs === b.wbs) return 0
        if (a.wbs === null) return 1
        if (b.wbs === null) return -1
        const a_array = a.wbs.split('.')
        const b_array = b.wbs.split('.')
        for (let i in (a_array.length < b_array.length) ? a_array : b_array) {
            if (Number(a_array[i]) < Number(b_array[i])) return -1
            if (Number(a_array[i]) > Number(b_array[i])) return 1
        }
        return 0
    }
    data.sort(compare)
}


function changeParent(data, id, parent_id) { // assumption is the data is sorted already by WBS

    // check if valid (basic, check if parent_id is a child of id)
    if (data[id].parent === parent_id) return false
    if (id === parent_id || parent_id < 0 || parent_id >= data.length) return false
    if (data[id].wbs !== null && !isString(data[id].wbs)) return false    
    if (parent_id !== null) if (!Number.isInteger(parent_id) || data[parent_id].wbs === null) return false

    // build helper subtrees
    let parent_old_id = data[id].parent
    let project_subtree = [id]
    let parent_new_subtree = parent_id === null ? [] : [parent_id]
    let parent_old_subtree = parent_old_id === null ? [] : [parent_old_id]
    let no_of_new_siblings = 1 // determine number of child for new parent
    for (let index in data) {
        if (project_subtree.includes(data[index].parent)) project_subtree.push(data[index].id)
        if ((parent_new_subtree.includes(data[index].parent) || parent_id === null) && data[index].wbs !== null) parent_new_subtree.push(data[index].id)
        if (data[index].id !== id && ((parent_old_subtree.includes(data[index].parent) && !project_subtree.includes(data[index].parent)) || (parent_old_id === null && data[index].wbs !== null))) parent_old_subtree.push(data[index].id)
        if (data[index].parent === parent_id && data[index].wbs !== null) no_of_new_siblings = no_of_new_siblings + 1
    }

    console.log(["Move: ", id, " amount: ", project_subtree.length, " under: ", parent_id])
    console.log(["Slice data:", parent_id + parent_new_subtree.length, id, project_subtree.length])

    if (id < parent_id && parent_id < id + project_subtree.length) return false;


    console.log(structuredClone(data))


    data[id].parent = parent_id

    if (parent_id !== null) data[parent_id].hasChildren = true
    if (parent_old_id !== null) data[parent_old_id].hasChildren = parent_old_subtree.length > 1

    // update hiding
    if (parent_id !== null) {
        let index = id
        while (true) {
            index = data[index].parent
            if (data[index].hidden || data[index].hiddenChildren) {
                data[id].hidden = true
                break
            }
            if (data[index].parent === null) break
        }
    }


    // reposition the node and its children
    let new2old_map
    if (parent_id + parent_new_subtree.length !== id) { // restructure if position needs to be changed
        if (parent_id + parent_new_subtree.length < id) {
            data.splice(parent_id + parent_new_subtree.length, 0, ...data.splice(id, project_subtree.length))
        } else {
            data.splice(parent_id + parent_new_subtree.length - project_subtree.length, 0, ...data.splice(id, project_subtree.length))
        }

        // Reset IDs
        new2old_map = resetIDs(data)
    }

    // remap project subtree
    if (typeof new2old_map !== 'undefined') {
        project_subtree.forEach((project_id, index) => project_subtree[index] = new2old_map.indexOf(project_id))
        id = new2old_map.indexOf(id)
        if (parent_id !== null) parent_id = new2old_map.indexOf(parent_id)
        if (parent_old_id !== null) parent_old_id = new2old_map.indexOf(parent_old_id)
    }

    
    console.log(structuredClone(data))


    // Rebuild WBS: 1st update current project, 2nd update old parent 
    let wbs_new = (parent_id === null ? String(no_of_new_siblings) : data[parent_id].wbs + '.' + no_of_new_siblings)
    if (data[id].wbs) {
        project_subtree.forEach((project_id) => {
            if (project_id !== id) data[project_id].wbs = wbs_new + data[project_id].wbs.slice(data[id].wbs.length)
        })
    }
    data[id].wbs = wbs_new


    if (parent_old_id !== null) {
        if (data[parent_old_id].hasChildren) {
            let parent_old_subtree_new = parent_old_id === null ? [] : [parent_old_id]
            data.forEach((element) => {
                if (parent_old_subtree_new.includes(element.parent)) parent_old_subtree_new.push(element.id)
            })
            let number_parent = 0
            let wbs_parent_length
            parent_old_subtree_new.forEach((project_id) => {
                if (data[project_id].wbs === null || project_id === parent_old_id) return
                if (data[project_id].parent === parent_old_id) {
                    wbs_parent_length = data[project_id].wbs.length
                    number_parent = number_parent + 1
                    data[project_id].wbs = data[parent_old_id].wbs + '.' + String(number_parent)
                } else {
                    data[project_id].wbs = data[parent_old_id].wbs + '.' + String(number_parent) + data[project_id].wbs.slice(wbs_parent_length)
                }
            })
        }
    } else { // update all tasks
        let number_parent = 0
        let wbs_parent_length
        data.forEach((element, index) => {
            if (element.wbs === null) return
            if (element.parent === null) {
                wbs_parent_length = element.wbs.length
                number_parent = number_parent + 1
                data[index].wbs = String(number_parent)
            } else {
                data[index].wbs = String(number_parent) + element.wbs.slice(wbs_parent_length)
            }
        })
    }

    return true
}



export function arePredecesorsLooped(data, id, predecessors) {
    return false;
}