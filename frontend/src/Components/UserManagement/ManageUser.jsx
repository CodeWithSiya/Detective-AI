import React, { useState, useEffect, useRef } from 'react';
import './ManageUser.css';
import Logo from "../Assets/Logo.png";
import {
    Search,
    Eye,
    EyeOff,
    X,
    ChevronRight,
    FileText,
    Image as ImageIcon,
    History,
    Users,
    BarChart3,
    Plus,
    Trash2,
    Share,
    Upload,
    Clock,
    Shield,
    Zap,
    CheckCircle,
    AlertTriangle,
    Activity,
    Type,
    FileUp,
    Download,
    Mail,
    ThumbsUp,
    ThumbsDown,
    AlertCircle,
    ArrowLeft,
    Loader,
    Menu,
    Target,
    TrendingUp,
    Brain,
    FileCheck,
    Info,
    Home,
    Settings,
    User,
    Save,
    UserX,
    Key,
    Edit3
} from 'lucide-react';
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { getAuthToken, isAuthenticated, getCurrentUser, logout } from "../UserAuthentication/AuthHandler";

const ManageUser = () => {
    // API Configuration
    const API_BASE_URL = 'http://localhost:8000';
    const navigate = useNavigate();

    // Get auth token and user data
    const authToken = getAuthToken();
    const isUserAuthenticated = isAuthenticated();
    const currentUser = getCurrentUser();

    // Redirect to login if not authenticated
    /*useEffect(() => {
        if (!isUserAuthenticated) {
            navigate('/', { replace: true });
            return;
        }
    }, [isUserAuthenticated, navigate]);*/

    // State management
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentView, setCurrentView] = useState('profile'); // 'profile', 'security', 'danger'
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    // Profile form state
    const [profileData, setProfileData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        username: ''
    });

    // Password change state
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    // UI state
    const [showCurrentPassword, setShowCurrentPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [showDeactivateModal, setShowDeactivateModal] = useState(false);
    const [deactivateConfirmText, setDeactivateConfirmText] = useState('');

    // Load user profile data
    useEffect(() => {
        if (currentUser) {
            setProfileData({
                firstName: currentUser.first_name || '',
                lastName: currentUser.last_name || '',
                email: currentUser.email || '',
                username: currentUser.username || ''
            });
        }
    }, [currentUser]);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    // Handle profile update
    const handleProfileUpdate = async (e) => {
        e.preventDefault();
        setIsSaving(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/user/profile/update/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`,
                },
                body: JSON.stringify({
                    first_name: profileData.firstName,
                    last_name: profileData.lastName,
                    email: profileData.email,
                    username: profileData.username
                }),
            });

            const data = await response.json();

            if (data.success) {
                alert('Profile updated successfully!');
                // Optionally refresh user data in auth context
            } else {
                throw new Error(data.error || 'Failed to update profile');
            }
        } catch (error) {
            console.error('Profile update failed:', error);
            alert('Failed to update profile. Please try again.');
        } finally {
            setIsSaving(false);
        }
    };

    // Handle password change
    const handlePasswordChange = async (e) => {
        e.preventDefault();
        
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            alert('New passwords do not match!');
            return;
        }

        if (passwordData.newPassword.length < 8) {
            alert('Password must be at least 8 characters long!');
            return;
        }

        setIsSaving(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/user/password/change/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`,
                },
                body: JSON.stringify({
                    current_password: passwordData.currentPassword,
                    new_password: passwordData.newPassword
                }),
            });

            const data = await response.json();

            if (data.success) {
                alert('Password changed successfully!');
                setPasswordData({
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: ''
                });
            } else {
                throw new Error(data.error || 'Failed to change password');
            }
        } catch (error) {
            console.error('Password change failed:', error);
            alert('Failed to change password. Please check your current password and try again.');
        } finally {
            setIsSaving(false);
        }
    };

    // Handle account deactivation
    const handleAccountDeactivation = async () => {
        if (deactivateConfirmText.toLowerCase() !== 'deactivate') {
            alert('Please type "deactivate" to confirm');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/user/deactivate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`,
                }
            });

            const data = await response.json();

            if (data.success) {
                alert('Account deactivated successfully. You will be logged out.');
                logout(); // Clear auth data
                navigate('/', { replace: true });
            } else {
                throw new Error(data.error || 'Failed to deactivate account');
            }
        } catch (error) {
            console.error('Account deactivation failed:', error);
            alert('Failed to deactivate account. Please try again.');
        } finally {
            setIsLoading(false);
            setShowDeactivateModal(false);
        }
    };

    // Handle logout
    const handleLogout = async () => {
        try {
            setIsLoading(true);            
            await fetch(`${API_BASE_URL}/api/auth/logout/`, {
                method: 'POST',
                headers: {
                'Authorization': `Token ${authToken}`,
            }
         });
            
            logout(); // Clear auth data
            navigate('/', { replace: true });
        } catch (error) {
            console.error('Logout failed:', error);
            //even if API call fails, still clear local auth
            logout();
            navigate('/', { replace: true });
        } finally {
            setIsLoading(false);
        }
    };

    const navigationItems = [
        { id: 'detective', label: 'Detector', icon: <Search className="icon-sm" /> },
        { id: 'team', label: 'Team', icon: <Users className="icon-sm" /> },
        { id: 'manage-user', label: 'Manage Account', icon: <Settings className="icon-sm" />, active: true },
        { id: '', label: 'Landing Page', icon: <Home className="icon-sm" /> }
    ];

    const managementSections = [
        { id: 'profile', label: 'Profile Settings', icon: <User className="icon-sm" />, active: currentView === 'profile' },
        { id: 'security', label: 'Security', icon: <Shield className="icon-sm" />, active: currentView === 'security' },
        { id: 'danger', label: 'Account Actions', icon: <AlertTriangle className="icon-sm" />, active: currentView === 'danger' }
    ];

    return (
        <div className="detective-container">
            {/* Sidebar */}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="detective-logo">
                        <div className="logo-icon">
                            <img src={Logo} alt="Detective AI Logo" className="logo-img" />
                        </div>
                        <span className="sidebar-title">Detective AI</span>
                    </div>
                    <button className="close-sidebar" onClick={toggleSidebar}>
                        <Menu className="icon-sm" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">Navigation</div>
                        {navigationItems.map((item) => (
                            <RouterLink
                                key={item.id}
                                to={`/${item.id}`}
                                className={`nav-item ${item.active ? 'active' : ''}`}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                                <ChevronRight className="icon-xs" style={{ marginLeft: 'auto' }} />
                            </RouterLink>
                        ))}
                    </div>

                    {/* Management Sections */}
                    <div className="nav-section">
                        <div className="nav-section-title">User Management</div>
                        {managementSections.map((section) => (
                            <button
                                key={section.id}
                                className={`nav-item ${section.active ? 'active' : ''}`}
                                onClick={() => setCurrentView(section.id)}
                            >
                                {section.icon}
                                <span>{section.label}</span>
                                <ChevronRight className="icon-xs" style={{ marginLeft: 'auto' }} />
                            </button>
                        ))}
                    </div>
                </nav>
            </div>

            {/* Header */}
            <header className={`detective-header ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="detective-header-inner">
                    <div className="header-left">
                        {!sidebarOpen && (
                            <button className="menu-toggle" onClick={toggleSidebar}>
                                <Menu className="icon-sm" />
                            </button>
                        )}
                        <div className="detective-logo">
                            <div className="logo-icon">
                                <img src={Logo} alt="Detective AI Logo" className="logo-img" />
                            </div>
                            <div>
                                <h1 className="detective-title">Detective AI</h1>
                                <p className="detective-subtitle">User Management</p>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className={`detective-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="content-area">
                    <div className="manage-user-interface">
                        <div className="interface-header">
                            <h1 className="interface-title">Manage Your Account</h1>
                            <p className="interface-subtitle">
                                Update your profile, security settings, and account preferences
                            </p>
                        </div>

                        {/* Profile Settings */}
                        {currentView === 'profile' && (
                            <div className="settings-container">
                                <div className="settings-header">
                                    <div className="settings-icon">
                                        <User className="icon-md text-white" />
                                    </div>
                                    <div>
                                        <h2 className="settings-title">Profile Settings</h2>
                                        <p className="settings-subtitle">Manage your personal information and preferences</p>
                                    </div>
                                </div>

                                <form className="settings-form" onSubmit={handleProfileUpdate}>
                                    <div className="form-grid">
                                        <div className="form-group">
                                            <label className="form-label">First Name</label>
                                            <input
                                                type="text"
                                                className="form-input"
                                                value={profileData.firstName}
                                                onChange={(e) => setProfileData(prev => ({
                                                    ...prev,
                                                    firstName: e.target.value
                                                }))}
                                                placeholder="Enter your first name"
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label className="form-label">Last Name</label>
                                            <input
                                                type="text"
                                                className="form-input"
                                                value={profileData.lastName}
                                                onChange={(e) => setProfileData(prev => ({
                                                    ...prev,
                                                    lastName: e.target.value
                                                }))}
                                                placeholder="Enter your last name"
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label className="form-label">Username</label>
                                            <input
                                                type="text"
                                                className="form-input"
                                                value={profileData.username}
                                                onChange={(e) => setProfileData(prev => ({
                                                    ...prev,
                                                    username: e.target.value
                                                }))}
                                                placeholder="Enter your username"
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label className="form-label">Email Address</label>
                                            <input
                                                type="email"
                                                className="form-input"
                                                value={profileData.email}
                                                onChange={(e) => setProfileData(prev => ({
                                                    ...prev,
                                                    email: e.target.value
                                                }))}
                                                placeholder="Enter your email address"
                                            />
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        className="save-button"
                                        disabled={isSaving}
                                    >
                                        {isSaving ? (
                                            <>
                                                <Loader className="icon-sm animate-spin" />
                                                Saving...
                                            </>
                                        ) : (
                                            <>
                                                <Save className="icon-sm" />
                                                Save Changes
                                            </>
                                        )}
                                    </button>
                                </form>
                            </div>
                        )}

                        {/* Security Settings */}
                        {currentView === 'security' && (
                            <div className="settings-container">
                                <div className="settings-header">
                                    <div className="settings-icon">
                                        <Shield className="icon-md text-white" />
                                    </div>
                                    <div>
                                        <h2 className="settings-title">Security Settings</h2>
                                        <p className="settings-subtitle">Update your password and security preferences</p>
                                    </div>
                                </div>

                                <form className="settings-form" onSubmit={handlePasswordChange}>
                                    <div className="form-group">
                                        <label className="form-label">Current Password</label>
                                        <div className="password-input-container">
                                            <input
                                                type={showCurrentPassword ? "text" : "password"}
                                                className="form-input"
                                                value={passwordData.currentPassword}
                                                onChange={(e) => setPasswordData(prev => ({
                                                    ...prev,
                                                    currentPassword: e.target.value
                                                }))}
                                                placeholder="Enter your current password"
                                            />
                                            <button
                                                type="button"
                                                className="password-toggle"
                                                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                                            >
                                                {showCurrentPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">New Password</label>
                                        <div className="password-input-container">
                                            <input
                                                type={showNewPassword ? "text" : "password"}
                                                className="form-input"
                                                value={passwordData.newPassword}
                                                onChange={(e) => setPasswordData(prev => ({
                                                    ...prev,
                                                    newPassword: e.target.value
                                                }))}
                                                placeholder="Enter your new password"
                                            />
                                            <button
                                                type="button"
                                                className="password-toggle"
                                                onClick={() => setShowNewPassword(!showNewPassword)}
                                            >
                                                {showNewPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Confirm New Password</label>
                                        <div className="password-input-container">
                                            <input
                                                type={showConfirmPassword ? "text" : "password"}
                                                className="form-input"
                                                value={passwordData.confirmPassword}
                                                onChange={(e) => setPasswordData(prev => ({
                                                    ...prev,
                                                    confirmPassword: e.target.value
                                                }))}
                                                placeholder="Confirm your new password"
                                            />
                                            <button
                                                type="button"
                                                className="password-toggle"
                                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                            >
                                                {showConfirmPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="password-requirements">
                                        <p className="requirements-title">Password Requirements:</p>
                                        <ul className="requirements-list">
                                            <li>At least 8 characters long</li>
                                            <li>Mix of uppercase and lowercase letters</li>
                                            <li>Include at least one number</li>
                                            <li>Include at least one special character</li>
                                        </ul>
                                    </div>

                                    <button
                                        type="submit"
                                        className="save-button"
                                        disabled={isSaving}
                                    >
                                        {isSaving ? (
                                            <>
                                                <Loader className="icon-sm animate-spin" />
                                                Updating...
                                            </>
                                        ) : (
                                            <>
                                                <Key className="icon-sm" />
                                                Change Password
                                            </>
                                        )}
                                    </button>
                                </form>
                            </div>
                        )}

                        {/* Danger Zone */}
                        {currentView === 'danger' && (
                            <div className="settings-container danger-zone">
                                <div className="settings-header">
                                    <div className="settings-icon danger">
                                        <AlertTriangle className="icon-md text-white" />
                                    </div>
                                    <div>
                                        <h2 className="settings-title">Account Actions</h2>
                                        <p className="settings-subtitle">Irreversible actions that affect your account</p>
                                    </div>
                                </div>

                                <div className="danger-actions">
                                    <div className="danger-item logout-item">
                                        <div className="danger-info">
                                            <h3 className="logout-title">Logout</h3>
                                            <p className="danger-description">
                                                Sign out of your account. You can log back in anytime with your credentials.
                                            </p>
                                        </div>
                                        <button
                                            className="logout-button"
                                            onClick={handleLogout}
                                            disabled={isLoading}
                                        >
                                            {isLoading ? (
                                                <>
                                                    <Loader className="icon-sm animate-spin" />
                                                    Logging out...
                                                </>
                                            ) : (
                                                <>
                                                    <ArrowLeft className="icon-sm" />
                                                    Logout
                                                </>
                                            )}
                                        </button>
                                    </div>
                                    
                                    <div className="danger-item">
                                        <div className="danger-info">
                                            <h3 className="danger-title">Deactivate Account</h3>
                                            <p className="danger-description">
                                                This will permanently deactivate your account and delete all your data. 
                                                This action cannot be undone. You will be logged out immediately.
                                            </p>
                                        </div>
                                        <button
                                            className="danger-button"
                                            onClick={() => setShowDeactivateModal(true)}
                                        >
                                            <UserX className="icon-sm" />
                                            Deactivate Account
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </main>

            {/* Deactivate Account Modal */}
            {showDeactivateModal && (
                <div className="modal-overlay" onClick={() => setShowDeactivateModal(false)}>
                    <div className="modal danger-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <div className="danger-modal-icon">
                                <AlertTriangle className="icon-md" />
                            </div>
                            <div>
                                <h3 className="modal-title">Deactivate Account</h3>
                                <p className="modal-subtitle">This action cannot be undone</p>
                            </div>
                            <button className="modal-close" onClick={() => setShowDeactivateModal(false)}>
                                <X className="icon-sm" />
                            </button>
                        </div>
                        
                        <div className="modal-content">
                            <p className="danger-warning">
                                Are you sure you want to deactivate your account? This will:
                            </p>
                            <ul className="danger-list">
                                <li>Permanently delete all your analysis history</li>
                                <li>Remove your profile and personal information</li>
                                <li>Revoke access to all Detective AI features</li>
                                <li>Log you out immediately</li>
                            </ul>
                            <p className="danger-confirm-text">
                                Type <strong>deactivate</strong> to confirm:
                            </p>
                            <input
                                type="text"
                                className="danger-confirm-input"
                                placeholder="Type 'deactivate' here"
                                value={deactivateConfirmText}
                                onChange={(e) => setDeactivateConfirmText(e.target.value)}
                            />
                        </div>

                        <div className="modal-actions">
                            <button 
                                className="modal-btn cancel" 
                                onClick={() => setShowDeactivateModal(false)}
                            >
                                Cancel
                            </button>
                            <button 
                                className="modal-btn danger" 
                                onClick={handleAccountDeactivation}
                                disabled={isLoading || deactivateConfirmText.toLowerCase() !== 'deactivate'}
                            >
                                {isLoading ? (
                                    <>
                                        <Loader className="icon-sm animate-spin" />
                                        Deactivating...
                                    </>
                                ) : (
                                    <>
                                        <UserX className="icon-sm" />
                                        Deactivate Account
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ManageUser;