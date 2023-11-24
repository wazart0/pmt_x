import React, { Component } from "react"
import Dashboard from "./components/Dashboard"
import TasksListMessages from "./components/TasksListMessages"



var messagingDashboard = {
    'websocket': new TasksListMessages("ws://localhost:8000/taskslist")
}

messagingDashboard['websocket'].onclose = () => {
    messagingDashboard['websocket'] = new TasksListMessages("ws://localhost:8000/taskslist")
}



class Console extends Component {
    constructor() {
        super()

        this.lines = []
    }

    log = (line) => {
        let currentTime = new Date().toLocaleString()
        this.lines.push(currentTime + String(line))
        this.setState({})
    }

    render() {
        return (
            <div className="consoleLog">
                <textarea rows='10' readOnly>
                    {/* {this.lines.map((line, index) => {
                        {index} {line}
                    })} */}
                </textarea>
            </div>
        )
    }
}



class App extends Component {
    constructor() {
        super()

        this.modalContent = {'content': null}

        this.console = new Console()



    }


    render() {
        return (
            // <div>{menubar}</div>
            <div className="mainContainer">
                <Dashboard messaging={messagingDashboard} console={this.console} />
            </div>
        )
    }
}
  


export default App
