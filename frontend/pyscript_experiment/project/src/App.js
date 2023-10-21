import React from "react";
import ProjectTable from "./components/ProjectTable";
import * as demo from "./components/tmpData";





function App() {
    return (
        <div className="mainContainer">
            <ProjectTable data={demo.data} columns={demo.columns}/>
        </div>
    );
}

export default App;