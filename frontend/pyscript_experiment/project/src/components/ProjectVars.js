

export var columns = {};

export var data = [];


export function emptyRow() {
    return {
        'id': data.length,
        'name': null,
        'description': null,
        'baselines': [],

        'wbs': null,
        'worktime': null,
        'start': null,
        'finish': null,
        'parent': null,

        'hidden': false
    };
}

export function setColumns(columns_dict) {
    columns = structuredClone(columns_dict);
}

export function setData(data_array) {
    data = structuredClone(data_array);
    data.push(emptyRow());
}

export function initColumnsAndData(columns_dict, data_array) {
    setColumns(columns_dict);
    setData(data_array);
}
