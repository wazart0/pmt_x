

// export var columns = {};

// export var data = [];


export function addProject(data, name) {
    let id = data.length
    data.push({
        'id': id,
        'name': name,
        'description': null,
        'baselines': [],

        'wbs': null,
        'worktime': null,
        'start': null,
        'finish': null,
        'parent': null,

        'hidden': false,
        'hasChildren': false,
        'hiddenChildren': false
    })
    return id
}

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
