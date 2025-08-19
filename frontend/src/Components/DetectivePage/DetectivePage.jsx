import React, {useState, useRef} from 'react';
import './DetectivePage.css';
import {
    Search,
    Eye,
    X,
    ChevronRight,
    FileText,
    Imgage as ImageIcon,
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
    Loader
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
            result: {isAI: true, confidence: 87, highlightedText: 'The rapid advancements of AI has <span class="hightlight">revolutionized<span class="tooltip">AI-typical word choice</span></span>various industries and <span class="highlight">transformed<span class="tooltip">Overused transition word</span></span> the way we approach complex problems.'}
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
            <div clasName={`sidebar ${sidebarOpen ? 'open' : ''}`}>
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

                
            </div>
        </div>
    );
}