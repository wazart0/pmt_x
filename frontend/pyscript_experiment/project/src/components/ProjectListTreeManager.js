import { data } from "./ProjectVars";


export function hideSubTree(parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [parent_id];
    data[parent_id].hiddenChildren = true;
    for (let index in data) {
        // console.log("for loop");
        // console.log(data[index]);
        if (subtree_IDs.includes(data[index].parent)) {
            // console.log("parent found");
            // console.log(data[index]);
            data[index]['hidden'] = true;
            if (data[index].hasChildren) subtree_IDs.push(data[index].id);
            // console.log(data[index]);
        }
    }
}


export function showSubTree(parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let subtree_IDs = [parent_id];
    let children_keep_hidden = [];
    data[parent_id].hiddenChildren = false;
    for (let index in data) {
        // console.log("for loop");
        // console.log(data[index]);
        if (subtree_IDs.includes(data[index].parent)) {
            // console.log("parent found");
            // console.log(data[index]);
            if (children_keep_hidden.includes(data[index].parent)) {
                if (data[index].hasChildren) children_keep_hidden.push(data[index].id);
            }
            else {
                data[index]['hidden'] = false;
            }
            if (data[index].hasChildren) subtree_IDs.push(data[index].id);
            // console.log(data[index]);
        }
    }
}


export function changeParent(id, parent_id) {
    // check if valid (basic, check if parent_id is a child of id)
    console.log(id)
    console.log(parent_id)
    if (id === parent_id || data.parent === parent_id || parent_id < 0 || parent_id >= data.length || !Number.isInteger(parent_id)) return false;
    let subtree_IDs = [id];
    for (let index in data) {
        if (subtree_IDs.includes(data[index].parent)) subtree_IDs.push(data[index].id);
    }
    if (subtree_IDs.includes(parent_id)) return false;

    console.log(subtree_IDs)

    // rebuild WBS (check subtree_IDs, add as last)
    let no_of_direct_children = 1; 
    for (let index in data) {
        if (data[index].parent === parent_id) {
            no_of_direct_children = no_of_direct_children + 1;
        }
    }

    console.log(data[parent_id].wbs)
    let wbs_new = data[parent_id].wbs + '.' + no_of_direct_children;
    console.log(wbs_new)
    if (data[id].hasChildren) {
        console.log('has children')
        let wbs_current_length = data[id].wbs.length;
        for (let index in subtree_IDs) {
            if (subtree_IDs[index] !== id) data[subtree_IDs[index]].wbs = wbs_new + data[subtree_IDs[index]].wbs.slice(wbs_current_length);
        }
    }

    let parent_old = data[id].parent;
    data[id].parent = parent_id;
    if (parent_old !== null) {
        console.log('parent old: ' + String(parent_old))
        data[parent_old]["hasChildren"] = false;
        for (let index in data) {
            if (data[index].parent === parent_old) {
                data[parent_old]["hasChildren"] = true;
                break;
            }
        }
    }
    data[parent_id]["hasChildren"] = true;

    data[id].wbs = wbs_new;


    // fix numbering of old parent children (eg. if project was first child) - needed to keep the order
    if (parent_old !== null) {
        let subtree_parent_IDs = [parent_old];
        for (let index in data) {
            if (subtree_parent_IDs.includes(data[index].parent)) subtree_parent_IDs.push(data[index].id);
        }
        // let wbs_parent_old = data[parent_old].wbs;
        // let wbs_to_change = null;
        // let new_number = 0;
        // let rgxp;
        // for (let index in data) {
        //     if (data[index].parent === parent_old) {
        //         wbs_to_change = data[index].wbs;
        //         let regexstring = wbs_to_change.replace(/\./g, '\\.');
        //         console.log(regexstring);
        //         rgxp = new RegExp(regexstring, "g");
        //         new_number = new_number + 1; 
        //     }
        //     if (wbs_to_change && data[index].wbs.match(rgxp)) {
        //         data[index].wbs = wbs_parent_old + '.' + new_number + data[index].wbs.slice(wbs_to_change.length);
        //     }
        // }
    }


    // sort array by WBS
    function compare(a, b) {
        if (a.wbs === null || b.wbs === null) {
            return -1;
        }
        if (a.wbs < b.wbs){
            return -1;
        }
        if (a.wbs > b.wbs){
            return 1;
        }
        return 0;
    }
    data.sort(compare);

    // allocate new IDs (reset index)
    let map = {};
    for (let index in data) {
        map[data[index].id] = index;
    }
    for (let index in data) {
        data[index].id = index;
        data[index].parent = data[index].parent !== null ? map[data[index].parent] : null;
    }

    return true;
}
