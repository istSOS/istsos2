// import { useState } from 'react'
import reactLogo from './assets/react.svg'
import istsosLogo from '../public/istsos.png'
import './App.css'
import Navbar from './Navbar';


function App() {
  // const [] = useState(0)

  return (
    <>
      <div className="app">
        <Navbar/>
        <div>
          <a href="https://istsos.org/" target="_blank">
            <img src={istsosLogo} className="logo" alt="istsos logo" />
          </a>
          <a href="https://react.dev" target="_blank">
            <img src={reactLogo} className="logo react" alt="React logo" />
          </a>
        </div>

        <h1 className='entry-welcome'>Welcome to istSOS</h1>
        <div >
          <button className="start-button">
            Load isoSOS
          </button>
        </div>
        <p className="read-the-docs">
          Click on the istSOS to learn more
        </p>
      </div>
    </>
  )
}

export default App
