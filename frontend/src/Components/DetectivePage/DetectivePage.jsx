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

    
}