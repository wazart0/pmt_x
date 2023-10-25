import { data, sortByWBS, resetIDs } from "./ProjectVars";
import { isString } from "./utils.js"





export function hideSubTree(id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [id];
    data[id].hiddenChildren = true;
    for (let index in data) {
        if (subtree_IDs.includes(data[index].parent)) {
            data[index]['hidden'] = true;
            if (data[index].hasChildren) subtree_IDs.push(data[index].id);
        }
    }
}


export function showSubTree(id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
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


export function changeParent(id, parent_id) { // returns true if data has been changed, false if no modifications were made

    // check if valid (basic, check if parent_id is a child of id)
    if (data[id].parent === parent_id) return false
    if (id === parent_id || parent_id < 0 || parent_id >= data.length) return false
    if (data[id].wbs !== null && !isString(data[id].wbs)) return false

    if (parent_id !== null) {
        if (!Number.isInteger(parent_id) || data[parent_id].wbs === null) return false

        let check_subtree = [id]
        for (let index in data) {
            if (check_subtree.includes(data[index].parent)) check_subtree.push(data[index].id)
        }
        if (check_subtree.includes(parent_id)) return false;

        // console.log(["check_subtree:", check_subtree])
    } 


    // determine number of child for new parent
    let no_of_new_siblings = 1
    for (let index in data) {
        if (data[index].parent === parent_id && data[index].wbs !== null) {
            no_of_new_siblings = no_of_new_siblings + 1
        }
    }


    // rebuild wbs of old parent and without child (eg. if project was first child) - needed to keep the order
    let parent_id_old = data[id].parent
    
    if (parent_id_old !== null) {
        let subtree_parent_old_IDs = [parent_id_old]
        for (let index in data) {
            if (data[index].id !== id && subtree_parent_old_IDs.includes(data[index].parent)) subtree_parent_old_IDs.push(data[index].id)
        }

        data[parent_id_old]["hasChildren"] = subtree_parent_old_IDs.length > 1 ? true : false

        // console.log("subtree_parent_IDs:")
        // console.log(subtree_parent_old_IDs)
        data[id].parent = parent_id
        
        if (data[parent_id_old]["hasChildren"]) {

            let wbs_parent_old = data[parent_id_old].wbs
            let new_number = 0
            let wbs_length
            for (let index in subtree_parent_old_IDs) {
                if (data[subtree_parent_old_IDs[index]].parent === parent_id_old) {
                    wbs_length = data[subtree_parent_old_IDs[index]].wbs.length
                    new_number = new_number + 1
                }
                if (subtree_parent_old_IDs[index] !== parent_id_old) data[subtree_parent_old_IDs[index]].wbs = wbs_parent_old + '.' + new_number + data[subtree_parent_old_IDs[index]].wbs.slice(wbs_length)
            }
        }
    } else {
        data[id].parent = parent_id
        let new_number = 0
        let wbs_length
        for (let index in data) {
            if (data[index].wbs !== null) {
                if (data[index].parent === parent_id_old) {
                    wbs_length = data[index].wbs.length
                    new_number = new_number + 1
                }
                data[index].wbs = new_number + data[index].wbs.slice(wbs_length)
            }
        }
    }


    // rebuild WBS of project and its children
    let wbs_new = parent_id === null ? String(no_of_new_siblings) : data[parent_id].wbs + '.' + no_of_new_siblings

    if (data[id].hasChildren) {
        let wbs_current_length = data[id].wbs.length

        let subtree_old_IDs = [id]
        for (let index in data) {
            if (subtree_old_IDs.includes(data[index].parent)) subtree_old_IDs.push(data[index].id)
        }
        // console.log("subtree_old_IDs:")
        // console.log(subtree_old_IDs)

        for (let index in subtree_old_IDs) {
            if (subtree_old_IDs[index] !== id) data[subtree_old_IDs[index]].wbs = wbs_new + data[subtree_old_IDs[index]].wbs.slice(wbs_current_length)
        }
    }

    
    // update relevant data
    data[id].wbs = wbs_new
    if (parent_id !== null) data[parent_id]["hasChildren"] = true

    if (parent_id_old !== null) {
        data[parent_id_old]["hasChildren"] = false
        for (let index in data) {
            if (data[index].parent === parent_id_old) {
                data[parent_id_old]["hasChildren"] = true
                break;
            }
        }
    }


    // sort data array by WBS
    sortByWBS()


    // allocate new IDs (reset index)
    resetIDs()


    // hide project if parent or its children are hidden
    let index = id
    while (data[index].parent !== null) {
        data[id].hidden = data[index].hidden || data[index].hiddenChildren
        index = data[index].parent
    }

    return true
}
