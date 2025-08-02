/**
 * Wikipedia Path Finder - React Application
 * 
 * Main application component with routing and global state management.
 * 
 * @author Gildian Gonzales
 * @license MIT
 */

import { Routes, Route } from "react-router-dom";
import Home from './views/Home';
import './App.css';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="*" element={
          <div className="error-page">
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/">Return to Home</a>
          </div>
        } />
      </Routes>
    </div>
  );
}

export default App;
