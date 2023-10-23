import { data, sortByWBS, resetIDs } from "./ProjectVars";


function isString(s) {
    return typeof(s) === 'string' || s instanceof String;
}



export function hideSubTree(parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [parent_id];
    data[parent_id].hiddenChildren = true;
    for (let index in data) {
        if (subtree_IDs.includes(data[index].parent)) {
            data[index]['hidden'] = true;
            if (data[index].hasChildren) subtree_IDs.push(data[index].id);
        }
    }
}


export function showSubTree(parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [parent_id]
    let children_keep_hidden = []
    data[parent_id].hiddenChildren = false
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


export function changeParent(id, parent_id) {

    // check if valid (basic, check if parent_id is a child of id)
    if (data[id].parent === parent_id) return false
    if (id === parent_id || parent_id < 0 || parent_id >= data.length) return false
    if (data[id].wbs !== null && !isString(data[id].wbs)) { console.log("ERROR: WBS is not a string!"); return false; }

    let parent_id_old = data[id].parent

    if (parent_id !== null) {
        if (!Number.isInteger(parent_id) || data[parent_id].wbs === null) return false

        let check_subtree = [id]
        for (let index in data) {
            if (check_subtree.includes(data[index].parent)) check_subtree.push(data[index].id)
        }
        if (check_subtree.includes(parent_id)) return false;

        // console.log(["check_subtree:", check_subtree])


        // init changes
        data[id].parent = null

        // console.log(['parent old: ', parent_id_old])


        // rebuild wbs of old parent and without child (eg. if project was first child) - needed to keep the order
        if (parent_id_old !== null) {
            let subtree_parent_old_IDs = [parent_id_old]
            for (let index in data) {
                if (data[index].id !== id && subtree_parent_old_IDs.includes(data[index].parent)) subtree_parent_old_IDs.push(data[index].id)
            }

            data[parent_id_old]["hasChildren"] = subtree_parent_old_IDs.length > 1 ? true : false
    
            // console.log("subtree_parent_IDs:")
            // console.log(subtree_parent_old_IDs)
            
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
        }
    }


    
    // rebuild WBS for ID
    let no_of_new_siblings = 1
    for (let index in data) {
        if (data[index].parent === parent_id && data[index].wbs) {
            no_of_new_siblings = no_of_new_siblings + 1
        }
    }

    let wbs_new = parent_id === null ? String(no_of_new_siblings) : data[parent_id].wbs + '.' + no_of_new_siblings
    // console.log(["new wbs: ", wbs_new])


    // rebuild WBS of children
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
    data[id].parent = parent_id
    if (parent_id !== null) data[parent_id]["hasChildren"] = true

    data[parent_id_old]["hasChildren"] = false
    for (let index in data) {
        if (data[index].parent === parent_id_old) {
            data[parent_id_old]["hasChildren"] = true
            break;
        }
    }

    // sort data array by WBS
    sortByWBS()

    // allocate new IDs (reset index)
    resetIDs()

    // show parent subtree with added child
    // showSubTree(parent_id) - rethink better logic (all parents  of this parent have to be expanded too)

    // console.log(structuredClone(data))
    return true
}
