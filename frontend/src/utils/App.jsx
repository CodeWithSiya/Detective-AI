import './App.css'
import Login from '../components/UserAuthentication/Login/Login';
import Signup from '../components/UserAuthentication/Signup/Signup';
import ForgotPassword from '../components/UserAuthentication/ForgotPassword/ForgotPassword';
import VerifyEmail from '../components/UserAuthentication/VerifyPassword/VerifyEmail';
import ChangePassword from '../components/UserAuthentication/ChangePassword/ChangePassword'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DetectivePage from '../components/DetectivePage/DetectivePage';
import DemoLandingPage from '../components/DemoLandingPage/DemoLandingPage';
import Team from '../components/Team/Team';
import ScrollToTop from './scrollToTop/ScrollToTop';
import Admin from '../components/Admin/Admin';
import DetectiveBasic from '../components/BasicDetectivePage/DetectiveBasic';
import ManageUser from '../components/UserManagement/ManageUser';

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
        <Route path="/detective-basic" element={<DetectiveBasic />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/manage-user" element={<ManageUser />} />
      </Routes>
    </Router>
  )
}
export default App