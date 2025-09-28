import React, { useState, useEffect, useRef } from 'react';
import './Admin.css';
import Logo from "../../assets/images/Logo.png";

import {
    Users,
    Activity,
    BarChart3,
    Shield,
    MessageSquare,
    TrendingUp,
    Clock,
    CheckCircle,
    AlertTriangle,
    FileText,
    Image as ImageIcon,
    Eye,
    ThumbsUp,
    Calendar,
    Search,
    Menu,
    X,
    ChevronRight,
    ArrowLeft,
    User,
    Target,
    Zap,
    Brain,
    Trash2,
    RefreshCw
} from 'lucide-react';
import { getAuthToken, isAuthenticated } from '../UserAuthentication/AuthHandler';

const AdminPage = () => {
    // API Configuration.
    const API_BASE_URL = 'http://localhost:8000';

    // State management
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentView, setCurrentView] = useState('dashboard');
    const [selectedUser, setSelectedUser] = useState(null);
    const [selectedFeedback, setSelectedFeedback] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [feedbackFilterType, setFeedbackFilterType] = useState('all');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Data states
    const [users, setUsers] = useState([]);
    const [feedback, setFeedback] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [recentActivity, setRecentActivity] = useState([]);

    const reportRef = useRef(null);

    // Get auth token and user data.
    const authToken = getAuthToken();
    const isUserAuthenticated = isAuthenticated();

    // Fetch statistics data on component mount
    useEffect(() => {
        const fetchDashboard = async () => {
            if (!isUserAuthenticated || !authToken) {
                setLoading(false);
                setError('Authentication required');
                return;
            }

            setLoading(true);
            setError(null);

            try {
                const response = await fetch(`${API_BASE_URL}/api/admin/dashboard/`, {
                    headers: {
                        'Authorization': `Token ${authToken}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error('Unauthorized access. Please check your admin privileges.');
                    } else if (response.status === 403) {
                        throw new Error('Forbidden. Admin access required.');
                    } else if (response.status === 404) {
                        throw new Error('Admin dashboard endpoint not found.');
                    } else {
                        throw new Error(`Server error: ${response.status}`);
                    }
                }

                const result = await response.json();
                
                if (result.success && result.data) {
                    setStatistics(result.data.statistics);
                    setRecentActivity(result.data.recent_activity);
                    console.log('Admin dashboard data loaded:', result.data);
                } else {
                    throw new Error(result.error || 'Failed to fetch dashboard data');
                }

            } catch (error) {
                console.error('Failed to fetch admin dashboard data:', error);
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, [isUserAuthenticated, authToken, API_BASE_URL]);

    // Mock data for development (remove when API is ready)
    useEffect(() => {
        if (statistics && users.length === 0) {
            // Mock data
            setUsers([
                {
                    id: 1,
                    name: 'Siyabonga Madondo',
                    email: 'MDNSIY014@myuct.ac.za',
                    joinDate: '2024-01-15',
                    totalAnalyses: 45,
                    accurateDetections: 42,
                    feedbackCount: 3
                },
                {
                    id: 2,
                    name: 'Sarah Johnson',
                    email: 'sarah.johnson@gmail.com',
                    joinDate: '2024-01-10',
                    totalAnalyses: 78,
                    accurateDetections: 71,
                    feedbackCount: 7
                },
                {
                    id: 3,
                    name: 'Mike Chen',
                    email: 'mike.chen@gmail.com',
                    joinDate: '2024-01-05',
                    totalAnalyses: 23,
                    accurateDetections: 20,
                    feedbackCount: 3
                }
            ]);

            setFeedback([
                {
                    id: 1,
                    userId: 1,
                    userName: 'Siyabonga Madondo',
                    submissionId: 'sub_123',
                    analysisId: 'ana_456',
                    feedbackText: 'The detection seems incorrect. This text was written by me, not AI.',
                    submittedAt: '2024-01-20T10:30:00Z',
                    status: 'pending',
                    analysisType: 'text',
                    originalPrediction: 'AI Generated',
                    confidence: 85
                },
                {
                    id: 2,
                    userId: 2,
                    userName: 'Sarah Johnson',
                    submissionId: 'sub_124',
                    analysisId: 'ana_457',
                    feedbackText: 'Great accuracy! The system correctly identified this as AI-generated content.',
                    submittedAt: '2024-01-19T15:45:00Z',
                    status: 'resolved',
                    analysisType: 'text',
                    originalPrediction: 'AI Generated',
                    confidence: 92
                },
                {
                    id: 3,
                    userId: 1,
                    userName: 'Siyabonga Madondo',
                    submissionId: 'sub_125',
                    analysisId: 'ana_458',
                    feedbackText: 'The image detection failed. This was clearly a real photograph.',
                    submittedAt: '2024-01-18T09:15:00Z',
                    status: 'reviewed',
                    analysisType: 'image',
                    originalPrediction: 'AI Generated',
                    confidence: 78
                }
            ]);

            console.log('Mock data loaded for admin dashboard');
        }
        
    }, [statistics, users.length]);

    // Handlers
    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const handleUserSelect = (user) => {
        setSelectedUser(user);
        setCurrentView('user-detail');
    };

    const handleFeedbackSelect = (feedbackItem) => {
        setSelectedFeedback(feedbackItem);
        setCurrentView('feedback-detail');
    };

    const deleteFeedback = async (feedbackId) => {
        try {
            const response = await fetch(`/api/admin/feedback/${feedbackId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                }
            });
            
            if (response.ok) {
                setFeedback(prev => prev.filter(item => item.id !== feedbackId));
            } else {
                throw new Error('Failed to delete feedback');
            }
        } catch (error) {
            console.error('Failed to delete feedback:', error);
            alert('Failed to delete feedback. Please try again.');
        }
    };

    // Filter functions
    const filteredUsers = users.filter(user => {
        const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            user.email.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
    });

    const filteredFeedback = feedback.filter(item => {
        const matchesSearch = item.feedbackText.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            item.userName.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = feedbackFilterType === 'all' || item.status === feedbackFilterType;
        return matchesSearch && matchesFilter;
    });

    // Navigation items
    const navigationItems = [
        { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 className="icon-sm" />, view: 'dashboard' },
        { id: 'users', label: 'Users', icon: <Users className="icon-sm" />, view: 'users' },
        { id: 'feedback', label: 'Feedback', icon: <MessageSquare className="icon-sm" />, view: 'feedback' },
        { id: 'activity', label: 'Activity', icon: <Activity className="icon-sm" />, view: 'activity' },
        { id: 'analytics', label: 'Analytics', icon: <TrendingUp className="icon-sm" />, view: 'analytics' }
    ];

    const StatCard = ({ title, value, change, icon, color = 'blue' }) => (
        <div className={`stat-card stat-card-${color}`}>
            <div className="stat-card-header">
                <div className={`stat-icon stat-icon-${color}`}>
                    {icon}
                </div>
                <div className="stat-info">
                    <div className="stat-value">{value}</div>
                    <div className="stat-title">{title}</div>
                </div>
            </div>
            {change && (
                <div className={`stat-change ${change.type}`}>
                    <TrendingUp className="icon-xs" />
                    <span>{change.value}</span>
                </div>
            )}
        </div>
    );

    if (loading) {
        return (
            <div className="admin-container">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <div className="loading-text">Loading admin dashboard...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="admin-container">
                <div className="error-container">
                    <div className="error-message">
                        <AlertTriangle className="icon-lg" />
                        <h3>Failed to load admin data</h3>
                        <p>{error}</p>
                        <button 
                            onClick={() => window.location.reload()} 
                            className="action-btn primary"
                        >
                            <RefreshCw className="icon-sm" />
                            Retry
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="admin-container">
            {/* Sidebar */}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <div className="sidebar-logo-icon">
                            <img src={Logo} alt="Detective AI Logo" className="logo-img" />
                        </div>
                        <span className="sidebar-title">Admin Panel</span>
                    </div>
                    <button className="close-sidebar" onClick={toggleSidebar}>
                        <X className="icon-sm" />
                    </button>
                </div>

                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">Administration</div>
                        {navigationItems.map((item) => (
                            <button
                                key={item.id}
                                className={`nav-item ${currentView === item.view ? 'active' : ''}`}
                                onClick={() => setCurrentView(item.view)}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                                <ChevronRight className="icon-xs" style={{ marginLeft: 'auto' }} />
                            </button>
                        ))}
                    </div>
                </nav>
            </div>

            {/* Header */}
            <header className={`admin-header ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="admin-header-inner">
                    <div className="header-left">
                        <button
                            className={`menu-toggle ${sidebarOpen ? 'sidebar-open' : ''}`}
                            onClick={toggleSidebar}
                        >
                            <Menu className="icon-sm" />
                        </button>

                        <div className="admin-logo">
                            <div className="admin-logo-icon">
                                <img src={Logo} alt="Detective AI Logo" className="logo-img" />
                            </div>
                            <div>
                                <h1 className="admin-title">Detective AI</h1>
                                <p className="admin-subtitle">Management Dashboard</p>
                            </div>
                        </div>
                    </div>

                    <div className="header-right">
                        <div className="admin-info">
                            <div className="admin-avatar">
                                <Shield className="icon-sm" />
                            </div>
                            <span>Administrator</span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className={`admin-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="content-area">
                    {currentView === 'dashboard' && statistics && (
                        <div className="dashboard-view">
                            <div className="view-header">
                                <div className="view-header-content">
                                    <h2 className="view-title">Dashboard Overview</h2>
                                    <p className="view-subtitle">Monitor system performance and user activity</p>
                                </div>
                            </div>

                            {/* Stats Grid */}
                            <div className="stats-grid">
                                <StatCard
                                    title="Total Users"
                                    value={statistics.users.total.toLocaleString()}
                                    change={{ type: 'positive', value: '+12.5%' }}
                                    icon={<Users className="icon-sm" />}
                                    color="blue"
                                />
                                <StatCard
                                    title="Analyses Today"
                                    value={statistics.analyses.today.toLocaleString()}
                                    change={{ type: 'positive', value: '+15.3%' }}
                                    icon={<Target className="icon-sm" />}
                                    color="purple"
                                />
                                <StatCard
                                    title="Analysis Success Rate"
                                    value={`${statistics.analyses.success_rate}%`}
                                    change={{ type: 'positive', value: '+2.1%' }}
                                    icon={<Brain className="icon-sm" />}
                                    color="orange"
                                />
                            </div>

                            {/* Quick Stats */}
                            <div className="quick-stats">
                                <div className="quick-stat-item">
                                    <div className="quick-stat-icon">
                                        <Clock className="icon-sm" />
                                    </div>
                                    <div>
                                        <div className="quick-stat-value">{statistics.performance.avg_processing_time_seconds}s</div>
                                        <div className="quick-stat-label">Avg Processing Time</div>
                                    </div>
                                </div>
                                <div className="quick-stat-item">
                                    <div className="quick-stat-icon">
                                        <Calendar className="icon-sm" />
                                    </div>
                                    <div>
                                        <div className="quick-stat-value">{statistics.submissions.this_week.toLocaleString()}</div>
                                        <div className="quick-stat-label">Analyses This Week</div>
                                    </div>
                                </div>
                                <div className="quick-stat-item">
                                    <div className="quick-stat-icon">
                                        <MessageSquare className="icon-sm" />
                                    </div>
                                    <div>
                                        <div className="quick-stat-value">{statistics.feedback.total}</div>
                                        <div className="quick-stat-label">Total Feedback</div>
                                    </div>
                                </div>
                                <div className="quick-stat-item">
                                    <div className="quick-stat-icon">
                                        <ThumbsUp className="icon-sm" />
                                    </div>
                                    <div>
                                        <div className="quick-stat-value">{statistics.feedback.satisfaction_rate}%</div>
                                        <div className="quick-stat-label">Positive Feedback</div>
                                    </div>
                                </div>
                            </div>

                            {/* Recent Activity */}
                            <div className="recent-activity-section">
                                <div className="section-header">
                                    <h3 className="section-title">Recent Activity</h3>
                                    <button className="action-btn" onClick={() => setCurrentView('activity')}>
                                        View All
                                        <ChevronRight className="icon-xs" />
                                    </button>
                                </div>
                                <div className="activity-list">
                                    {recentActivity.slice(0, 5).map((activity) => (
                                        <div key={activity.id} className="activity-item">
                                            <div className="activity-icon">
                                                {activity.type === 'analysis' && <FileText className="icon-sm" />}
                                                {activity.type === 'feedback' && <MessageSquare className="icon-sm" />}
                                                {activity.type === 'user' && <Users className="icon-sm" />}
                                            </div>
                                            <div className="activity-content">
                                                <div className="activity-title">{activity.action}</div>
                                                <div className="activity-meta">
                                                    {activity.user} • {new Date(activity.timestamp).toLocaleString()}
                                                </div>
                                            </div>
                                            <div className={`activity-status status-${activity.status}`}>
                                                {activity.status}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {currentView === 'users' && (
                        <div className="users-view">
                            <div className="view-header">
                                <div className="view-header-content">
                                    <h2 className="view-title">User Management</h2>
                                </div>
                                <div className="view-actions">
                                    <div className="search-bar">
                                        <Search className="icon-sm" />
                                        <input
                                            type="text"
                                            placeholder="Search users..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="users-grid">
                                {filteredUsers.map((user) => (
                                    <div key={user.id} className="user-card" onClick={() => handleUserSelect(user)}>
                                        <div className="user-card-header">
                                            <div className="user-avatar">
                                                <User className="icon-sm" />
                                            </div>
                                        </div>
                                        <div className="user-info">
                                            <h3 className="user-name">{user.name}</h3>
                                            <p className="user-email">{user.email}</p>
                                        </div>
                                        <div className="user-stats">
                                            <div className="user-stat">
                                                <span className="stat-value">{user.totalAnalyses}</span>
                                                <span className="stat-label">Analyses</span>
                                            </div>
                                            <div className="user-stat">
                                                <span className="stat-value">{Math.round((user.accurateDetections / user.totalAnalyses) * 100)}%</span>
                                                <span className="stat-label">Accuracy</span>
                                            </div>
                                            <div className="user-stat">
                                                <span className="stat-value">{user.feedbackCount}</span>
                                                <span className="stat-label">Feedback</span>
                                            </div>
                                        </div>
                                        <div className="user-meta">
                                            Joined {new Date(user.joinDate).toLocaleDateString()}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {currentView === 'user-detail' && selectedUser && (
                        <div className="user-detail-view">
                            <div className="view-header">
                                <button className="back-button" onClick={() => setCurrentView('users')}>
                                    <ArrowLeft className="icon-sm" />
                                    Back to Users
                                </button>
                                <h2 className="view-title">{selectedUser.name}</h2>
                            </div>

                            <div className="user-detail-content">
                                <div className="user-detail-card">
                                    <div className="user-detail-header">
                                        <div className="user-detail-avatar">
                                            <User className="icon-lg" />
                                        </div>
                                        <div className="user-detail-info">
                                            <h3>{selectedUser.name}</h3>
                                            <p>{selectedUser.email}</p>
                                        </div>
                                    </div>

                                    <div className="user-detail-stats">
                                        <div className="detail-stat">
                                            <div className="detail-stat-icon">
                                                <Target className="icon-sm" />
                                            </div>
                                            <div>
                                                <div className="detail-stat-value">{selectedUser.totalAnalyses}</div>
                                                <div className="detail-stat-label">Total Analyses</div>
                                            </div>
                                        </div>
                                        <div className="detail-stat">
                                            <div className="detail-stat-icon">
                                                <CheckCircle className="icon-sm" />
                                            </div>
                                            <div>
                                                <div className="detail-stat-value">{Math.round((selectedUser.accurateDetections / selectedUser.totalAnalyses) * 100)}%</div>
                                                <div className="detail-stat-label">Accuracy Rate</div>
                                            </div>
                                        </div>
                                        <div className="detail-stat">
                                            <div className="detail-stat-icon">
                                                <MessageSquare className="icon-sm" />
                                            </div>
                                            <div>
                                                <div className="detail-stat-value">{selectedUser.feedbackCount}</div>
                                                <div className="detail-stat-label">Feedback Given</div>
                                            </div>
                                        </div>
                                        <div className="detail-stat">
                                            <div className="detail-stat-icon">
                                                <Calendar className="icon-sm" />
                                            </div>
                                            <div>
                                                <div className="detail-stat-value">{new Date(selectedUser.joinDate).toLocaleDateString()}</div>
                                                <div className="detail-stat-label">Join Date</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* User's feedback */}
                                <div className="user-feedback-section">
                                    <h3 className="section-title">User Feedback</h3>
                                    <div className="feedback-list">
                                        {feedback.filter(f => f.userId === selectedUser.id).map((item) => (
                                            <div key={item.id} className="feedback-item">
                                                <div className="feedback-header">
                                                    <div className="feedback-type">
                                                        {item.analysisType === 'text' ? <FileText className="icon-sm" /> : <ImageIcon className="icon-sm" />}
                                                        <span>{item.analysisType} Analysis</span>
                                                    </div>
                                                    <div className={`feedback-status status-${item.status}`}>
                                                        {item.status}
                                                    </div>
                                                </div>
                                                <div className="feedback-content">
                                                    <p>{item.feedbackText}</p>
                                                </div>
                                                <div className="feedback-meta">
                                                    Original prediction: {item.originalPrediction} ({item.confidence}% confidence) • 
                                                    {new Date(item.submittedAt).toLocaleString()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {currentView === 'feedback' && (
                        <div className="feedback-view">
                            <div className="view-header">
                                <h2 className="view-title">User Feedback</h2>
                                <div className="view-actions">
                                    <div className="search-bar">
                                        <Search className="icon-sm" />
                                        <input
                                            type="text"
                                            placeholder="Search feedback..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                        />
                                    </div>
                                    <select
                                        className="filter-select"
                                        value={feedbackFilterType}
                                        onChange={(e) => setFeedbackFilterType(e.target.value)}
                                    >
                                        <option value="all">All Feedback</option>
                                        <option value="pending">Pending</option>
                                        <option value="reviewed">Reviewed</option>
                                        <option value="resolved">Resolved</option>
                                    </select>
                                </div>
                            </div>

                            <div className="feedback-grid">
                                {filteredFeedback.map((item) => (
                                    <div key={item.id} className="feedback-card">
                                        <div className="feedback-card-header">
                                            <div className="feedback-user">
                                                <User className="icon-sm" />
                                                <span>{item.userName}</span>
                                            </div>
                                            <div className={`feedback-status status-${item.status}`}>
                                                {item.status}
                                            </div>
                                        </div>
                                        <div className="feedback-card-content">
                                            <div className="feedback-type-info">
                                                {item.analysisType === 'text' ? <FileText className="icon-sm" /> : <ImageIcon className="icon-sm" />}
                                                <span>{item.analysisType} Analysis</span>
                                                <span className="confidence-badge">{item.confidence}% confidence</span>
                                            </div>
                                            <p className="feedback-text">{item.feedbackText}</p>
                                        </div>
                                        <div className="feedback-card-actions">
                                            <button 
                                                className="action-btn view"
                                                onClick={() => handleFeedbackSelect(item)}
                                            >
                                                <Eye className="icon-xs" />
                                                View Details
                                            </button>
                                            <button 
                                                className="action-btn delete"
                                                onClick={() => deleteFeedback(item.id)}
                                            >
                                                <Trash2 className="icon-xs" />
                                            </button>
                                        </div>
                                        <div className="feedback-card-meta">
                                            {new Date(item.submittedAt).toLocaleString()}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {currentView === 'feedback-detail' && selectedFeedback && (
                        <div className="feedback-detail-view">
                            <div className="view-header">
                                <button className="back-button" onClick={() => setCurrentView('feedback')}>
                                    <ArrowLeft className="icon-sm" />
                                    Back to Feedback
                                </button>
                                <h2 className="view-title">Feedback Details</h2>
                            </div>

                            <div className="feedback-detail-content">
                                <div className="feedback-detail-card">
                                    <div className="feedback-detail-header">
                                        <div className="feedback-user-info">
                                            <div className="user-avatar">
                                                <User className="icon-md" />
                                            </div>
                                            <div>
                                                <h3>{selectedFeedback.userName}</h3>
                                                <p>Submission ID: {selectedFeedback.submissionId}</p>
                                            </div>
                                        </div>
                                        <div className={`status-badge status-${selectedFeedback.status}`}>
                                            {selectedFeedback.status}
                                        </div>
                                    </div>

                                    <div className="analysis-info">
                                        <div className="analysis-type">
                                            {selectedFeedback.analysisType === 'text' ? <FileText className="icon-sm" /> : <ImageIcon className="icon-sm" />}
                                            <span>{selectedFeedback.analysisType} Analysis</span>
                                        </div>
                                        <div className="original-prediction">
                                            <span>Original Prediction: </span>
                                            <strong>{selectedFeedback.originalPrediction}</strong>
                                            <span className="confidence-badge">{selectedFeedback.confidence}% confidence</span>
                                        </div>
                                    </div>

                                    <div className="feedback-content-detail">
                                        <h4>User Feedback:</h4>
                                        <p>{selectedFeedback.feedbackText}</p>
                                    </div>

                                    <div className="feedback-meta-detail">
                                        <div className="meta-item">
                                            <Clock className="icon-sm" />
                                            <span>Submitted: {new Date(selectedFeedback.submittedAt).toLocaleString()}</span>
                                        </div>
                                        <div className="meta-item">
                                            <Target className="icon-sm" />
                                            <span>Analysis ID: {selectedFeedback.analysisId}</span>
                                        </div>
                                    </div>

                                    <div className="feedback-actions">
                                        <button className="action-btn primary">
                                            <CheckCircle className="icon-sm" />
                                            Mark as Resolved
                                        </button>
                                        <button className="action-btn secondary">
                                            <RefreshCw className="icon-sm" />
                                            Re-analyze
                                        </button>
                                        <button className="action-btn delete" onClick={() => deleteFeedback(selectedFeedback.id)}>
                                            <Trash2 className="icon-sm" />
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {currentView === 'activity' && (
                        <div className="activity-view">
                            <div className="view-header">
                                <h2 className="view-title">System Activity</h2>
                                <div className="view-actions">
                                    <button className="action-btn">
                                        <RefreshCw className="icon-sm" />
                                        Refresh
                                    </button>
                                </div>
                            </div>

                            <div className="activity-timeline">
                                {recentActivity.map((activity) => (
                                    <div key={activity.id} className="timeline-item">
                                        <div className="timeline-marker">
                                            <div className={`timeline-icon ${activity.type}`}>
                                                {activity.type === 'analysis' && <FileText className="icon-xs" />}
                                                {activity.type === 'feedback' && <MessageSquare className="icon-xs" />}
                                                {activity.type === 'user' && <Users className="icon-xs" />}
                                            </div>
                                        </div>
                                        <div className="timeline-content">
                                            <div className="timeline-header">
                                                <h4>{activity.action}</h4>
                                                <div className={`activity-status status-${activity.status}`}>
                                                    {activity.status}
                                                </div>
                                            </div>
                                            <div className="timeline-meta">
                                                <span className="activity-user">{activity.user}</span>
                                                {activity.analysisType && (
                                                    <span className="activity-type">• {activity.analysisType} analysis</span>
                                                )}
                                                <span className="activity-time">• {new Date(activity.timestamp).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {currentView === 'analytics' && statistics && (
                        <div className="analytics-view" ref={reportRef}>
                            <div className="view-header">
                                <h2 className="view-title">Analytics & Reports</h2>
                                <div className="view-actions">
                                </div>
                            </div>

                            <div className="analytics-content">
                                {/* Performance Metrics */}
                                <div className="analytics-section">
                                    <h3 className="section-title">Performance Metrics</h3>
                                    <div className="metrics-grid">
                                        <div className="metric-card">
                                            <div className="metric-header">
                                                <Target className="icon-sm" />
                                                <span>Analysis Success Rate</span>
                                            </div>
                                            <div className="metric-value">{statistics.analyses.success_rate}%</div>
                                            <div className="metric-change positive">+2.1% from last week</div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-header">
                                                <Zap className="icon-sm" />
                                                <span>Avg Processing Time</span>
                                            </div>
                                            <div className="metric-value">{statistics.performance.avg_processing_time_seconds}s</div>
                                            <div className="metric-change negative">+0.3s from last week</div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-header">
                                                <Users className="icon-sm" />
                                                <span>User Satisfaction</span>
                                            </div>
                                            <div className="metric-value">{statistics.feedback.satisfaction_rate}%</div>
                                            <div className="metric-change positive">+5.2% from last week</div>
                                        </div>
                                    </div>
                                </div>

                                {/* Usage Statistics */}
                                <div className="analytics-section">
                                    <h3 className="section-title">Usage Statistics</h3>
                                    <div className="usage-stats">
                                        <div className="usage-stat">
                                            <div className="usage-icon">
                                                <FileText className="icon-sm" />
                                            </div>
                                            <div className="usage-info">
                                                <div className="usage-value">{5}</div>
                                                <div className="usage-label">Text Analyses</div>
                                                <div className="usage-percentage">75% of total</div>
                                            </div>
                                        </div>
                                        <div className="usage-stat">
                                            <div className="usage-icon">
                                                <ImageIcon className="icon-sm" />
                                            </div>
                                            <div className="usage-info">
                                                <div className="usage-value">{10}</div>
                                                <div className="usage-label">Image Analyses</div>
                                                <div className="usage-percentage">25% of total</div>
                                            </div>
                                        </div>
                                        <div className="usage-stat">
                                            <div className="usage-icon">
                                                <ThumbsUp className="icon-sm" />
                                            </div>
                                            <div className="usage-info">
                                                <div className="usage-value">{statistics.feedback.positive}</div>
                                                <div className="usage-label">Positive Feedback</div>
                                                <div className="usage-percentage">{statistics.feedback.satisfaction_rate}% of feedback</div>
                                            </div>
                                        </div>
                                        <div className="usage-stat">
                                            <div className="usage-icon">
                                                <AlertTriangle className="icon-sm" />
                                            </div>
                                            <div className="usage-info">
                                                <div className="usage-value">{statistics.feedback.negative}</div>
                                                <div className="usage-label">Issues Reported</div>
                                                <div className="usage-percentage">{Math.round((statistics.feedback.negative / statistics.feedback.total) * 100)}% of feedback</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default AdminPage;