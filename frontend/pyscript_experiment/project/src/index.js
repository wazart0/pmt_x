import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
// import { CanvasGantt } from "gantt";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);




// const data1 = [{
//   id: 1,
//   type: 'group',
//   text: '1 Waterfall model',
//   start: new Date('2018-10-10T09:24:24.319Z'),
//   end: new Date('2018-12-12T09:32:51.245Z'),
//   percent: 0.71,
//   links: []
// }, {
//   id: 11,
//   parent: 1,
//   text: '1.1 Requirements',
//   start: new Date('2018-10-21T09:24:24.319Z'),
//   end: new Date('2018-11-22T01:01:08.938Z'),
//   percent: 0.29,
//   links: [{
//     target: 12,
//     type: 'FS'
//   }]
// }, {
//   id: 12,
//   parent: 1,
//   text: '1.2 Design',
//   start: new Date('2018-11-05T09:24:24.319Z'),
//   end: new Date('2018-12-12T09:32:51.245Z'),
//   percent: 0.78,
// }];

// const canvasGantt = new CanvasGantt('#canvas-root', data1, {
//     viewMode: 'week'
//   });

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
