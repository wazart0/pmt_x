

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

export function setColumns(columns_dict) {
    columns = structuredClone(columns_dict);
}

export function setData(data_array) {
    data = structuredClone(data_array);
}

export function initColumnsAndData(columns_dict, data_array) {
    setColumns(columns_dict);
    setData(data_array);
}
