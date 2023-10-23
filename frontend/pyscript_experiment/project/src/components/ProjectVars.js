

export var columns = {};

export var data = [];


export function addProject(name) {
    let id = data.length;
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

        'hidden': false
    });
    return id;
}

export function validateParentAgainstWBS() {
    return true;
}

export function resetWBS() {

}

export function resetIDs() {
    let map = {};
    for (let index in data) {
        map[data[index].id] = Number(index);
    }
    for (let index in data) {
        data[index].id = Number(index);
        data[index].parent = data[index].parent !== null ? map[data[index].parent] : null;
    }
}

export function overwriteNullWBS() {

}

export function sortByWBS() {
    function compare(a, b) {
        if (a.wbs === b.wbs) return 0
        if (a.wbs === null) return 1
        if (b.wbs === null) return -1
        if (a.wbs < b.wbs) return -1
        if (a.wbs > b.wbs) return 1
    }
    data.sort(compare);
}

export function setColumns(columns_dict) {
    columns = structuredClone(columns_dict)
}

export function setData(data_array) {
    data = structuredClone(data_array)
    sortByWBS()
    if (!validateParentAgainstWBS()) {
        console.log("WARNING: WBS invalid, resetting WBS.")
        resetWBS()
    }
}

export function initColumnsAndData(columns_dict, data_array) {
    setColumns(columns_dict)
    setData(data_array)
}
