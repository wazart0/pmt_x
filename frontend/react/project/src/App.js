import React, { Component } from "react"
import ProjectList from "./components/ProjectList"
import Modal from "./components/Modal"
import { sortByWBS } from "./components/ProjectVars"
// import { data as globalData, columns as globalColumns, initColumnsAndData } from "./components/ProjectVars"
import * as demo from "./components/tmpData"


class App extends Component {
    constructor() {
        super()
        this.state = {
            show: false
        }
        this.modalShow = this.modalShow.bind(this)
        this.modalHide = this.modalHide.bind(this)
        this.modalContent = {'content': null}

        this.data = structuredClone(demo.data)
        this.columns = structuredClone(demo.columns)
        
        sortByWBS(this.data)
    }
  
    modalShow = () => {
        this.setState({ show: true })
    }
  
    modalHide = () => {
        this.setState({ show: false })
    }

    // modalContent = (content) => {
    //     console.log("content")
    //     console.log(content)
    //     return content
    // }

    render() {
        return (
            <div className="mainContainer">
                <Modal show={this.state.show} handleClose={this.modalHide}>
                    {this.modalContent}
                </Modal>
                <div background-color='blue' display='inline-block' width='200px' overflow='scroll'>
                    <ProjectList data={this.data} columns={this.columns} modalContent={this.modalContent} modalShow={this.modalShow} />
                </div>
                <div background-color='powderblue' display='inline-block' width='50%'>ddd</div>
            </div>
        )
    }
}
  


export default App
