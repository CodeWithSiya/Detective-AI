import React, {useState, useEffect } from 'react';
import './DetectiveBasic.css';
import Logo from "../../assets/images/Logo.png";
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
    Info,
    Home
} from 'lucide-react';
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { isAuthenticated } from '../UserAuthentication/AuthHandler';

const DetectiveBasic = () => {
    // API Configuration.
    const API_BASE_URL = 'http://127.0.0.1:8000';
    const navigate = useNavigate();

    // Get authentication data.
    const isUserAuthenticated = isAuthenticated();

    // Redirect to detective page if authenticated.
    useEffect(() => {
        if (isUserAuthenticated) {
            navigate('/detective', { replace: true });
            return;
        }
    }, [isUserAuthenticated, navigate]);

    //sidebar and view state
    const [sidebarOpen, setSidebarOpen] = useState(false);

    //text analysis state
    const [textContent, setTextContent] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [showTooltip, setShowTooltip] = useState(null);

    const CHARACTER_LIMIT = 250;

    //count characters in text
    const getCharacterCount = () => {
      return textContent.length;
    };

    const isOverLimit = () => {
      return getCharacterCount() > CHARACTER_LIMIT;
    };

    //sidebar toggle
    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const performTextAnalysis = async (text) => {
        try {
            // Check if user is authenticated.
            const token = localStorage.getItem('token');
            const headers = {
                'Content-Type': 'application/json',
            };

            // Add authorization header if user is authenticated.
            if (token) {
                headers['Authorization'] = `Token ${token}`;
            }

            // Fetch data from the API.
            const response = await fetch(`${API_BASE_URL}/api/analysis/text/`, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    text: text,
                }),
            });

            // Check if the response is okay.
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Analysis failed');
            }

            // Fetches data from the API response.
            const data = await response.json();

            // Generate highlighted text from API data.
            const highlightedText = generateHighlightedText(
                text,
                data.data.analysis_result.analysis.analysis_details
            );

            // Extract data from the response structure.
            const analysisData = data.data.analysis_result;
            const prediction = analysisData.prediction;
            const analysis = analysisData.analysis;
            const statistics = analysisData.statistics;
            const analysisDetails = analysis.analysis_details;
            const submission = data.data.submission; // This might be undefined

            return {
                isAI: prediction.is_ai_generated,
                confidence: Math.round(prediction.confidence * 100),
                highlightedText: highlightedText,
                detectionReasons: analysis.detection_reasons || [],
                statistics: {
                    totalWords: statistics.total_words,
                    sentences: statistics.sentences,
                    avgSentenceLength: statistics.avg_sentence_length,
                    aiKeywordsCount: statistics.ai_keywords_count,
                    transitionWordsCount: statistics.transition_words_count,
                    corporateJargonCount: statistics.corporate_jargon_count,
                    buzzwordsCount: statistics.buzzwords_count,
                    suspiciousPatternsCount: statistics.suspicious_patterns_count,
                    humanIndicatorsCount: statistics.human_indicators_count,
                },
                analysisDetails: {
                    foundKeywords: analysisDetails.found_keywords,
                    foundPatterns: analysisDetails.found_patterns,
                    foundTransitions: analysisDetails.found_transitions,
                    foundJargon: analysisDetails.found_jargon,
                    foundBuzzwords: analysisDetails.found_buzzwords,
                    foundHumanIndicators: analysisDetails.found_human_indicators,
                },
                analysisId: data.data.analysis_result.analysis_id,
                // Only include submission if it exists in the response
                submission: submission ? {
                    submissionId: submission.id,
                    submissionName: submission.name,
                } : null,
            };
        } catch (error) {
            console.error('Analysis failed:', error);
            throw error;
        }
    };

        const generateHighlightedText = (originalText, analysisDetails) => {
        if (!analysisDetails) return originalText;
        
        let highlightedText = originalText;
        const highlights = [];
        
        // Collect all found items with their types
        if (analysisDetails.found_keywords?.length > 0) {
            analysisDetails.found_keywords.forEach(keyword => {
                highlights.push({
                    text: keyword,
                    type: 'keyword',
                    tooltip: 'AI-typical keyword detected'
                });
            });
        }
        
        if (analysisDetails.found_patterns?.length > 0) {
            analysisDetails.found_patterns.forEach(pattern => {
                highlights.push({
                    text: pattern,
                    type: 'suspicious',
                    tooltip: 'Suspicious AI pattern detected'
                });
            });
        }
        
        if (analysisDetails.found_transitions?.length > 0) {
            analysisDetails.found_transitions.forEach(transition => {
                highlights.push({
                    text: transition,
                    type: 'transition',
                    tooltip: 'Overused transition word'
                });
            });
        }
        
        if (analysisDetails.found_jargon?.length > 0) {
            analysisDetails.found_jargon.forEach(jargon => {
                highlights.push({
                    text: jargon,
                    type: 'jargon',
                    tooltip: 'Corporate jargon flagged by detectors'
                });
            });
        }
        
        if (analysisDetails.found_buzzwords?.length > 0) {
            analysisDetails.found_buzzwords.forEach(buzzword => {
                highlights.push({
                    text: buzzword,
                    type: 'buzzword',
                    tooltip: 'Buzzword frequently used by AI'
                });
            });
        }
        
        if (analysisDetails.found_human_indicators?.length > 0) {
            analysisDetails.found_human_indicators.forEach(indicator => {
                highlights.push({
                    text: indicator,
                    type: 'human',
                    tooltip: 'Human writing indicator'
                });
            });
        }
        
        // Apply highlights to text with staggered tooltip positioning
        highlights.forEach((highlight, index) => {
            // Escape special regex characters but preserve the original text case
            const escapedText = highlight.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            
            // Use global flag and case-insensitive, but capture the actual matched text
            const regex = new RegExp(`\\b(${escapedText})\\b`, 'gi');
            
            // Calculate tooltip offset class to prevent overlap
            const offsetClass = `tooltip-offset-${index % 4}`;
            
            highlightedText = highlightedText.replace(regex, (match) => {
                return `<span class="highlight highlight-${highlight.type}">${match}<span class="tooltip ${offsetClass}">${highlight.tooltip}</span></span>`;
            });
        });
        
        return highlightedText;
    };

    //---------------------------
    //handlers for user actions
    //--------------------------
    const handleTextAnalysis = async () => {
        if (!textContent.trim() || isOverLimit()) return;

        setIsAnalyzing(true);

        try {
            const result = await performTextAnalysis(textContent);
            setAnalysisResult(result);
        } catch (error) {
            console.error('Text analysis failed:', error);
            alert('Analysis failed. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    //disabled feature handlers
    const handleDisabledFeature = (feature) => {
        setShowTooltip(feature);
        setTimeout(() => setShowTooltip(null), 2000);
    };

    // Basic Analysis Report Component
    const BasicAnalysisReport = ({ result }) => (
        <div className="analysis-report">
            <div className="report-header">
                <div className="report-icon">
                    <FileCheck className="icon-md" style={{ color: '#ffffff' }} />
                </div>
                <div>
                    <h3 className="report-title">Basic Analysis Report</h3>
                    <p className="report-subtitle">Limited analysis for non-registered users</p>
                </div>
            </div>

            {/* Basic Statistics*/}
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
                </div>
            </div>

            {/* Detection Factors */}
            <div className="report-section">
                <div className="section-header">
                    <Brain className="icon-sm" />
                    <h4 className="section-title">Key Detection Factors</h4>
                </div>
                <div className="factors-list">
                    {result.detectionReasons?.slice(0, 3).map((reason, index) => (
                        <div key={index} className={`factor-item factor-${reason.type}`}>
                            <div className="factor-header">
                                <div className={`factor-icon ${reason.type}`}>
                                    {reason.type === 'critical' && <AlertTriangle className="icon-xs" />}
                                    {reason.type === 'warning' && <AlertCircle className="icon-xs" />}
                                    {reason.type === 'info' && <Info className="icon-xs" />}
                                </div>
                                <div className="factor-title">{reason.title}</div>
                                <div className={`factor-impact impact-${reason.impact.toLowerCase()}`}>
                                    {reason.impact} Impact
                                </div>
                            </div>
                            <div className="factor-description">{reason.description}</div>
                        </div>
                    ))}
                    {result.detectionReasons?.length > 3 && (
                        <div className="upgrade-notice">
                          <div className="upgrade-text">
                            <Shield className="icon-sm" />
                            Sign in to see {result.detectionReasons.length - 3} more detection factors and advanced analysis
                          </div>
                        </div>
                    )}
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
                            ? `This content shows ${result.confidence}% likelihood of being AI-generated.`
                            : `This content shows ${result.confidence}% likelihood of being human-written.`
                        }
                    </p>
                </div>
            </div>
        </div>
    );

    const navigationItems = [
        {id: 'detective-basic', label: 'Basic Detector', icon: <Search className="icon-sm"/>, active: true},
        {id: '', label: 'Landing Page', icon: <Home className="icon-sm"/>}
    ];

    return (
        <div className="basic-detective-container">
            
            {/*sidebar*/}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <div className="sidebar-logo-icon">
                            <img src={Logo} alt="Detective AI Logo" className="logo-img"/>
                        </div>
                        <span className="sidebar-title">Detective AI</span>
                    </div>
                    <button className="close-sidebar" onClick={toggleSidebar}>
                        <Menu className="icon-sm"/>
                    </button>
                </div>

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

                    {/* Upgrade Prompt */}
                    <div className="upgrade-prompt">
                      <div className="upgrade-content">
                        <Shield className="icon-md upgrade-icon"/>
                        <h4>Unlock Full Features</h4>
                        <p>Sign in for free to access:</p>
                        <ul>
                            <li>Unlimited text analysis</li>
                            <li>File uploaded support</li>
                            <li>Image detection</li>
                            <li>Analysis history</li>
                            <li>Advanced report</li>
                        </ul>
                      </div>
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

                  {/* Left side: menu button + logo together */}
                  <div className="header-left">
                    <button
                      className="menu-toggle"
                      onClick={toggleSidebar}
                    >
                      <Menu className="icon-sm"/>
                    </button>

                    {/*logo*/}
                    <div className="detective-logo">
                      <div className="detective-logo-icon">
                        <img src={Logo} alt="Detective AI Logo" className="logo-img"/>
                      </div>
                      <div>
                        <h1 className="detective-title">Detective AI</h1>
                        <p className="detective-subtitle">Content Detection</p>
                      </div>
                    </div>
                  </div>   
                    
                    {/* Right side: sign in */}
                  <RouterLink to="/login">
                     <button className="btn-signin">
                     <span>Sign In</span>
                     <ChevronRight className="icon-sm"/>
                     </button>
                  </RouterLink>
                  </div>
            </header>

            {/*main content*/}
            <main className={`detective-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
              <div className="content-area">
                {/* Main Detection Interface */}
                <div className="detection-interface">
                    <div className="interface-header">
                        <h1 className="interface-title">AI Content Detection</h1>
                        <p className="interface-subtitle">
                            Try our AI detection with up to 250 characters. Sign in for unlimited access.
                        </p>
                    </div>

                    {/* Detection Type Options */}
                    <div className="detection-options">
                      {/* Text detection - Enabled*/}
                      <div className="detection-card active">
                        <div className="card-icon">
                          <FileText className="icon-lg" />
                        </div>
                        <h3 className="card-title">Text Detection</h3>
                        <p className="card-description">Analyse text up to 250 characters for AI-generated patterns.</p>
                      </div>

                      {/* Image detection - Disabled */}
                      <div
                        className="detection-card disabled"
                        onMouseEnter={() => setShowTooltip('image')}
                        onMouseLeave={() => setShowTooltip(null)}
                      >
                        <div className="card-icon">
                          <ImageIcon className="icon-lg" />
                        </div>
                        <h3 className="card-title">Image Detection</h3>
                        <p className="card-description">Detect AI-generated images using advanced visual analysis.</p>
                        {showTooltip === 'image' && (
                          <div className="feature-tooltip"> 
                            Sign in for Image Detection
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Text Input Area */}
                    <div className="text-input-area">
                      <div className="input-toggle">
                        <button 
                            className="toggle-btn active">
                            <Type className="icon-sm" />
                            Type Text
                        </button>
                        <button 
                            className="toggle-btn disabled"
                            onMouseEnter={() => setShowTooltip('upload')}
                            onMouseLeave={() => setShowTooltip(null)}
                            onClick= {() => handleDisabledFeature('upload')}
                        >
                            <FileUp className="icon-sm" />
                            Upload Document
                            {showTooltip === 'upload' && (
                              <div className="feature-tooltip">
                                Sign in for File Upload
                              </div>
                            )}
                        </button>
                      </div>

                      <div className="text-input-wrapper">
                        <textarea
                            className={`text-area ${isOverLimit() ? 'over-limit' : ''}`}
                            placeholder="Paste or type your text here for AI detection analysis (up to 250 characters)..."
                            value={textContent}
                            onChange={(e) => setTextContent(e.target.value)}
                        />
                        <div className={`word-counter ${isOverLimit() ? 'over-limit' : ''}`}>
                          {getCharacterCount()} / {CHARACTER_LIMIT} characters
                          {isOverLimit() && <span className="limit-warning"> - Limit exceeded</span>}
                        </div>
                      </div>

                      <button 
                        className="analyze-button"
                        onClick={handleTextAnalysis}
                        disabled={!textContent.trim() || isAnalyzing || isOverLimit()}
                      >
                        {isAnalyzing ? (
                            <>
                                <Loader className="icon-sm animate-spin" />
                                Analysing...
                            </>
                        ) : (
                            <>
                                <Eye className="icon-sm" />
                                Analyse Text
                            </>
                        )}
                      </button>
                    </div>

                    {/* Loading State */}
                    {isAnalyzing && (
                        <div className="loading-container">
                            <div className="loading-spinner"></div>
                            <div className="loading-text">Analysing text patterns...</div>
                        </div>
                    )}

                    {/* Results */}
                    {analysisResult && !isAnalyzing && (
                      <div className="results-container">
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
                        </div>

                        {/* Basic Analysis Report */}
                        <BasicAnalysisReport result={analysisResult} />

                        <div className="analyzed-text" dangerouslySetInnerHTML={{ __html: analysisResult.highlightedText }} />

                        {/* Sign in prompt */}
                        <div className="signin-prompt">
                          <div className="signin-content">
                            <Shield className="signin-icon" />
                            <div>
                              <h4>Want More Detailed Analysis?</h4>
                              <p>Sign in to unlock advanced features, unlimited analysis, and detailed reports.</p>
                            </div>
                            <RouterLink to="/login">
                                <button className="signin-btn">Sign In</button>
                            </RouterLink>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Feature Promotion*/}
                    <div className="features-promotion">
                      <h3 className="promotion-title">Unlock Premium Features</h3>
                      <div className="features-grid">
                          <div className="feature-card">
                              <div className="feature-icon">
                                  <FileText className="icon-md" />
                              </div>
                              <h4>Unlimited Text Analysis</h4>
                              <p>Analyse texts of any length without character limits</p>
                          </div>
                          <div className="feature-card">
                              <div className="feature-icon">
                                  <Upload className="icon-md" />
                              </div>
                              <h4>File Upload Support</h4>
                              <p>Upload PDF and DOCX files for direct analysis</p>
                          </div>
                          <div className="feature-card">
                              <div className="feature-icon">
                                  <ImageIcon className="icon-md" />
                              </div>
                              <h4>Image Detection</h4>
                              <p>Detect AI-generated images with advanced algorithms</p>
                          </div>
                      </div>
                    </div>
                </div>
              </div>
            </main>  
        </div>
    );
};
export default DetectiveBasic;