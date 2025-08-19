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
    const imageInputReff = useRef(null);

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
}