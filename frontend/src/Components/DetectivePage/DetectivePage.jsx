import React, {useState, useRef, useEffect} from 'react';
import './DetectivePage.css';
import Logo from "../Assets/Logo.png";
import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker?url";
import {
    Search, Eye, X, ChevronRight, FileText, Image as ImageIcon, History, Users,
    BarChart3, Play, Plus, Trash2, Share, Upload, Clock, Shield, Zap, CheckCircle,
    AlertTriangle, Activity, Type, FileUp, Download, Mail, ThumbsUp, ThumbsDown,
    AlertCircle, ArrowLeft, Loader, Menu, Target, TrendingUp, Brain, FileCheck, Info
} from 'lucide-react';
import { Link as RouterLink } from "react-router-dom";
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;

const DetectivePage = () => {
    // API Configuration
    const API_BASE_URL = 'http://localhost:8000'; // Adjust for your Django server
    
    // UI State
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentView, setCurrentView] = useState('main');
    const [activeDetectionType, setActiveDetectionType] = useState('text');
    const [inputMode, setInputMode] = useState('type');
    const [textContent, setTextContent] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [uploadedImage, setUploadedImage] = useState(null);
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedbackText, setFeedbackText] = useState('');
    const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Data State - now from API
    const [historyItems, setHistoryItems] = useState([]);
    const [recentStats, setRecentStats] = useState([]);
    const [recentActivity, setRecentActivity] = useState([]);
    const [feedbackList, setFeedbackList] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);

    // Refs
    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);
    const reportRef = useRef(null);

    // Load initial data
    useEffect(() => {
        loadInitialData();
    }, []);

    const loadInitialData = async () => {
        try {
            setLoading(true);
            await Promise.all([
                fetchUserProfile(),
                fetchUserSubmissions(),
                fetchSubmissionStats(),
                fetchUserFeedback()
            ]);
        } catch (err) {
            setError('Failed to load data');
            console.error('Initial data load error:', err);
        } finally {
            setLoading(false);
        }
    };

    // API Functions
    const fetchUserProfile = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/users/me/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const user = await response.json();
                setCurrentUser(user);
            }
        } catch (err) {
            console.error('Failed to fetch user profile:', err);
        }
    };

    const fetchUserSubmissions = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/submissions/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const submissions = await response.json();
                // Transform API data to match UI format
                const formattedHistory = submissions.map(sub => ({
                    id: sub.id,
                    type: sub.content_type || 'text',
                    title: sub.title || `${sub.content_type} Analysis`,
                    date: formatDate(sub.created_at),
                    content: sub.content,
                    result: {
                        isAI: sub.ai_confidence > 50,
                        confidence: sub.ai_confidence,
                        highlightedText: sub.highlighted_content || sub.content,
                        detectionReasons: sub.detection_reasons || [],
                        statistics: sub.analysis_statistics || {}
                    }
                }));
                setHistoryItems(formattedHistory);

                // Set recent activity from submissions
                const recentActivities = submissions.slice(0, 3).map(sub => ({
                    id: sub.id,
                    title: `${sub.content_type} analysis completed`,
                    time: formatDate(sub.created_at),
                    status: 'success',
                    type: sub.content_type
                }));
                setRecentActivity(recentActivities);
            }
        } catch (err) {
            console.error('Failed to fetch submissions:', err);
        }
    };

    const fetchSubmissionStats = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/submissions/statistics/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const stats = await response.json();
                const formattedStats = [
                    { label: 'Today', value: stats.today_count?.toString() || '0', change: '+12%' },
                    { label: 'This Week', value: stats.week_count?.toString() || '0', change: '+8%' },
                    { label: 'Accuracy', value: `${stats.accuracy_rate || 94.2}%`, change: '+2.1%' },
                    { label: 'Avg Time', value: `${stats.avg_analysis_time || 8.3}s`, change: '-1.2s' },
                ];
                setRecentStats(formattedStats);
            }
        } catch (err) {
            console.error('Failed to fetch stats:', err);
        }
    };

    const fetchUserFeedback = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/feedback/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const feedback = await response.json();
                const formattedFeedback = feedback.map(fb => ({
                    id: fb.id,
                    query: fb.analysis?.title || 'Analysis',
                    feedback: fb.feedback_text,
                    date: formatDate(fb.created_at)
                }));
                setFeedbackList(formattedFeedback);
            }
        } catch (err) {
            console.error('Failed to fetch feedback:', err);
        }
    };

    // Real Text Analysis API Call
    const performTextAnalysis = async (text) => {
        try {
            const response = await fetch(`${API_BASE_URL}/analysis/text/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: text,
                    analysis_type: 'comprehensive'
                }),
            });

            if (response.ok) {
                const result = await response.json();
                return {
                    isAI: result.ai_confidence > 50,
                    confidence: result.ai_confidence,
                    highlightedText: result.highlighted_content || text,
                    detectionReasons: result.detection_reasons || [],
                    statistics: result.analysis_statistics || {},
                    analysisDetails: result.analysis_details || {},
                    submissionId: result.submission_id
                };
            } else {
                throw new Error('Analysis failed');
            }
        } catch (err) {
            console.error('Text analysis error:', err);
            throw err;
        }
    };

    // Real Image Analysis API Call
    const performImageAnalysis = async (imageFile) => {
        try {
            const formData = new FormData();
            formData.append('image', imageFile);
            formData.append('analysis_type', 'comprehensive');

            const response = await fetch(`${API_BASE_URL}/analysis/image/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                return {
                    isAI: result.ai_confidence > 50,
                    confidence: result.ai_confidence,
                    highlightedText: '',
                    filename: imageFile.name,
                    isImage: true,
                    submissionId: result.submission_id,
                    analysisDetails: result.analysis_details || {}
                };
            } else {
                throw new Error('Image analysis failed');
            }
        } catch (err) {
            console.error('Image analysis error:', err);
            throw err;
        }
    };

    // Updated Analysis Handlers
    const handleTextAnalysis = async () => {
        if (!textContent.trim()) return;

        setIsAnalyzing(true);
        try {
            const result = await performTextAnalysis(textContent);
            setAnalysisResult(result);
            // Refresh submissions after new analysis
            fetchUserSubmissions();
        } catch (err) {
            setError('Analysis failed. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const fileType = file.type;
        const fileName = file.name.toLowerCase();

        if (activeDetectionType === 'text') {
            if (!fileType.includes('pdf')) {
                alert('Please upload only PDF files for text analysis.');
                return;
            }

            setIsAnalyzing(true);
            try {
                // Extract text from PDF
                const reader = new FileReader();
                reader.onload = async function () {
                    const typedArray = new Uint8Array(this.result);
                    const pdf = await pdfjsLib.getDocument(typedArray).promise;
                    let fullText = "";

                    for (let i = 1; i <= pdf.numPages; i++) {
                        const page = await pdf.getPage(i);
                        const textContent = await page.getTextContent();
                        fullText += textContent.items.map((item) => item.str).join(" ") + "\n";
                    }

                    // Analyze extracted text
                    try {
                        const result = await performTextAnalysis(fullText);
                        setAnalysisResult({ ...result, filename: file.name });
                        fetchUserSubmissions();
                    } catch (err) {
                        setError('PDF analysis failed. Please try again.');
                    } finally {
                        setIsAnalyzing(false);
                    }
                };
                reader.readAsArrayBuffer(file);
            } catch (err) {
                setError('Failed to read PDF file.');
                setIsAnalyzing(false);
            }
        }
    };

    const handleImageUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const fileType = file.type;
        if (!fileType.includes('image')) {
            alert('Please upload only PNG or JPEG images.');
            return;
        }

        const reader = new FileReader();
        reader.onload = async (e) => {
            setUploadedImage(e.target?.result);
            setIsAnalyzing(true);
            
            try {
                const result = await performImageAnalysis(file);
                setAnalysisResult(result);
                fetchUserSubmissions();
            } catch (err) {
                setError('Image analysis failed. Please try again.');
            } finally {
                setIsAnalyzing(false);
            }
        };
        reader.readAsDataURL(file);
    };

    // Submit Feedback to API
    const submitFeedback = async () => {
        if (!feedbackText.trim() || !analysisResult) return;

        try {
            const response = await fetch(`${API_BASE_URL}/feedback/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    submission_id: analysisResult.submissionId,
                    feedback_text: feedbackText,
                    rating: 1 // thumbs down
                }),
            });

            if (response.ok) {
                setFeedbackText('');
                setShowFeedback(false);
                fetchUserFeedback(); // Refresh feedback list
                alert('Thank you for your feedback!');
            } else {
                throw new Error('Failed to submit feedback');
            }
        } catch (err) {
            console.error('Feedback submission error:', err);
            alert('Failed to submit feedback. Please try again.');
        }
    };

    // Download Report from API
    const downloadReport = async (submissionId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/reports/analysis/${submissionId}/download/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `analysis-report-${submissionId}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                throw new Error('Download failed');
            }
        } catch (err) {
            console.error('Download error:', err);
            alert('Failed to download report. Please try again.');
        }
    };

    // Email Report via API
    const emailReport = async (submissionId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/reports/analysis/${submissionId}/email/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipient_email: currentUser?.email
                }),
            });

            if (response.ok) {
                alert('Report sent to your email!');
            } else {
                throw new Error('Email failed');
            }
        } catch (err) {
            console.error('Email error:', err);
            alert('Failed to send email. Please try again.');
        }
    };

    // Delete Submission
    const deleteHistoryItem = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/submissions/${id}/delete/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
            });

            if (response.ok) {
                setHistoryItems(prev => prev.filter(item => item.id !== id));
            } else {
                throw new Error('Delete failed');
            }
        } catch (err) {
            console.error('Delete error:', err);
            alert('Failed to delete item. Please try again.');
        }
    };

    // Utility Functions
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);

        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        return date.toLocaleDateString();
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const saveToHistory = () => {
        // This is now handled automatically by the API when analysis is performed
        alert('Results saved to history!');
    };

    const viewHistoryItem = (item) => {
        setSelectedHistoryItem(item);
        setCurrentView('history-detail');
    };

    const resetAnalysis = () => {
        setAnalysisResult(null);
        setTextContent('');
        setUploadedImage(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
        if (imageInputRef.current) imageInputRef.current.value = '';
    };

    const handleThumbsDown = () => {
        setShowFeedback(true);
    };

    const exportReportAsPDF = () => {
        if (analysisResult?.submissionId) {
            downloadReport(analysisResult.submissionId);
        } else {
            alert('No submission ID available for download');
        }
    };

    const exportResults = (format) => {
        if (format === 'email' && analysisResult?.submissionId) {
            emailReport(analysisResult.submissionId);
        } else {
            alert(`${format} export not available`);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className="detective-container">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <div className="loading-text">Loading Detective AI...</div>
                </div>
            </div>
        );
    }

    // Error state
    if (error && !historyItems.length) {
        return (
            <div className="detective-container">
                <div className="error-container">
                    <AlertTriangle className="icon-lg" />
                    <div className="error-text">{error}</div>
                    <button className="retry-button" onClick={loadInitialData}>
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    // Your existing component JSX remains the same from here...
    // Just replace the mock functions with the real API calls above
    
    const detectionOptions = [
        {
            id: 'text',
            title: 'Text Detection',
            description: 'Analyze text content for AI-generated patterns and signatures.',
            icon: <FileText className="icon-lg"/>
        },
        {
            id: 'image',
            title: 'Image Detection',
            description: 'Detect AI-generated images using advanced visual analysis',
            icon: <ImageIcon className="icon-lg"/>
        }
    ];

    const navigationItems = [
        {id: 'detector', label: 'Detector', icon: <Search className="icon-sm"/>, active: true},
        {id: 'team', label: 'Team', icon: <Users className="icon-sm"/>},
        {id: 'demo', label: 'Demo', icon: <Play className="icon-sm"/>}
    ];

    // Analysis Report Component remains the same
    const AnalysisReport = ({ result }) => (
        <div className="analysis-report">
            <div className="report-header">
                <div className="report-icon">
                    <FileCheck className="icon-md" style={{ color: '#ffffff' }} />
                </div>
                <div>
                    <h3 className="report-title">Detailed Analysis Report</h3>
                    <p className="report-subtitle">Comprehensive breakdown of detection methodology</p>
                </div>
            </div>

            {/* Statistics Overview */}
            <div className="report-section">
                <div className="section-header">
                    <TrendingUp className="icon-sm" />
                    <h4 className="section-title">Content Statistics</h4>
                </div>
                <div className="stats-grid">
                    <div className="stat-item">
                        <span className="stat-label">Total Words</span>
                        <span className="stat-value">{result.statistics?.totalWords || 'N/A'}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Sentences</span>
                        <span className="stat-value">{result.statistics?.sentences || 'N/A'}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Confidence</span>
                        <span className="stat-value">{result.confidence}%</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">AI Indicators</span>
                        <span className="stat-value">{result.detectionReasons?.length || 0}</span>
                    </div>
                </div>
            </div>

            {/* Detection Factors */}
            {result.detectionReasons && result.detectionReasons.length > 0 && (
                <div className="report-section">
                    <div className="section-header">
                        <Brain className="icon-sm" />
                        <h4 className="section-title">Detection Factors</h4>
                    </div>
                    <div className="factors-list">
                        {result.detectionReasons.map((reason, index) => (
                            <div key={index} className={`factor-item factor-${reason.type || 'info'}`}>
                                <div className="factor-header">
                                    <div className={`factor-icon ${reason.type || 'info'}`}>
                                        {reason.type === 'critical' && <AlertTriangle className="icon-xs" />}
                                        {reason.type === 'warning' && <AlertCircle className="icon-xs" />}
                                        {reason.type === 'info' && <Info className="icon-xs" />}
                                        {reason.type === 'success' && <CheckCircle className="icon-xs" />}
                                        {!reason.type && <Info className="icon-xs" />}
                                    </div>
                                    <div className="factor-title">{reason.title || reason.reason}</div>
                                    <div className={`factor-impact impact-${(reason.impact || 'medium').toLowerCase()}`}>
                                        {reason.impact || 'Medium'} Impact
                                    </div>
                                </div>
                                <div className="factor-description">{reason.description || reason.details}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Confidence Breakdown */}
            <div className="report-section">
                <div className="section-header">
                    <Shield className="icon-sm" />
                    <h4 className="section-title">Confidence Analysis</h4>
                </div>
                <div className="confidence-breakdown">
                    <div className="confidence-bar">
                        <div 
                            className={`confidence-fill ${result.isAI ? 'ai-detected' : 'human-written'}`}
                            style={{ width: `${result.confidence}%` }}
                        ></div>
                    </div>
                    <div className="confidence-labels">
                        <span className="confidence-label">0%</span>
                        <span className="confidence-label">50%</span>
                        <span className="confidence-label">100%</span>
                    </div>
                    <p className="confidence-explanation">
                        {result.isAI 
                            ? `This content shows ${result.confidence}% likelihood of being AI-generated.`
                            : `This content shows ${result.confidence}% likelihood of being human-written.`
                        }
                    </p>
                </div>
            </div>
        </div>
    );

    // Rest of your JSX remains exactly the same, just with the API integration above
    return (
        <div className="detective-container">
            

            {/*sidebar*/}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <div className="sidebar-logo-icon">
                            {/*<Search className="icon-sm text-white"/>*/}
                            <img src={Logo} alt="Detective AI Logo" className="logo-img"/>
                        </div>
                        <span className="sidebar-title">Detective AI</span>
                    </div>
                    <button className="close-sidebar" onClick={toggleSidebar}>
                        <Menu className="icon-sm"/>
                    </button>
                </div>

                {/*new detection button*/}
                <button className="new-detection" onClick={() => {
                    setCurrentView('main');
                    setActiveDetectionType('text');
                    setInputMode('type');
                    resetAnalysis();
                    setShowFeedback(false);
                    setSelectedHistoryItem(null);
                }}>
                    <Plus className="icon-sm"/>
                    <span>New Detection</span>
                </button>

                {/*navigation */}
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
                                <ChevronRight className="icon-xs" style={{ marginLeft: 'auto'}}/>
                            
                            </RouterLink>
                        ))}
                    </div>

                    {/*history section*/}
                    <div className="nav-section history-section">
                        <div className="nav-section-title">Recent Detections</div>
                        {historyItems.map((item) => (
                            <div key={item.id} className="history-item">
                                <div className="history-content" onClick={() => viewHistoryItem(item)}>
                                    {item.type === 'text' ?
                                        <FileText className="icon-xs"/> :
                                        <ImageIcon className="icon-xs"/>
                                    }
                                    <div>
                                        <div className="history-text">{item.title}</div>
                                        <div style={{fontSize: '0.75rem', color: '#6b7280'}}>
                                            {item.date}
                                        </div>
                                    </div>
                                </div>
                                <div className="history-actions">
                                    <button className="history-action">
                                        <Share className="icon-xs"/>
                                    </button>
                                    <button
                                        className="history-action"
                                        onClick={() => deleteHistoryItem(item.id)}
                                    >
                                        <Trash2 className="icon-xs"/>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </nav>
            </div>

            {/*sidebar overlay */}
            <div
                className={`sidebar-overlay ${sidebarOpen ? 'active' : ''}`}
                onClick={toggleSidebar}
            />

            {/*header*/}
            <header className={`detective-header ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="detective-header-inner">

                    <div className="header-left"></div>
                        {/*Menu toggle button*/}
                        <button
                            className={`menu-toggle ${sidebarOpen ? 'sidebar-open' : ''}`}
                            onClick={toggleSidebar}
                        >
                            <Menu className="icon-sm"/>
                        </button>

                        {/*logo*/}
                        <div className="detective-logo">
                            <div className="detective-logo-icon">
                                {/*<Search className="icon-md text-white"/>*/}
                                <img src={Logo} alt="Detective AI Logo" className="logo-img"/>
                                
                            </div>
                            <div>
                                <h1 className="detective-title">Detective AI</h1>
                                <p className="detective-subtitle">Content Detection</p>
                            </div>
                        </div>
                    {/*Sign in button*/}
                    {/*<button className="btn-signin">
                        <span>Sign In</span>
                        <ChevronRight className="icon-sm"/>
                    </button>*/}
                </div>
            </header>

            {/*main content*/}
            <main className={`detective-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="content-area">
                    {currentView === 'main' ? (
                        <>
                            {/* Main Detection Interface */}
                            <div className="detection-interface">
                                <div className="interface-header">
                                    <h1 className="interface-title">AI Content Detection</h1>
                                    <p className="interface-subtitle">
                                        Upload your content for instant AI detection analysis
                                    </p>
                                </div>

                                {/*quick stats*/}
                                <div className="stats-dashboard">
                                    {recentStats.map((stat, index) => (
                                        <div key={index} className="stat-card-mini">
                                            <div className="stat-value">{stat.value}</div>
                                            <div className="stat-label">{stat.label}</div>
                                            <div style={{ 
                                                fontSize: '0.75rem', 
                                                color: stat.change.startsWith('+') ? '#10b981' : '#ef4444',
                                                marginTop: '0.5rem'
                                            }}>
                                                {stat.change}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Detection Type Options */}
                                <div className="detection-options">
                                    {detectionOptions.map((option) => (
                                        <div
                                            key={option.id}
                                            className={`detection-card ${activeDetectionType === option.id ? 'active' : ''}`}
                                            onClick={() => {
                                                setActiveDetectionType(option.id);
                                                resetAnalysis();
                                            }}
                                        >
                                            <div className="card-icon">
                                                {option.icon}
                                            </div>
                                            <h3 className="card-title">{option.title}</h3>
                                            <p className="card-description">{option.description}</p>
                                        </div>
                                    ))}
                                </div>

                                {/* Text Input Area */}
                                {activeDetectionType === 'text' && (
                                    <div className="text-input-area">
                                        <div className="input-toggle">
                                            <button 
                                                className={`toggle-btn ${inputMode === 'type' ? 'active' : ''}`}
                                                onClick={() => {
                                                    setInputMode('type');
                                                    resetAnalysis();
                                                }}
                                            >
                                                <Type className="icon-sm" />
                                                Type Text
                                            </button>
                                            <button 
                                                className={`toggle-btn ${inputMode === 'upload' ? 'active' : ''}`}
                                                onClick={() => {
                                                    setInputMode('upload');
                                                    resetAnalysis();
                                                }}
                                            >
                                                <FileUp className="icon-sm" />
                                                Upload Document
                                            </button>
                                        </div>

                                        {inputMode === 'type' ? (
                                            <>
                                                <textarea
                                                    className="text-area"
                                                    placeholder="Paste or type your text here for AI detection analysis..."
                                                    value={textContent}
                                                    onChange={(e) => setTextContent(e.target.value)}
                                                />
                                                <button 
                                                    className="analyze-button"
                                                    onClick={handleTextAnalysis}
                                                    disabled={!textContent.trim() || isAnalyzing}
                                                >
                                                    {isAnalyzing ? (
                                                        <>
                                                            <Loader className="icon-sm animate-spin" />
                                                            Analyzing...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Eye className="icon-sm" />
                                                            Analyze Text
                                                        </>
                                                    )}
                                                </button>
                                            </>
                                        ) : (
                                            <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
                                                <div className="upload-icon">
                                                    <FileText className="icon-lg" />
                                                </div>
                                                <h3 className="upload-title">Upload Document</h3>
                                                <p className="upload-description">
                                                    Click here or drag and drop PDF or DOCX files (up to 25MB)
                                                </p>
                                                <button className="upload-button">
                                                    <Upload className="icon-sm" />
                                                    Choose Document
                                                </button>
                                                <input
                                                    ref={fileInputRef}
                                                    type="file"
                                                    className="file-input"
                                                    accept=".pdf,.docx"
                                                    onChange={handleFileUpload}
                                                />
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Image Upload Area */}
                                {activeDetectionType === 'image' && (
                                    <div className="upload-area" onClick={() => imageInputRef.current?.click()}>
                                        <div className="upload-icon">
                                            <ImageIcon className="icon-lg" />
                                        </div>
                                        <h3 className="upload-title">Upload Image</h3>
                                        <p className="upload-description">
                                            Click here or drag and drop PNG or JPEG images (up to 10MB)
                                        </p>
                                        <button className="upload-button">
                                            <Upload className="icon-sm" />
                                            Choose Image
                                        </button>
                                        <input
                                            ref={imageInputRef}
                                            type="file"
                                            className="file-input"
                                            accept=".png,.jpg,.jpeg"
                                            onChange={handleImageUpload}
                                        />
                                    </div>
                                )}

                                {/* Loading State */}
                                {isAnalyzing && (
                                    <div className="loading-container">
                                        <div className="loading-spinner"></div>
                                        <div className="loading-text">
                                            {activeDetectionType === 'text' ? 'Analyzing text patterns...' : 'Processing image...'}
                                        </div>
                                    </div>
                                )}

                                {/* Results */}
                                {analysisResult && !isAnalyzing && (
                                    <div className="results-container">
                                        {analysisResult.isImage ? (
                                            // Image Results
                                            <div className="image-result">
                                                <div className="results-header">
                                                    <div className="detection-result">
                                                        <div className={`result-icon ${analysisResult.isAI ? 'ai-detected' : 'human-written'}`}>
                                                            {analysisResult.isAI ? <AlertCircle className="icon-md text-white" /> : <CheckCircle className="icon-md text-white" />}
                                                        </div>
                                                        <div>
                                                            <div className={`result-status ${analysisResult.isAI ? 'ai-detected' : 'human-written'}`}>
                                                                {analysisResult.isAI ? 'AI Generated' : 'Likely Human'}
                                                            </div>
                                                            <div className="result-confidence">
                                                                Confidence: {analysisResult.confidence}%
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                                {uploadedImage && (
                                                    <img src={uploadedImage} alt="Uploaded" className="result-image" />
                                                )}
                                                
                                                <div className="image-analysis">
                                                    <p style={{ color: '#d1d5db', marginBottom: '1rem' }}>
                                                        Analysis Complete: {analysisResult.filename}
                                                    </p>
                                                    <p style={{ color: '#9ca3af' }}>
                                                        {analysisResult.isAI ? 
                                                            'Our AI detection algorithms have identified patterns consistent with machine-generated imagery.' :
                                                            'The image appears to be authentic with natural characteristics typical of human-created content.'
                                                        }
                                                    </p>
                                                </div>
                                            </div>
                                        ) : (
                                            // Text Results
                                            <>
                                                <div className="results-header">
                                                    <div className="detection-result">
                                                        <div className={`result-icon ${analysisResult.isAI ? 'ai-detected' : 'human-written'}`}>
                                                            {analysisResult.isAI ? <AlertCircle className="icon-md text-white" /> : <CheckCircle className="icon-md text-white" />}
                                                        </div>
                                                        <div>
                                                            <div className={`result-status ${analysisResult.isAI ? 'ai-detected' : 'human-written'}`}>
                                                                {analysisResult.isAI ? 'AI Generated Content Detected' : 'Likely Human Written'}
                                                            </div>
                                                            <div className="result-confidence">
                                                                Confidence: {analysisResult.confidence}%
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div className="results-actions">
                                                        <button className="action-btn export" onClick={exportReportAsPDF}>
                                                            <Download className="icon-sm" />
                                                            Export PDF
                                                        </button>
                                                        <button className="action-btn" onClick={() => exportResults('email')}>
                                                            <Mail className="icon-sm" />
                                                            Email
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Enhanced Analysis Report */}
                                                <div ref={reportRef}>
                                                    <AnalysisReport result={analysisResult} />
                                                </div>

                                                <div className="analyzed-text" dangerouslySetInnerHTML={{ __html: analysisResult.highlightedText }} />

                                                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
                                                    <button 
                                                        className="action-btn" 
                                                        onClick={() => {
                                                            saveToHistory();
                                                            alert('Results saved to history!');
                                                        }}
                                                        style={{ background: 'linear-gradient(135deg, #10b981, #059669)', color: 'white' }}
                                                    >
                                                        <ThumbsUp className="icon-sm" />
                                                        Accurate
                                                    </button>
                                                    <button className="action-btn" onClick={handleThumbsDown}>
                                                        <ThumbsDown className="icon-sm" />
                                                        Not Accurate
                                                    </button>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )}

                                {/* Recent Activity */}
                                <div className="recent-activity">
                                    <div className="activity-header">
                                        <div className="activity-icon">
                                            <Activity className="icon-md text-white" />
                                        </div>
                                        <h3 className="activity-title">Recent Activity</h3>
                                    </div>
                                    <div className="activity-list">
                                        {recentActivity.map((activity) => (
                                            <div key={activity.id} className="activity-item">
                                                <div className="activity-item-icon">
                                                    {activity.type === 'text' ? 
                                                        <FileText className="icon-sm text-white" /> :
                                                        <ImageIcon className="icon-sm text-white" />
                                                    }
                                                </div>
                                                <div className="activity-item-content">
                                                    <div className="activity-item-title">{activity.title}</div>
                                                    <div className="activity-item-time">{activity.time}</div>
                                                </div>
                                                <div className={`activity-item-status status-${activity.status}`}>
                                                    {activity.status === 'success' && <CheckCircle className="icon-xs" />}
                                                    {activity.status === 'processing' && <Clock className="icon-xs" />}
                                                    {activity.status === 'warning' && <AlertTriangle className="icon-xs" />}
                                                    <span style={{ marginLeft: '0.25rem', textTransform: 'capitalize' }}>
                                                        {activity.status}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Feedback List (Admin View for Prototype) */}
                                {feedbackList.length > 0 && (
                                    <div className="feedback-list">
                                        <h3 style={{ marginBottom: '1.5rem', color: '#d1d5db' }}>User Feedback (Admin View)</h3>
                                        {feedbackList.map((feedback) => (
                                            <div key={feedback.id} className="feedback-item">
                                                <div className="feedback-header">
                                                    <div className="feedback-query">{feedback.query}</div>
                                                    <div className="feedback-date">{feedback.date}</div>
                                                </div>
                                                <div className="feedback-content">"{feedback.feedback}"</div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </>
                    ) : (
                        // History Detail View
                        <div className="history-detail">
                            <div className="history-detail-header">
                                <h2 className="history-detail-title">{selectedHistoryItem?.title}</h2>
                                <button className="back-button" onClick={() => setCurrentView('main')}>
                                    <ArrowLeft className="icon-sm" />
                                    Back to Main
                                </button>
                            </div>

                            {selectedHistoryItem && (
                                <div className="results-container">
                                    <div className="results-header">
                                        <div className="detection-result">
                                            <div className={`result-icon ${selectedHistoryItem.result.isAI ? 'ai-detected' : 'human-written'}`}>
                                                {selectedHistoryItem.result.isAI ? <AlertCircle className="icon-md text-white" /> : <CheckCircle className="icon-md text-white" />}
                                            </div>
                                            <div>
                                                <div className={`result-status ${selectedHistoryItem.result.isAI ? 'ai-detected' : 'human-written'}`}>
                                                    {selectedHistoryItem.result.isAI ? 'AI Generated Content Detected' : 'Likely Human Written'}
                                                </div>
                                                <div className="result-confidence">
                                                    Confidence: {selectedHistoryItem.result.confidence}%
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="results-actions">
                                            <button className="action-btn export" onClick={exportReportAsPDF}>
                                                <Download className="icon-sm" />
                                                Export PDF
                                            </button>
                                            <button className="action-btn" onClick={() => exportResults('email')}>
                                                <Mail className="icon-sm" />
                                                Email
                                            </button>
                                        </div>
                                    </div>

                                    {/*show analysis report for history items if available */}
                                    {selectedHistoryItem.result.detectionReasons && (
                                        <div ref={reportRef}>
                                            <AnalysisReport result={selectedHistoryItem.result} />
                                        </div>
                                    )}

                                    <div className="analyzed-text" dangerouslySetInnerHTML={{ __html: selectedHistoryItem.result.highlightedText }} />
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </main>

            {/* Feedback Modal */}
            {showFeedback && (
                <div className="modal-overlay">
                    <div className="modal">
                        <div className="modal-header">
                            <h3 className="modal-title">Help Us Improve</h3>
                            <button className="modal-close" onClick={() => setShowFeedback(false)}>
                                <X className="icon-sm" />
                            </button>
                        </div>
                        <p style={{ color: '#9ca3af', marginBottom: '1rem' }}>
                            We're sorry the results weren't accurate. Please let us know what went wrong:
                        </p>
                        <textarea
                            className="feedback-textarea"
                            placeholder="Please describe what was inaccurate about the detection..."
                            value={feedbackText}
                            onChange={(e) => setFeedbackText(e.target.value)}
                        />
                        <div className="modal-actions">
                            <button className="modal-btn cancel" onClick={() => setShowFeedback(false)}>
                                Cancel
                            </button>
                            <button className="modal-btn submit" onClick={submitFeedback}>
                                Submit Feedback
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DetectivePage;