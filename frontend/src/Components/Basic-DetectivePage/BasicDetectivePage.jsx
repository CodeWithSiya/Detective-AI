import React, {useState, useRef} from 'react';
import './BasicDetectivePage.css';
import Logo from "../Assets/Logo.png";
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
    AlertCircle,
    Activity,
    Type,
    FileUp,
    Download,
    Mail,
    ThumbsUp,
    ThumbsDown,
    ArrowLeft,
    Loader,
    Menu,
    Target,
    TrendingUp,
    Brain,
    FileCheck,
    Info
} from 'lucide-react';
import { Link as RouterLink } from "react-router-dom";

const BasicDetectivePage = () => {
    //sidebar and view state
    const [sidebarOpen, setSidebarOpen] = useState(false);

    //text analysis state
    const [textContent, setTextContent] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [uploadedImage, setUploadedImage] = useState(null);

    const WORD_LIMIT = 250;

    //count words in text
    const getWordCoount = () => {
      return textContent.trim() ? textContent.trim().split(/\s+/).length : 0;
    };

    const isOverLimit = () => {
      return getWordCoount() > WORD_LIMIT;
    };

    //sidebar toggle
    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    //------------------------
    //mock AI detection logic
    //-------------------------
    const performTextAnalysis = (text) => {
        const aiKeywords = ['revolutionized', 'transformed', 'cutting-edge', 'state-of-the-art', 'innovative', 'delves', 'leverage', 'optimize', 'facilitate', 'profoundly', 'countless', 'unimaginable', 'accelerated', 'breakthroughs', 'integration', 'thrive', 'competitive', 'environments', 'strategies', 'organizations', 'insights', 'resources', 'evolution', 'algorithms', 'reshaped', 'interaction', 'ecosystems', 'ultimately', 'underscoring', 'innovations'];
        const suspiciousPatterns = ['AI-generated', 'machine learning', 'aritificial intelligence'];
        const transitionWords = ['furthermore', 'moreover', 'additionally', 'consequently', 'therefore', 'nevertheless', 'however'];

        let isAI = false;
        let confidence = 0;
        const detectionReasons = [];

        //check ai keywords
        const lowerText = text.toLowerCase();
        const words = text.split(/\s+/).filter(word => word.length > 0);
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);

        //check for pattern
        const foundPatterns = suspiciousPatterns.filter(pattern => lowerText.includes(pattern.toLowerCase()));
        const foundKeywords = aiKeywords.filter(keyword => lowerText.includes(keyword));
        const foundTransitions = transitionWords.filter(word => lowerText.includes(word));

        //base confidence
        confidence = 50;

        //analysis logic for AI detection
        if (foundPatterns.length > 0) {
            isAI = true;
            confidence += 35;
            detectionReasons.push({
                type: 'critical',
                title: 'Explicit AI References',
                description: `Found ${foundPatterns.length} explicit AI-related phrases: ${foundPatterns.join(', ')}`,
                impact: 'High'
            });
        }

        if (foundKeywords.length >= 3) {
            isAI = true;
            confidence += 20;
            detectionReasons.push({
                type: 'warning',
                title: 'High AI Keyword Density',
                description: `Detected ${foundKeywords.length} AI-typical words`,
                impact: 'High'
            });
        }

        if (foundTransitions.length >= 2) {
            confidence += 15;
            detectionReasons.push({
                type: 'info',
                title: 'Formal Transition Pattern',
                description: `Multiple formal transitions detected: ${foundTransitions.join(', ')}`,
                impact: 'Medium'
            });
        }

        //final determination
        if (confidence >= 60) {
            isAI = true;
        } else {
            isAI = false;
        }

        //ensure confidence is within bounds
        confidence = Math.min(95, Math.max(5, confidence));
        
        //if determined to be human invert confidence
        if (!isAI) {
            confidence = 100 - confidence;
        }

        //generate highlighted text
        let highlightedText = text;

        [...foundKeywords, ...foundPatterns, ...foundTransitions].forEach(keyword => {
            const regex = new RegExp(`\\b${keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, 'gi');
            highlightedText = highlightedText.replace(
                regex,
                `<span class="highlight highlight-keyword">${keyword}</span>`
            );
        });

        return {
            isAI,
            confidence,
            highlightedText,
            detectionReasons,
            statistics:{
                totalWords: words.length,
                sentences: sentences.length,
                avgSentenceLength: sentences.length > 0 ? words.length / sentences.length : 0
            }
        };
    };

    //---------------------------
    //handlers for user actions
    //--------------------------
    const handleTextAnalysis = async () => {
        if (!textContent.trim() || isOverLimit()) return;

        setIsAnalyzing(true);

        setTimeout(() => {
            const result = performTextAnalysis(textContent);
            setAnalysisResult(result);
            setIsAnalyzing(false);
        }, 2000);   //simulate api delay
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

    // Analysis Report Component
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
                        <span className="stat-value">{result.statistics?.totalWords}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Sentences</span>
                        <span className="stat-value">{result.statistics?.sentences}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Avg Sentence Length</span>
                        <span className="stat-value">{result.statistics?.avgSentenceLength.toFixed(1)} words</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">AI Indicators</span>
                        <span className="stat-value">{(result.statistics?.aiKeywordsCount || 0) + (result.statistics?.suspiciousPatternsCount || 0)}</span>
                    </div>
                </div>
            </div>

            {/* Detection Factors */}
            <div className="report-section">
                <div className="section-header">
                    <Brain className="icon-sm" />
                    <h4 className="section-title">Detection Factors</h4>
                </div>
                <div className="factors-list">
                    {result.detectionReasons?.map((reason, index) => (
                        <div key={index} className={`factor-item factor-${reason.type}`}>
                            <div className="factor-header">
                                <div className={`factor-icon ${reason.type}`}>
                                    {reason.type === 'critical' && <AlertTriangle className="icon-xs" />}
                                    {reason.type === 'warning' && <AlertCircle className="icon-xs" />}
                                    {reason.type === 'info' && <Info className="icon-xs" />}
                                    {reason.type === 'success' && <CheckCircle className="icon-xs" />}
                                </div>
                                <div className="factor-title">{reason.title}</div>
                                <div className={`factor-impact impact-${reason.impact.toLowerCase()}`}>
                                    {reason.impact} Impact
                                </div>
                            </div>
                            <div className="factor-description">{reason.description}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Pattern Analysis */}
            <div className="report-section">
                <div className="section-header">
                    <Target className="icon-sm" />
                    <h4 className="section-title">Pattern Analysis</h4>
                </div>
                <div className="pattern-grid">
                    <div className="pattern-category">
                        <h5 className="pattern-title">Transition Words</h5>
                        <div className="pattern-count">{result.statistics?.transitionWordsCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails?.foundTransitions.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {(result.analysisDetails?.foundTransitions.length || 0) > 3 && (
                                <span className="pattern-more">+{(result.analysisDetails?.foundTransitions.length || 0) - 3}</span>
                            )}
                        </div>
                    </div>
                    
                    <div className="pattern-category">
                        <h5 className="pattern-title">Corporate Jargon</h5>
                        <div className="pattern-count">{result.statistics?.corporateJargonCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails?.foundJargon.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {(result.analysisDetails?.foundJargon.length || 0) > 3 && (
                                <span className="pattern-more">+{(result.analysisDetails?.foundJargon.length || 0) - 3}</span>
                            )}
                        </div>
                    </div>

                    <div className="pattern-category">
                        <h5 className="pattern-title">Buzzwords</h5>
                        <div className="pattern-count">{result.statistics?.buzzwordsCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails?.foundBuzzwords.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {(result.analysisDetails?.foundBuzzwords.length || 0) > 3 && (
                                <span className="pattern-more">+{(result.analysisDetails?.foundBuzzwords.length || 0) - 3}</span>
                            )}
                        </div>
                    </div>

                    <div className="pattern-category">
                        <h5 className="pattern-title">AI Patterns</h5>
                        <div className="pattern-count">{result.statistics?.suspiciousPatternsCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails?.foundPatterns.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {(result.analysisDetails?.foundPatterns.length || 0) > 3 && (
                                <span className="pattern-more">+{(result.analysisDetails?.foundPatterns.length || 0) - 3}</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/*Confidence Breakdown */}
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
                            ? `This content shows ${result.confidence}% likelihood of being AI-generated based on ${result.detectionReasons?.length} detection factors.`
                            : `This content shows ${result.confidence}% likelihood of being human-written with natural language patterns.`
                        }
                    </p>
                </div>
            </div>
        </div>
    );

    //detection type cards and sidebar navigation
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

    return (
        <div className="detective-container">
            {/*Menu toggle button*/}
            <button
                className={`menu-toggle ${sidebarOpen ? 'sidebar-open' : ''}`}
                onClick={toggleSidebar}
            >
                <Menu className="icon-sm"/>
            </button>

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

                                                {/* Enhanced Analysis Report */}
                                                <AnalysisReport result={analysisResult} />

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

                                    {/*show analysis report for history items if available */}
                                    {selectedHistoryItem.result.detectionReasons && (
                                        <AnalysisReport result={selectedHistoryItem.result} />
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
export default BasicDetectivePage;