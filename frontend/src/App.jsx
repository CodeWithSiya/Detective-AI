import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Login from './Components/UserAuthentication/Login'
import Signup from './Components/UserAuthentication/Signup';
import ForgotPassword from './Components/UserAuthentication/ForgotPassword';
import VerifyEmail from './Components/UserAuthentication/VerifyEmail';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/verify-email" element={<VerifyEmail />}/>
      </Routes>
    </Router>
  )
}

export default App
