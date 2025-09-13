import React, {useState, useRef, useEffect} from 'react';
import './DetectivePage.css';
import Logo from "../Assets/Logo.png";
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
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;   //assign pdf.js worker

const DetectivePage = () => {
    // API Configuration.
    const API_BASE_URL = 'http://localhost:8000';
    
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
    const reportRef = useRef(null);

    //history items state
    const [historyItems, setHistoryItems] = useState([]);

    // Fetch user history on component mount
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await fetch('/api/user/submissions', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('userToken')}`, // If using auth
                    }
                });
                const data = await response.json();
                
                if (data.success) {
                    // Transform API data to match your component format
                    const transformedHistory = data.data.map(item => ({
                        id: item.submission.id,
                        type: 'text', // or determine from item data
                        title: item.submission.name,
                        date: new Date(item.submission.created_at).toLocaleString(),
                        content: item.input_text.substring(0, 100) + '...',
                        result: {
                            isAI: item.analysis_result.prediction.is_ai_generated,
                            confidence: Math.round(item.analysis_result.prediction.confidence * 100),
                            highlightedText: item.input_text, // Will be processed by generateHighlightedText when viewed
                            detectionReasons: item.analysis_result.analysis.detection_reasons,
                            statistics: item.analysis_result.statistics,
                            analysisDetails: item.analysis_result.analysis.analysis_details
                        }
                    }));
                    setHistoryItems(transformedHistory);
                }
            } catch (error) {
                console.error('Failed to fetch history:', error);
            }
        };
        
        fetchHistory();
    }, []);

    /* REMOVED - RECENT ACTIVITY WILL BE IN ADMIN PAGE
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
    */

    //sidebar toggle
    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    //------------------------
    // API-based AI detection logic
    //-------------------------
    
    // Helper function to generate highlighted text from API data
    const generateHighlightedText = (originalText, analysisDetails) => {
        if (!analysisDetails) return originalText;
        
        let highlightedText = originalText;
        const highlights = [];
        
        // Collect all found items with their types
        if (analysisDetails.foundKeywords?.length > 0) {
            analysisDetails.foundKeywords.forEach(keyword => {
                highlights.push({
                    text: keyword,
                    type: 'keyword',
                    tooltip: 'AI-typical keyword detected'
                });
            });
        }
        
        if (analysisDetails.foundPatterns?.length > 0) {
            analysisDetails.foundPatterns.forEach(pattern => {
                highlights.push({
                    text: pattern,
                    type: 'suspicious',
                    tooltip: 'Suspicious AI pattern detected'
                });
            });
        }
        
        if (analysisDetails.foundTransitions?.length > 0) {
            analysisDetails.foundTransitions.forEach(transition => {
                highlights.push({
                    text: transition,
                    type: 'transition',
                    tooltip: 'Overused transition word'
                });
            });
        }
        
        if (analysisDetails.foundJargon?.length > 0) {
            analysisDetails.foundJargon.forEach(jargon => {
                highlights.push({
                    text: jargon,
                    type: 'jargon',
                    tooltip: 'Corporate jargon flagged by detectors'
                });
            });
        }
        
        if (analysisDetails.foundBuzzwords?.length > 0) {
            analysisDetails.foundBuzzwords.forEach(buzzword => {
                highlights.push({
                    text: buzzword,
                    type: 'buzzword',
                    tooltip: 'Buzzword frequently used by AI'
                });
            });
        }
        
        if (analysisDetails.foundHumanIndicators?.length > 0) {
            analysisDetails.foundHumanIndicators.forEach(indicator => {
                highlights.push({
                    text: indicator,
                    type: 'human',
                    tooltip: 'Human writing indicator'
                });
            });
        }
        
        // Apply highlights to text
        highlights.forEach(highlight => {
            const regex = new RegExp(`\\b${highlight.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
            highlightedText = highlightedText.replace(regex, 
                `<span class="highlight highlight-${highlight.type}">
                    ${highlight.text}
                    <span class="tooltip">${highlight.tooltip}</span>
                </span>`
            );
        });
        
        return highlightedText;
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
    
    /* OLD MOCKED ANALYSIS LOGIC - COMMENTED OUT
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

        // Helper for group highlighting
        const highlightGroups = [
            {
                words: aiKeywords,
                className: "highlight-keyword",
                tooltip: "AI keyword: frequently used in AI-generated content"
            },
            {
                words: suspiciousPatterns,
                className: "highlight-suspicious",
                tooltip: "Explicit AI-related phrase"
            },
            {
                words: transitionWords,
                className: "highlight-transition",
                tooltip: "Formal transition word: often overused by AI"
            },
            {
                words: corporateJargon,
                className: "highlight-jargon",
                tooltip: "Corporate jargon: business/AI terminology"
            },
            {
                words: buzzwords,
                className: "highlight-buzzword",
                tooltip: "Buzzword: marketing or hype language"
            }
        ];

        // Avoid double-highlighting by replacing in order of least likely overlap
        highlightGroups.forEach(group => {
            group.words.forEach(keyword => {
                const regex = new RegExp(`\\b${keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, 'gi');
                highlightedText = highlightedText.replace(
                    regex,
                    `<span class="highlight ${group.className}">${keyword}<span class="tooltip">${group.tooltip}</span></span>`
                );
            });
        });
        return {
            isAI,
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
    */

    const performImageAnalysis = async (file) => {
        try {
            const formData = new FormData();
            formData.append('image', file);
            
            const response = await fetch('/api/analyze/image', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Image analysis failed');
            }
            
            return {
                isAI: data.data.analysis_result.prediction.is_ai_generated,
                confidence: Math.round(data.data.analysis_result.prediction.confidence * 100),
                submissionId: data.data.submission.id,
                analysisId: data.data.analysis_result.analysis_id,
                highlightedText: '' // Images don't have highlighted text
            };
        } catch (error) {
            console.error('Image analysis failed:', error);
            throw error;
        }
    };

    /* OLD MOCKED IMAGE ANALYSIS - COMMENTED OUT
    const performImageAnalysis = (filename) => {
        //mock logic based on filename
        const lower = filename.toLowerCase();
        if (lower.includes("lindo_ai") || lower.includes("generated")){
            return {isAI: true, confidence: 90, highlightedText: ''};
        }
        else if (lower.includes("lindo_original") || lower.includes("written")){
            return {isAI: false, confidence: 92, highlightedText: ''};
        }

        return {isAI: Math.random() > 0.5, confidence: 85, highlightedText: ''}
    };
    */

    //---------------------------
    //handlers for user actions
    //--------------------------
    const handleTextAnalysis = async () => {
        if (!textContent.trim()) return;

        setIsAnalyzing(true);

        try {
            const result = await performTextAnalysis(textContent);
            setAnalysisResult(result);
            saveToHistory(result); // Save to history after successful analysis
        } catch (error) {
            console.error('Text analysis failed:', error);
            alert('Analysis failed. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    /* OLD MOCKED TEXT ANALYSIS HANDLER - COMMENTED OUT
    const handleTextAnalysis = async () => {
        if (!textContent.trim()) return;

        setIsAnalyzing(true);

        setTimeout(() => {
            const result = performTextAnalysis(textContent);
            setAnalysisResult(result);
            setIsAnalyzing(false);
        }, 2000);   //simulate api delay
    };
    */

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
                //read PDF text using pdfjs
                const reader = new FileReader();
                reader.onload = async function () {
                    try {
                        const typedArray = new Uint8Array(this.result);
                        const pdf = await pdfjsLib.getDocument(typedArray).promise;
                        let fullText = "";

                        for (let i = 1; i <= pdf.numPages; i++) {
                            const page = await pdf.getPage(i);
                            const textContent = await page.getTextContent();
                            fullText += textContent.items.map((item) => item.str).join(" ") + "\n";
                        }

                        // Perform real API analysis on extracted text
                        const result = await performTextAnalysis(fullText);
                        setAnalysisResult({ ...result, filename: file.name });
                        saveToHistory({ ...result, filename: file.name });
                    } catch (error) {
                        console.error('PDF analysis failed:', error);
                        alert('PDF analysis failed. Please try again.');
                    } finally {
                        setIsAnalyzing(false);
                    }
                };
                reader.readAsArrayBuffer(file);
            } catch (error) {
                console.error('File upload failed:', error);
                alert('File upload failed. Please try again.');
                setIsAnalyzing(false);
            }
        }
    };

    /* OLD MOCKED FILE UPLOAD HANDLER - COMMENTED OUT
    const handleFileUpload = async (event) => {
        const file = event.target.files?.[0];
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
                    fullText += textContent.items.map((item) => item.str).join(" ") + "\n";
                }

                //perform enhanced analysis on extracted tezt
                const result = performTextAnalysis(fullText);
                setAnalysisResult({ ...result, filename: file.name });
                setIsAnalyzing(false);
            };
            reader.readAsArrayBuffer(file);
        }
    };
    */

    const handleImageUpload = async (event) => {
        const file = event.target.files?.[0];
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
        reader.onload = async (e) => {
            setUploadedImage(e.target?.result);

            setIsAnalyzing(true);
            try {
                const result = await performImageAnalysis(file);
                setAnalysisResult({...result, filename: file.name, isImage: true});
                saveToHistory({...result, filename: file.name, isImage: true});
            } catch (error) {
                console.error('Image analysis failed:', error);
                alert('Image analysis failed. Please try again.');
            } finally {
                setIsAnalyzing(false);
            }
        };
        reader.readAsDataURL(file);
    };

    /* OLD MOCKED IMAGE UPLOAD HANDLER - COMMENTED OUT
    const handleImageUpload = async (event) => {
        const file = event.target.files?.[0];
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
            setUploadedImage(e.target?.result);

            setIsAnalyzing(true);
            setTimeout(() => {
                const result = performImageAnalysis(file.name);
                setAnalysisResult({...result, filename: file.name, isImage: true});
                setIsAnalyzing(false);
            }, 2500);
        };
        reader.readAsDataURL(file);
    };
    */

    const handleThumbsDown = () => {
        setShowFeedback(true);
    };

    const submitFeedback = async () => {
        if (!feedbackText.trim()) return;
        
        try {
            const response = await fetch('/api/feedback/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_id: analysisResult?.analysisId,
                    submission_id: analysisResult?.submissionId,
                    feedback_text: feedbackText,
                    query: analysisResult?.filename || 'Current Analysis'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                setFeedbackText('');
                setShowFeedback(false);
                alert('Feedback submitted successfully!');
            } else {
                throw new Error(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Failed to submit feedback:', error);
            alert('Failed to submit feedback. Please try again.');
        }
    };

    /* OLD MOCKED FEEDBACK SUBMISSION - COMMENTED OUT
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
    */

    //-------------------
    //history management
    //-------------------
    const saveToHistory = async (analysisData) => {
        // Add to local state for immediate UI update
        const newHistoryItem = {
            id: analysisData.submissionId || Date.now(),
            type: activeDetectionType,
            title: analysisData.filename || `${activeDetectionType} Analysis ${new Date().toLocaleTimeString()}`,
            date: new Date().toLocaleString(),
            content: activeDetectionType === 'text' ? textContent.substring(0, 100) + '...' : 'Image analysis',
            result: analysisData
        };
        setHistoryItems(prev => [newHistoryItem, ...prev]);
    };

    const viewHistoryItem = (item) => {
        // Generate highlighted text if not already available
        if (item.result.analysisDetails && !item.result.highlightedText.includes('<span class="highlight"')) {
            const originalText = item.content.endsWith('...') ? 
                item.content.substring(0, item.content.length - 3) : item.content;
            item.result.highlightedText = generateHighlightedText(originalText, item.result.analysisDetails);
        }
        setSelectedHistoryItem(item);
        setCurrentView('history-detail');
    };

    const deleteHistoryItem = async (id) => {
        try {
            const response = await fetch(`/api/submissions/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                setHistoryItems(prev => prev.filter(item => item.id !== id));
            } else {
                throw new Error('Failed to delete history item');
            }
        } catch (error) {
            console.error('Failed to delete history item:', error);
            alert('Failed to delete history item. Please try again.');
        }
    };

    /* OLD MOCKED HISTORY MANAGEMENT - COMMENTED OUT
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
    */

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
            description: 'Analyse text content for AI-generated patterns and signatures.',
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

    // PDF export function
    const exportReportAsPDF = async () => {
        const input = reportRef.current;
        if (!input) return;
        const canvas = await html2canvas(input, { scale: 2 });
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({
            orientation: 'portrait',
            unit: 'px',
            format: [canvas.width, canvas.height]
        });
        pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
        pdf.save('analysis-report.pdf');
    };

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
                    <div className="header-left">
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
                                                            Analyse Text
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
                                                            // Results are already saved automatically during analysis
                                                            alert('Thank you for your feedback!');
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
                                {/*<div className="recent-activity">
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
                                </div>*/}
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

            {/* FEEDBACK MODAL - Still present but will be moved to admin page */}
            {showFeedback && (
                <div className="modal-overlay" onClick={() => setShowFeedback(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">Provide Feedback</h3>
                            <button className="modal-close" onClick={() => setShowFeedback(false)}>
                                <X className="icon-sm" />
                            </button>
                        </div>
                        <textarea
                            className="feedback-textarea"
                            placeholder="Help us improve by describing what was incorrect about this analysis..."
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