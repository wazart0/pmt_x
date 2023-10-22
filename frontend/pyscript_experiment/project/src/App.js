import React from "react";
import ProjectList from "./components/ProjectList";
import * as demo from "./components/tmpData";
import { initColumnsAndData } from "./components/ProjectVars";





function App() {
    initColumnsAndData(demo.columns, demo.data);
    return (
        <div className="mainContainer">
            <ProjectList />
        </div>
    );
}

export default App;
