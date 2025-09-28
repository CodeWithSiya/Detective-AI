import './App.css'
import Login from '../components/userAuthentication/login/Login'
import Signup from '../components/userAuthentication/signup/Signup';
import ForgotPassword from '../components/userAuthentication/forgotPassword/ForgotPassword';
import VerifyEmail from '../components/userAuthentication/verifyPassword/VerifyEmail';
import ChangePassword from '../components/userAuthentication/changePassword/ChangePassword'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DetectivePage from '../components/detectivePage/DetectivePage';
import DemoLandingPage from '../components/demoLandingPage/DemoLandingPage';
import Team from '../components/team/Team';
import ScrollToTop from '../utils/scrollToTop/ScrollToTop';
import Admin from '../components/admin/Admin';
import DetectiveBasic from '../components/basicDetectivePage/DetectiveBasic';
import ManageUser from '../components/userManagement/ManageUser';

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