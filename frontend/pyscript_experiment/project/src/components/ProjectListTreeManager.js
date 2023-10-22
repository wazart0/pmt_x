import { data } from "./ProjectVars";


export function hideSubTree(parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let children_list = [parent_id];
    data[parent_id].hiddenChildren = true;
    for (let item in data) {
        // console.log("for loop");
        // console.log(data[item]);
        if (children_list.includes(data[item].parent)) {
            // console.log("parent found");
            // console.log(data[item]);
            data[item]['hidden'] = true;
            if (data[item].hasChildren) children_list.append(data[item].id);
            // console.log(data[item]);
        }
    }
}


export function showSubTree(parent_id) { // assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    let children_list = [parent_id];
    let children_keep_hidden = [];
    data[parent_id].hiddenChildren = false;
    for (let item in data) {
        // console.log("for loop");
        // console.log(data[item]);
        if (children_list.includes(data[item].parent)) {
            // console.log("parent found");
            // console.log(data[item]);
            if (children_keep_hidden.includes(data[item].parent)) {
                if (data[item].hasChildren) children_keep_hidden.append(data[item].id);
            }
            else {
                data[item]['hidden'] = false;
            }
            if (data[item].hasChildren) children_list.append(data[item].id);
            // console.log(data[item]);
        }
    }
}


export function changeParent(id, parent_id) {
    // check if valid (basic, check if parent_id is a child of id)
    if (id === parent_id || parent_id < 0 || parent_id >= data.length) return false;
    
    // rebuild WBS (check children, add as last)
    // sort array by WBS
    // allocate new IDs
}
