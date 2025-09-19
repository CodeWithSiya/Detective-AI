import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Login from './components/UserAuthentication/Login/Login'
import Signup from './components/UserAuthentication/Signup/Signup';
import ForgotPassword from './components/UserAuthentication/ForgotPassword/ForgotPassword';
import VerifyEmail from './components/UserAuthentication/VerifyPassword/VerifyEmail';
import ChangePassword from './components/UserAuthentication/ChangePassword/ChangePassword'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DetectivePage from './Components/DetectivePage/DetectivePage';
import DemoLandingPage from './Components/DemoLandingPage/DemoLandingPage';
import Team from './Components/Team/Team';
import ScrollToTop from './Components/ScrollToTop/ScrollToTop';
import BasicDetectivePage from './Components/Basic-DetectivePage/BasicDetectivePage';
import Admin from './Components/Admin/Admin';

function App() {
  return (
    <Router>
    <ScrollToTop/>
      <Routes>
        <Route path="/" element={<DemoLandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/verify-email" element={<VerifyEmail />}/>
        <Route path="/change-password" element={<ChangePassword/>}/>
        <Route path="/detective" element={<DetectivePage />} />
        <Route path="/team" element={<Team />} />
        <Route path="/basic-detective" element={<BasicDetectivePage />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Router>
  )
}
export default App