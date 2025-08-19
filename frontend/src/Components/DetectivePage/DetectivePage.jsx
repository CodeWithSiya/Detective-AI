import React, {useState, useRef} from 'react';
import './DetectivePage.css';
import {
    Search,
    Eye,
    X,
    ChevronRight,
    FileText,
    Image as ImageIcon,
    History,
    Users,
    BarChart3,
    Play,
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
    Menu
} from 'lucide-react';

const DetectivePage = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [activeDetectionType, setActiveDetectionType] = useState('text');
    const [inputMode, setInputMode] = useState('type'); //type or upload
    const [textContent, setTextContent] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedbackText, setFeedbackText] = useState('');
    const [currentView, setCurrentView] = useState('main'); // 'main' or 'history-detail'
    const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);
    const [uploadedImage, setUploadedImage] = useState(null);

    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);

    const [historyItems, setHistoryItems] = useState([
        {
            id: 1,
            type:'text',
            title: 'Academic Essay Analysis',
            date: '2 hours ago',
            content: 'The rapid evolution of AI has revolutionized various industries...',
            result: {isAI: true, confidence: 87, highlightedText: 'The rapid advancements of AI has <span class="highlight">revolutionized<span class="tooltip">AI-typical word choice</span></span>various industries and <span class="highlight">transformed<span class="tooltip">Overused transition word</span></span> the way we approach complex problems.'}
        },
        {
            id: 2,
            type:'text',
            title: 'Research Paper Review',
            date: '2 days ago',
            content: 'Climate change represents one of the most pressing challenges of our time...',
            result: {isAI: false, confidence: 92, highlightedText: 'Climate change represents one of the most pressing challenges of our time. The scientific evidence  overwhelmingly supports the conclusion that human activities are the primary driver of recent climate change.'}
        }
    ]);

    const [recentStats] = useState([
        {label: 'Today', value: '24', change: '+12%'},
        {label: 'This Week', value: '156', change: '+8%'},
        {label: 'Accuracy', value: '94.2%', change: '+2.1%'},
        {label: 'Avg Time', value: '8.3s', change: '-1.2s%'},
    ]);

    const [recentActivity] = useState([
        {
            id: 1,
            title: 'Text analysis completed',
            time: '2 minutes ago',
            status: 'success',
            type: 'text'
        },
        {
            id: 2,
            title: 'Image Processing in progress',
            time: '5 minutes ago',
            status: 'processing',
            type: 'image'
        },
        {
            id: 3,
            title: 'Batch analysis completed',
            time: '1 hour ago',
            status: 'success',
            type: 'text'
        }
    ]);

    const [feedbackList, setFeedbackList] = useState([
        {
            id: 1,
            query: 'Academic Essay Analysis',
            feedback: 'The detection seemed inaccurate. The highlighted words appear to be normal academic language.',
            date: '2 hours ago'
        },
        {
            id: 2,
            query: 'Blog Post Detection',
            feedback: 'Great accuracy! The AI detection was spot on and helped me verify the content.',
            date: '1 day ago'
        }
    ]);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    //mock ai detection logic
    const performTextAnalysis = (text) => {
        const aiKeywords = ['revolutionized', 'transformed', 'cutting-edge', 'state-of-the-art', 'innovative', 'delves', 'furthermore', 'moreover', 'additionally'];
        const suspiciousPatterns = ['AI-generated', 'machine learning', 'aritificial intelligence'];

        let isAI = false;
        let confidence = 0;

        //check for ai keywords
        const lowerText = text.toLowerCase();
        const foundKeywords = aiKeywords.filter(keyword => lowerText.includes(keyword));
        const foundPatterns = suspiciousPatterns.filter(pattern => lowerText.includes(pattern.toLowerCase()));

        if (foundKeywords.length > 2 || foundPatterns.length > 0){
            isAI = true;
            confidence = Math.min(95, 60 + (foundKeywords.length * 10) + (foundPatterns.length * 15));
        }
        else{
            confidence = Math.max(75, 90 - (foundKeywords.length * 5));
        }

        //generate highlighted text
        let highlightedText = text;
        [...aiKeywords, ...suspiciousPatterns].forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            highlightedText = highlightedText.replace(regex,
                `<span class="hightlight">${keyword}<span class="tooltip">AI-typical phrase detected</span></span>`
            );
        });
        return {isAI, confidence, highlightedText};
    };

    const performImageAnalysis = (filename) => {
        //mock logic based on filename
        const isAI = filename.toLowerCase().includes('ai') || filename.toLowerCase().includes('generated');
        const confidence = isAI ? Math.floor(Math.random() * 20) + 80 : Math.floor(Math.random() * 20) + 75;

        return {isAI, confidence};
    };

    const handleTextAnalysis = async () => {
        if (!textContent.trim()) return;

        setIsAnalyzing(true);

        //simulate api delay
        setTimeout(() => {
            const result = performTextAnalysis(textContent);
            setAnalysisResult(result);
            setIsAnalyzing(false);
        }, 2000);
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const fileType = file.type;
        const fileName = file.name.toLowerCase();

        if (activeDetectionType === 'text'){
            if (!fileType.includes('pdf') && !fileType.includes('document') && !fileName.endsWith('docx')){
                alert('Please upload only PDF or DOCX files for text analysis.');
                return;
            }

            //mock file reading
            setIsAnalyzing(true);
            setTimeout(() => {
                const mockText = `This is a sample text extracted from ${file.name}. The document contains various paragraphs with potentially AI-generated content that needs to be analyzed for authenticity.`;
                const result = performTextAnalysis(mockText);
                setAnalysisResult({...result, filename: file.name});
                setIsAnalyzing(false);
            }, 3000);
        }
    };

    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const fileType = file.type;

        if (!fileType.includes('image')){
            alert('Please upload only PNG or JPEG images.');
            return;
        }

        if (!fileType.includes('png') && !fileType.includes('jpeg') && !fileType.includes('jpg')){
            alert('Please Upload only PNG or JPEG');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            setUploadedImage(e.target.result);

            setIsAnalyzing(true);
            setTimeout(() => {
                const result = performImageAnalysis(file.name);
                setAnalysisResult({...result, filename: file.name, isImage: true});
                setIsAnalyzing(false);
            }, 2500);
        };
        reader.readAsDataURL(file);
    };

    const handleThumbsDown = () => {
        setShowFeedback(true);
    };

    const submitFeedback = () =>{
        if (!feedbackText.trim()) return;

        const newFeedback = {
            id: Date.now(),
            query: analysisResult?.filename || 'Text Analysis',
            feedback: feedbackText,
            date: 'Just now'
        };

        setFeedbackList(prev => [newFeedback, ...prev]);
        setFeedbackText('');
        setShowFeedback(false);
    };

    const saveToHistory = () => {
        if (!analysisResult || analysisResult.isImage) return;

        const newHistoryItem = {
            id: Date.now(),
            type: 'text',
            title: analysisResult.filename || `Analysis ${new Date().toLocaleTimeString()}`,
            date: 'Just now',
            content: textContent,
            result: analysisResult
        };
        setHistoryItems(prev => [newHistoryItem, ...prev]);
    };

    const viewHistoryItem = (item) => {
        setSelectedHistoryItem(item);
        setCurrentView('history-detail');
    };

    const deleteHistoryItem = (id) => {
        setHistoryItems(prev => prev.filter(item => item.id !== id));
    };

    const exportResults = (format) => {
        if (format === 'pdf'){
            alert('PDF export functionality would be implemented here.');
        }
        else{
            alert('Email export functionality would be implemented here.');
        }
    };

    const resetAnalysis = () => {
        setAnalysisResult(null);
        setTextContent('');
        setUploadedImage(null);
        if (fileInputRef.current){
            fileInputRef.current.value = '';
        }
        if (imageInputRef.current){
            imageInputRef.current.value = '';
        }
    };

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
        {id: 'dashboard', label: 'Dashboard', icon: <BarChart3 className="icon-sm"/>},
        {id: 'demo', label: 'Demo', icon: <Play className="icon-sm"/>}
    ];

    return (
        <div className="detective-container">
            {/*Menu toggle button*/}
            <button
                className={`menu-toggle ${sidebarOpen ? 'sidebar-open' : ''}`}
                onClick={toggleSidebar}
            >
                <Menu className="icon-md"/>
            </button>

            {/*sidebar*/}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <div className="sidebar-logo-icon">
                            <Search className="icon-sm text-white"/>
                        </div>
                        <span className="sidebar-title">Detective AI</span>
                    </div>
                    <button className="close-sidebar" onClick={toggleSidebar}>
                        <X className="icon-sm"/>
                    </button>
                </div>

                {/*new detection button*/}
                <button className="new-detection">
                    <Plus className="icon-sm"/>
                    <span>New Detection</span>
                </button>

                {/*navigation */}
                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">Navigation</div>
                        {navigationItems.map((item) => (
                            <button
                                key={item.id}
                                className={`nav-item ${item.active ? 'active' : ''}`}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                                <ChevronRight className="icon-xs" style={{ marginLeft: 'auto'}}/>
                            </button>
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
                    {/*logo*/}
                    <div className="detective-logo">
                        <div className="detective-logo-icon">
                            <Search className="icon-md text-white"/>
                            <div className="detective-logo-badge">
                                <Eye className="icon-xs text-white"/>
                            </div>
                        </div>
                        <div>
                            <h1 className="detective-title">Detective AI</h1>
                            <p className="detective-subtitle">Content Detection</p>
                        </div>
                    </div>
                    {/*Sign in button*/}
                    <button className="btn-signin">
                        <span>Sign In</span>
                        <ChevronRight className="icon-sm"/>
                    </button>
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
                                                        <button className="action-btn export" onClick={() => exportResults('pdf')}>
                                                            <Download className="icon-sm" />
                                                            Export PDF
                                                        </button>
                                                        <button className="action-btn" onClick={() => exportResults('email')}>
                                                            <Mail className="icon-sm" />
                                                            Email
                                                        </button>
                                                    </div>
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
                                            <button className="action-btn export" onClick={() => exportResults('pdf')}>
                                                <Download className="icon-sm" />
                                                Export PDF
                                            </button>
                                            <button className="action-btn" onClick={() => exportResults('email')}>
                                                <Mail className="icon-sm" />
                                                Email
                                            </button>
                                        </div>
                                    </div>

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