import React, {useState, useRef} from 'react';
import './DetectivePage.css';
import Logo from '../Assets/Logo.png';
import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker?url";  //pdf.js worker import for parsing pdfs
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
    Menu,
    Target,
    TrendingUp,
    Brain,
    FileCheck,
    Info
} from 'lucide-react';
import { Link as RouterLink } from "react-router-dom";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;   //assign pdf.js worker

const DetectivePage = () => {
    //sidebar and view state
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentView, setCurrentView] = useState('main');

    //text and image analysis state
    const [activeDetectionType, setActiveDetectionType] = useState('text');
    const [inputMode, setInputMode] = useState('type'); //type or upload
    const [textContent, setTextContent] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [uploadedImage, setUploadedImage] = useState(null);

    //feedback state
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedbackText, setFeedbackText] = useState('');
    const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

    //Refs for file inputs
    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);

    //history items state
    const [historyItems, setHistoryItems] = useState([
        //sample items
        {
            id: 1,
            type:'text',
            title: 'Academic Essay Analysis',
            date: '2 hours ago',
            content: 'This AI-generated report demonstrates how the field of artificial...',
            result: {isAI: true, confidence: 87, highlightedText: 'This <span class="highlight">AI-generated<span class="tooltip">Explicit phrase often flagged</span></span> report demonstrates how the field of <span class="highlight">artificial intelligence<span class="tooltip">Suspicious phrase pattern</span></span> has <span class="highlight">revolutionized<span class="tooltip">AI-typical word choice</span></span> and <span class="highlight">transformed<span class="tooltip">Generic overused verb</span></span> countless industries through <span class="highlight">cutting-edge<span class="tooltip">Buzzword frequently used by AI</span></span>, <span class="highlight">state-of-the-art<span class="tooltip">Marketing-style phrasing</span></span>, and profoundly <span class="highlight">innovative<span class="tooltip">Overly polished descriptor</span></span> approaches. The discussion <span class="highlight">delves<span class="tooltip">Unnatural academic phrasing</span></span> into the potential to <span class="highlight">leverage<span class="tooltip">Corporate jargon flagged by detectors</span></span> data, <span class="highlight">optimize<span class="tooltip">Common AI buzzword</span></span> processes, and <span class="highlight">facilitate<span class="tooltip">Inflated word choice</span></span> decision-making in ways that were previously unimaginable. <span class="highlight">Furthermore<span class="tooltip">Overused transition word</span></span>, research in <span class="highlight">machine learning<span class="tooltip">Suspicious phrase pattern</span></span> has <span class="highlight">consequently<span class="tooltip">Formulaic connector</span></span> accelerated breakthroughs across science, healthcare, and technology. <span class="highlight">Moreover<span class="tooltip">Repetitive transition marker</span></span>, the integration of these methods has <span class="highlight">additionally<span class="tooltip">Stacked connector often in AI text</span></span> created opportunities for businesses to thrive in highly competitive environments. <span class="highlight">Furthermore<span class="tooltip">Overused transition word</span></span>, by adopting such strategies, organizations can <span class="highlight">leverage<span class="tooltip">Corporate jargon flagged again</span></span> insights, <span class="highlight">optimize<span class="tooltip">Repetitive buzzword</span></span> resources, and <span class="highlight">facilitate<span class="tooltip">Artificially formal phrasing</span></span> growth. <span class="highlight">Moreover<span class="tooltip">Repetitive transition marker</span></span>, the evolution of algorithms has <span class="highlight">additionally<span class="tooltip">Stacked connector again</span></span> reshaped human interaction with digital ecosystems, ultimately underscoring how <span class="highlight">state-of-the-art<span class="tooltip">Buzzword repeated</span></span> innovations continue to transform society.'}
        },
        {
            id: 2,
            type:'text',
            title: 'Report Review',
            date: '2 days ago',
            content: 'Abstract—This practical investigates the computational performance of the STM32F0...',
            result: {isAI: false, confidence: 92, highlightedText: 'Abstract—This practical investigates the computational performance of the STM32F0 microcontroller through implementation and benchmarking of Mandelbrot set calculations. Two numerical approaches were evaluated: Fixed-Point Arithmetic and Double-Precision Floating-Point operations across multiple image resolutions (128x128 to 256×256 pixels). The study demonstrates the trade-offs between computational accuracy and execution speed in embedded systems, with Fixed-Point Arithmetic achieving great performance while maintaining acceptable accuracy within 1% tolerance of reference Python implementations (Mandelbrot.py).'}
        }
    ]);

    //quick stats and recent activities
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
        const corporateJargon = ['leverage', 'optimize', 'facilitate', 'streamline', 'synergize', 'paradigm'];
        const buzzwords = ['cutting-edge', 'state-of-the-art', 'revolutionary', 'groundbreaking', 'innovative', 'profoundly'];
        const humanIndicators = ['hi', 'my name is', 'i am', 'yah', 'from', 'student', 'towards', 'degree', 'majoring'];

        let isAI = false;
        let confidence = 0;
        const detectionReasons = [];
        const statistics = {
            totalWords: 0,
            sentences: 0,
            avgSentenceLength: 0,
            aiKeywordsCount: 0,
            transitionWordsCount: 0,
            corporateJargonCount: 0,
            buzzwordsCount: 0,
            suspiciousPatternsCount: 0,
            humanIndicatorsCount: 0
        };

        //check for ai keywords
        const lowerText = text.toLowerCase();

        //calculate basic stats
        const words = text.split(/\s+/).filter(word => word.length > 0);
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);

        statistics.totalWords = words.length;
        statistics.sentences = sentences.length;
        statistics.avgSentenceLength = sentences.length > 0 ? words.length / sentences.length : 0;
        
        //check for ai keywords
        const foundKeywords = aiKeywords.filter(keyword => lowerText.includes(keyword));
        statistics.aiKeywordsCount = foundKeywords.length;

        //check for transition words
        const foundTransitions = transitionWords.filter(word => lowerText.includes(word));
        statistics.transitionWordsCount = foundTransitions.length;

        //check for corporate jargon
        const foundJargon = corporateJargon.filter(word => lowerText.includes(word));
        statistics.corporateJargonCount = foundJargon.length;

        //check for buzzwords
        const foundBuzzwords = buzzwords.filter(word => lowerText.includes(word));
        statistics.buzzwordsCount = foundBuzzwords.length;

        //check for suspicious patterns
        const foundPatterns = suspiciousPatterns.filter(pattern => lowerText.includes(pattern.toLowerCase()));
        statistics.suspiciousPatternsCount = foundPatterns.length;

        //check for human indicators
        const foundHumanIndicators = humanIndicators.filter(indicator => lowerText.includes(indicator));
        statistics.humanIndicatorsCount = foundHumanIndicators.length;

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

        if (foundKeywords.length >= 5) {
            isAI = true;
            confidence += 20;
            detectionReasons.push({
                type: 'warning',
                title: 'High AI Keyword Density',
                description: `Detected ${foundKeywords.length} AI-typical words (${((foundKeywords.length / words.length) * 100).toFixed(1)}% of text)`,
                impact: 'High'
            });
        }

        if (foundTransitions.length >= 3) {
            isAI = true;
            confidence += 15;
            detectionReasons.push({
                type: 'warning',
                title: 'Excessive Formal Transitions',
                description: `High frequency of formal transition words: ${foundTransitions.length} instances (${foundTransitions.join(', ')})`,
                impact: 'Medium'
            });
        }

        if (foundJargon.length >= 3) {
            isAI = true;
            confidence += 10;
            detectionReasons.push({
                type: 'info',
                title: 'Corporate Jargon Pattern',
                description: `Business terminology suggests AI generation: ${foundJargon.join(', ')}`,
                impact: 'Medium'
            });
        }

        if (statistics.avgSentenceLength > 20) {
            confidence += 5;
            detectionReasons.push({
                type: 'info',
                title: 'Complex Sentence Structure',
                description: `Average sentence length of ${statistics.avgSentenceLength.toFixed(1)} words suggests formal AI writing`,
                impact: 'Low'
            });
        }

        //human indicators (reduce AI confidence)
        if (foundHumanIndicators.length >= 3) {
            confidence -= 30;
            detectionReasons.push({
                type: 'success',
                title: 'Personal/Conversational Language',
                description: `Found ${foundHumanIndicators.length} human-style indicators: ${foundHumanIndicators.slice(0, 5).join(', ')}`,
                impact: 'Positive'
            });
        }

        if (statistics.avgSentenceLength < 15 && foundTransitions.length <= 1) {
            confidence -= 20;
            detectionReasons.push({
                type: 'success',
                title: 'Natural Sentence Structure',
                description: 'Short, natural sentences with minimal formal transitions',
                impact: 'Positive'
            });
        }

        if (foundKeywords.length === 0 && foundPatterns.length === 0) {
            confidence -= 25;
            detectionReasons.push({
                type: 'success',
                title: 'No AI-typical Patterns',
                description: 'No AI buzzwords or suspicious patterns detected',
                impact: 'Positive'
            });
        }

        //check for informal language patterns
        const informalPatterns = ['!', 'yah', 'hi', 'my name', 'i am', 'cool'];
        const foundInformal = informalPatterns.filter(pattern => lowerText.includes(pattern));
        if (foundInformal.length >= 2) {
            confidence -= 15;
            detectionReasons.push({
                type: 'success',
                title: 'Informal/Personal Tone',
                description: 'Casual language and personal expressions detected',
                impact: 'Positive'
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
        [...aiKeywords, ...suspiciousPatterns, ...transitionWords, ...corporateJargon, ...buzzwords].forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            highlightedText = highlightedText.replace(regex,
                `<span class="hightlight">${keyword}<span class="tooltip">AI-typical phrase detected</span></span>`
            );
        });
        return {isAI,
            confidence,
            highlightedText,
            detectionReasons,
            statistics,
            analysisDetails: {
                foundKeywords,
                foundPatterns,
                foundTransitions,
                foundJargon,
                foundBuzzwords,
                foundHumanIndicators
            }
        };
    };

    const performImageAnalysis = (filename) => {
        //mock logic based on filename
        const lower = filename.toLowerCase();
        if (lower.includes("lindo_ai") || lower.includes("generated")){
            return {isAI: true, confidence: 90};
        }
        else if (lower.includes("lindo_original") || lower.includes("written")){
            return {isAI: false, confidence: 92};
        }

        return {isAI: Math.random() > 0.5, confidence: 85}
    };

    //---------------------------
    //handlers for user actions
    //--------------------------
    const handleTextAnalysis = async () => {
        if (!textContent.trim()) return;

        setIsAnalyzing(true);

        setTimeout(() => {
            const result = performTextAnalysis(textContent);
            setAnalysisResult(result);
            setIsAnalyzing(false);
        }, 2000);   //simulate api delay
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const fileType = file.type;
        const fileName = file.name.toLowerCase();

        if (activeDetectionType === 'text') {
            if (!fileType.includes('pdf')) {
                alert('Please upload only PDF files for text analysis in this prototype.');
                return;
            }

            setIsAnalyzing(true);

            //read PDF text using pdfjs
            const reader = new FileReader();
            reader.onload = async function () {
                const typedArray = new Uint8Array(this.result);
                const pdf = await pdfjsLib.getDocument(typedArray).promise;
                let fullText = "";

                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    fullText += textContent.items.map(item => item.str).join(" ") + "\n";
                }

                //perform enhanced analysis on extracted tezt
                const result = performTextAnalysis(fullText);
                setAnalysisResult({ ...result, filename: file.name });
                setIsAnalyzing(false);
            };
            reader.readAsArrayBuffer(file);
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

    //-------------------
    //history management
    //-------------------
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
                        <span className="stat-value">{result.statistics.totalWords}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Sentences</span>
                        <span className="stat-value">{result.statistics.sentences}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Avg Sentence Length</span>
                        <span className="stat-value">{result.statistics.avgSentenceLength.toFixed(1)} words</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">AI Indicators</span>
                        <span className="stat-value">{result.statistics.aiKeywordsCount + result.statistics.suspiciousPatternsCount}</span>
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
                    {result.detectionReasons.map((reason, index) => (
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
                        <div className="pattern-count">{result.statistics.transitionWordsCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails.foundTransitions.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {result.analysisDetails.foundTransitions.length > 3 && (
                                <span className="pattern-more">+{result.analysisDetails.foundTransitions.length - 3}</span>
                            )}
                        </div>
                    </div>
                    
                    <div className="pattern-category">
                        <h5 className="pattern-title">Corporate Jargon</h5>
                        <div className="pattern-count">{result.statistics.corporateJargonCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails.foundJargon.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {result.analysisDetails.foundJargon.length > 3 && (
                                <span className="pattern-more">+{result.analysisDetails.foundJargon.length - 3}</span>
                            )}
                        </div>
                    </div>

                    <div className="pattern-category">
                        <h5 className="pattern-title">Buzzwords</h5>
                        <div className="pattern-count">{result.statistics.buzzwordsCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails.foundBuzzwords.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {result.analysisDetails.foundBuzzwords.length > 3 && (
                                <span className="pattern-more">+{result.analysisDetails.foundBuzzwords.length - 3}</span>
                            )}
                        </div>
                    </div>

                    <div className="pattern-category">
                        <h5 className="pattern-title">AI Patterns</h5>
                        <div className="pattern-count">{result.statistics.suspiciousPatternsCount}</div>
                        <div className="pattern-items">
                            {result.analysisDetails.foundPatterns.slice(0, 3).map((word, i) => (
                                <span key={i} className="pattern-tag">{word}</span>
                            ))}
                            {result.analysisDetails.foundPatterns.length > 3 && (
                                <span className="pattern-more">+{result.analysisDetails.foundPatterns.length - 3}</span>
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
                            ? `This content shows ${result.confidence}% likelihood of being AI-generated based on ${result.detectionReasons.length} detection factors.`
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
                <button className="new-detection">
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
export default DetectivePage;