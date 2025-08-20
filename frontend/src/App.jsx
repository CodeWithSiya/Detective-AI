import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Login from './Components/LoginSignUP/Login'
import Signup from './Components/LoginSignUP/Signup';
import ForgotPassword from './Components/LoginSignUP/ForgotPassword';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DetectivePage from './Components/DetectivePage/DetectivePage';
import DemoLandingPage from './Components/DemoLandingPage/DemoLandingPage';
import Team from './Components/Team/Team';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DemoLandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/detective" element={<DetectivePage />} />
        <Route path="/team" element={<Team />} />
      </Routes>
    </Router>
  )
}
export default App
