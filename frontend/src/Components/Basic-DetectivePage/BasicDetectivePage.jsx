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
    const getWordCount = () => {
      return textContent.trim() ? textContent.trim().split(/\s+/).length : 0;
    };

    const isOverLimit = () => {
      return getWordCount() > WORD_LIMIT;
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

    //disabled feature handlers
    const handleDisabledFeature = (feature) => {
        setShowToolTip(feature);
        setTimeout(() => setShowToolTip(null), 2000);
    };

    // Basic Analysis Report Component
    const AnalysisReport = ({ result }) => (
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
        {id: 'detector', label: 'Detector', icon: <Search className="icon-sm"/>, active: true},
        {id: 'team', label: 'Team', icon: <Users className="icon-sm"/>},
        {id: 'demo', label: 'Demo', icon: <Play className="icon-sm"/>}
    ];

    return (
        <div className="basic-detective-container">
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
                      <div className="upgrade-icon">
                        <Shield className="icon-md upgrade-icon"/>
                        <h4>Unlock Full Features</h4>
                        <p>Sign in for free to access:</p>
                        <ul>
                            <li>Unlimited Text analysis</li>
                            <li>File Uploade Support</li>
                            <li>Image Detection</li>
                            <li>Analysis History</li>
                            <li>Advanced Report</li>
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
                    <button className="btn-signin">
                        <span>Sign In</span>
                        <ChevronRight className="icon-sm"/>
                    </button>
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
                              Try our AI detection with up to 250 words. Sign in for unlimited access.
                          </p>
                      </div>

                      {/* Detection Type Options */}
                      <div className="detection-options">
                        {/* Text detection - Enabled*/}
                        <div className="detection-option active">
                          <div className="card-icon">
                            <FileText className="icon-lg" />
                          </div>
                          <h3 className="card-title">Text Detection</h3>
                          <p className="card-description">Analyze text up to 250 words for AI-generated patterns.</p>
                        </div>

                        {/* Image detection - Disabled */}
                        <div
                          className="detection-option disabled"
                          onMouseEnter={() => setShowToolTip('image')}
                          onMouseLeave={() => setShowToolTip(null)}
                        >
                          <div className="card-icon">
                            <ImageIcon className="icon-lg" />
                          </div>
                          <h3 className="card-title">Image Detection</h3>
                          <p className="card-description">Detect AI-generated images using advanced visual analysis.</p>
                          {showToolTip === 'image' && (
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
                              onMouseEnter={() => setShowToolTip('upload')}
                              onMouseLeave={() => setShowToolTip(null)}
                              onClick= {() => handleDisabledFeature('upload')}
                          >
                              <FileUp className="icon-sm" />
                              Upload Document
                              {showToolTip === 'upload' && (
                                <div className="feature-tooltip">
                                  Sign in for File Upload
                                </div>
                              )}
                          </button>
                        </div>

                        <div className="text-input-wrapper">
                          <textarea
                              className={`text-area ${isOverLimit() ? 'over-limit' : ''}`}
                              placeholder="Paste or type your text here for AI detection analysis (up to 250 words)..."
                              value={textContent}
                              onChange={(e) => setTextContent(e.target.value)}
                          />
                          <div classsName={`word-count ${isOverLimit() ? 'over-limit' : ''}`}>
                            {getWordCount()} / {WORD_LIMIT} words
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
                                  Analyzing...
                              </>
                          ) : (
                              <>
                                  <Eye className="icon-sm" />
                                  Analyze Text
                              </>
                          )}
                        </button>
                      </div>

                      {/* Loading State */}
                      {isAnalyzing && (
                          <div className="loading-container">
                              <div className="loading-spinner"></div>
                              <div className="loading-text">Analyzing text patterns...</div>
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
                              <button className="signin-btn">Sign In</button>
                            </div>
                          </div>
                        </div>
                      )}

  



            
        </div>
    );
};
export default BasicDetectivePage;