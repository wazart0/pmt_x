


export function validateParentAgainstWBS() {
    return true
}

export function resetWBS() {

}

export function resetIDs(data) {
    let new2old_map = []
    for (let index in data) {
        new2old_map.push(data[index].id)
    }
    for (let index in data) {
        data[index].id = Number(index)
        data[index].parent = data[index].parent !== null ? new2old_map.indexOf(data[index].parent) : null
    }
    return new2old_map
}

export function overwriteNullWBS() {

}

// export function setColumns(columns_dict) {
//     columns = structuredClone(columns_dict)
// }

// export function setData(data_array) {
//     data = structuredClone(data_array)
//     sortByWBS()
//     if (!validateParentAgainstWBS()) {
//         console.log("WARNING: WBS invalid, resetting WBS.")
//         resetWBS()
//     }
// }

// export function initColumnsAndData(columns_dict, data_array) {
//     setColumns(columns_dict)
//     setData(data_array)
// }
