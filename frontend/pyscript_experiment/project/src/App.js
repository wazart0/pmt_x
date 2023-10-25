import React, { Component } from "react"
import ProjectList from "./components/ProjectList"
import Modal from "./components/Modal"
import { data as globalData, columns as globalColumns, initColumnsAndData } from "./components/ProjectVars"
import * as demo from "./components/tmpData"


class App extends Component {
    constructor() {
        super()
        this.state = {
            show: false
        }
        this.showModal = this.showModal.bind(this)
        this.hideModal = this.hideModal.bind(this)

        this.data = globalData
        this.columns = globalColumns
        this.modal = null

        initColumnsAndData(demo.columns, demo.data)
    }
  
    showModal = () => {
        this.setState({ show: true })
    }
  
    hideModal = () => {
        this.setState({ show: false })
    }

    render() {
        return (
            <div className="mainContainer">
                <h1>React Modal</h1>
                <Modal show={this.state.show} handleClose={this.hideModal}>
                    {this.modal} 
                </Modal>
                <button type="button" onClick={this.showModal}>Open</button>
                <ProjectList showModal={this.showModal} modal={this.modal} />
            </div>
        )
    }
}
  


export default App
