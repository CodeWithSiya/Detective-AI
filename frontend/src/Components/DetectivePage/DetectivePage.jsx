// For DOCX parsing
import mammoth from "mammoth";
import React, {useState, useRef, useEffect, useCallback, useMemo} from 'react';
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
    Info,
    Home,
    Settings
} from 'lucide-react';
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { getAuthToken, isAuthenticated, getCurrentUser } from "../UserAuthentication/AuthHandler";
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { sub } from "framer-motion/client";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;   //assign pdf.js worker

const DetectivePage = () => {
    // API Configuration.
    const API_BASE_URL = 'http://localhost:8000';
    const navigate = useNavigate();

    // Get auth token and user data.
    const authToken = getAuthToken();
    const isUserAuthenticated = isAuthenticated();
    const currentUser = getCurrentUser();

    // Redirect to login if not authenticated.
    useEffect(() => {
        if (!isUserAuthenticated) {
            navigate('/', { replace: true });
            return;
        }
    }, [isUserAuthenticated, navigate]);
    
    // Sidebar and view state
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentView, setCurrentView] = useState('main');

    // Text and image analysis state
    const [activeDetectionType, setActiveDetectionType] = useState('text');
    const [inputMode, setInputMode] = useState('type'); //type or upload
    const [textContent, setTextContent] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [uploadedImage, setUploadedImage] = useState(null);
    
    // Uploaded file states for feedback
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isFileUploaded, setIsFileUploaded] = useState(false);

    // Feedback state
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedbackText, setFeedbackText] = useState('');
    const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

    // Individual History Items
    const [historyItemStates, setHistoryItemStates] = useState({});

    // Refs for file inputs
    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);
    const reportRef = useRef(null);

    // History items state
    const [historyItems, setHistoryItems] = useState([]);
    const [isHistoryLoading, setIsHistoryLoading] = useState(false);
    
    // Search state for filtering history
    const [searchQuery, setSearchQuery] = useState('');

    // Replace the single isExporting state with separate states
    const [isPDFExporting, setIsPDFExporting] = useState(false);
    const [isEmailSending, setIsEmailSending] = useState(false);

    // Feedback State
    const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
    const [isSubmittingThumbsUp, setIsSubmittingThumbsUp] = useState(false);

    // Filter history items based on search query
    const filteredHistoryItems = useMemo(() => {
        if (!searchQuery.trim()) {
            return historyItems;
        }
        
        return historyItems.filter(item => 
            item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.date.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.type.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [historyItems, searchQuery]);

    // Handle search input changes
    const handleSearchChange = (event) => {
        setSearchQuery(event.target.value);
    };

    // Clear search
    const clearSearch = () => {
        setSearchQuery('');
    };

    // Helper function to truncate text with ellipsis
    const truncateText = (text, maxLength = 20) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

    // Fetch user history on component mount
    const fetchHistory = useCallback(async () => {
        try {
            // Only fetch history if user is authenticated.
            if (!isUserAuthenticated || !authToken) {
                console.log('User not authenticated, skipping history fetch');
                return;
            }

            setIsHistoryLoading(true);

            const response = await fetch(`${API_BASE_URL}/api/submissions/`, {
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log(data);
            
            if (data.success) {
                const transformedHistory = data.data.submissions.map(item => ({
                    id: item.id,
                    type: item.type,
                    title: truncateText(item.name), // Apply truncation here
                    fullTitle: item.name, // Keep original for tooltips
                    date: new Date(item.created_at).toLocaleString(),
                    content: 'Click to view details...', 
                    result: null       // Will be populated when individual submission is fetched.
                }));
                setHistoryItems(transformedHistory);
            }
        } catch (error) {
            console.error('Failed to fetch history:', error);
            if (error.message.includes('401')) {
                console.log('Authentication failed, user may need to log in again');
            }
        } finally {
            setIsHistoryLoading(false);
        }
    }, [isUserAuthenticated, authToken]);

    useEffect(() => {
        // Only fetch history if user is authenticated
        if (!isUserAuthenticated || !authToken) {
            console.log('User not authenticated, skipping history fetch');
            return;
        }

        fetchHistory();
    }, [fetchHistory]);

    //sidebar toggle
    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };
    
    // Helper function to generate highlighted text from API data with priority-based highlighting
    const generateHighlightedText = (originalText, analysisDetails) => {
        if (!analysisDetails) return originalText;
        
        // Define priority levels (higher number = higher priority)
        const PRIORITY_LEVELS = {
            suspicious: 7,    // Highest priority - AI patterns
            keyword: 6,       // AI keywords
            critical: 5,      // Critical indicators
            warning: 4,       // Warning level
            jargon: 3,        // Corporate jargon
            buzzword: 2,      // Buzzwords
            transition: 1,    // Lowest priority - transition words
            human: 0         // Human indicators (different styling)
        };
        
        // Collect all found items with their types and priorities
        const highlights = [];
        
        if (analysisDetails.found_keywords?.length > 0) {
            analysisDetails.found_keywords.forEach(keyword => {
                highlights.push({
                    text: keyword,
                    type: 'keyword',
                    priority: PRIORITY_LEVELS.keyword,
                    tooltip: 'AI-typical keyword detected'
                });
            });
        }
        
        if (analysisDetails.found_patterns?.length > 0) {
            analysisDetails.found_patterns.forEach(pattern => {
                highlights.push({
                    text: pattern,
                    type: 'suspicious',
                    priority: PRIORITY_LEVELS.suspicious,
                    tooltip: 'Suspicious AI pattern detected'
                });
            });
        }
        
        if (analysisDetails.found_transitions?.length > 0) {
            analysisDetails.found_transitions.forEach(transition => {
                highlights.push({
                    text: transition,
                    type: 'transition',
                    priority: PRIORITY_LEVELS.transition,
                    tooltip: 'Overused transition word'
                });
            });
        }
        
        if (analysisDetails.found_jargon?.length > 0) {
            analysisDetails.found_jargon.forEach(jargon => {
                highlights.push({
                    text: jargon,
                    type: 'jargon',
                    priority: PRIORITY_LEVELS.jargon,
                    tooltip: 'Corporate jargon flagged by detectors'
                });
            });
        }
        
        if (analysisDetails.found_buzzwords?.length > 0) {
            analysisDetails.found_buzzwords.forEach(buzzword => {
                highlights.push({
                    text: buzzword,
                    type: 'buzzword',
                    priority: PRIORITY_LEVELS.buzzword,
                    tooltip: 'Buzzword frequently used by AI'
                });
            });
        }
        
        if (analysisDetails.found_human_indicators?.length > 0) {
            analysisDetails.found_human_indicators.forEach(indicator => {
                highlights.push({
                    text: indicator,
                    type: 'human',
                    priority: PRIORITY_LEVELS.human,
                    tooltip: 'Human writing indicator'
                });
            });
        }
        
        // Find all matches for all highlights in the original text
        const matches = [];
        
        highlights.forEach((highlight, highlightIndex) => {
            const escapedText = highlight.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`\\b(${escapedText})\\b`, 'gi');
            let match;
            
            while ((match = regex.exec(originalText)) !== null) {
                matches.push({
                    start: match.index,
                    end: match.index + match[0].length,
                    text: match[0],
                    type: highlight.type,
                    priority: highlight.priority,
                    tooltip: highlight.tooltip,
                    highlightIndex: highlightIndex
                });
            }
        });
        
        // Sort matches by start position
        matches.sort((a, b) => a.start - b.start);
        
        // Remove overlapping matches, keeping higher priority ones
        const filteredMatches = [];
        
        for (let i = 0; i < matches.length; i++) {
            const currentMatch = matches[i];
            let shouldAdd = true;
            
            // Check against already added matches
            for (let j = 0; j < filteredMatches.length; j++) {
                const existingMatch = filteredMatches[j];
                
                // Check if there's any overlap
                const overlaps = (
                    (currentMatch.start >= existingMatch.start && currentMatch.start < existingMatch.end) ||
                    (currentMatch.end > existingMatch.start && currentMatch.end <= existingMatch.end) ||
                    (currentMatch.start <= existingMatch.start && currentMatch.end >= existingMatch.end)
                );
                
                if (overlaps) {
                    // If current match has higher priority, remove the existing one
                    if (currentMatch.priority > existingMatch.priority) {
                        filteredMatches.splice(j, 1);
                        j--; // Adjust index after removal
                    } else {
                        // Keep existing match, don't add current
                        shouldAdd = false;
                        break;
                    }
                }
            }
            
            if (shouldAdd) {
                filteredMatches.push(currentMatch);
            }
        }
        
        // Sort filtered matches by start position (reverse order for replacement)
        filteredMatches.sort((a, b) => b.start - a.start);
        
        // Apply highlights from end to beginning to maintain correct positions
        let result = originalText;
        
        filteredMatches.forEach((match, index) => {
            const offsetClass = `tooltip-offset-${index % 4}`;
            const highlightHtml = `<span class="highlight highlight-${match.type}">${match.text}<span class="tooltip ${offsetClass}">${match.tooltip}</span></span>`;
            
            result = result.substring(0, match.start) + highlightHtml + result.substring(match.end);
        });
        
        return result;
    };

    const performTextAnalysis = async (text, onSuccess) => {
        try {
            // Check if user is authenticated - consistent with exportReportAsPDF
            if (!isUserAuthenticated || !authToken) {
                throw new Error('User not authenticated');
            }

            const headers = {
                'Content-Type': 'application/json',
                'Authorization': `Token ${authToken}`,
            };

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

            const result =  {
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

            if (onSuccess && result.submission) {
                try {
                    await onSuccess(result);
                } catch (callbackError) {
                    console.error('Success callback failed:', callbackError);
                }
            }

            return result;

        } catch (error) {
            console.error('Analysis failed:', error);
            throw error;
        }
    };
    
    const performImageAnalysis = async (file) => {
        try {
            const formData = new FormData();
            formData.append('image', file);
            
            const response = await fetch(`${API_BASE_URL}/api/analysis/image/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${authToken}`,
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Image analysis failed');
            }
            
            // Extract analysis explanations from the correct location and split by \n\n
            const analysisText = data.data.analysis_result.analysis.explanation || '';
            const analysisPoints = analysisText.split('\n\n').filter(point => point.trim() !== '');
            
            return {
                isAI: data.data.analysis_result.prediction.is_ai_generated,
                confidence: Math.round(data.data.analysis_result.prediction.confidence * 100),
                submissionId: data.data.submission.id,
                analysisId: data.data.analysis_result.analysis_id,
                analysisPoints: analysisPoints,
                detectionReasons: data.data.analysis_result.analysis.detection_reasons || [], // Add detection reasons
                metadata: data.data.analysis_result.metadata,
                imageUrl: data.data.submission.image_url,
                dimensions: data.data.submission.dimensions,
                fileSize: data.data.submission.file_size_mb,
                filename: data.data.submission.name,
                timestamp: data.timestamp
            };
        } catch (error) {
            console.error('Image analysis failed:', error);
            throw error;
        }
    };

    //---------------------------
    //handlers for user actions
    //--------------------------
    const handleTextAnalysis = async () => {
        if (!textContent.trim()) return;

        setIsAnalyzing(true);

        try {
            const result = await performTextAnalysis(textContent, async (analysisResult) => {
                // This callback runs after successful analysis with submission
                console.log('Refreshing history after successful submission...');
                await fetchHistory();
            });
            
            setAnalysisResult(result);
            console.log(result);
            
        } catch (error) {
            console.error('Text analysis failed:', error);
            alert('Analysis failed. Please try again.');
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
            if (!fileType.includes('pdf') && !fileType.includes('msword') && !fileType.includes('officedocument.wordprocessingml.document') && !fileType.includes('plain') && !fileName.endsWith('.docx') && !fileName.endsWith('.txt')) {
                alert('Please upload only PDF, DOCX, or TXT files for text analysis.');
                return;
            }

            // Set upload feedback
            setUploadedFile({
                name: file.name,
                size: (file.size / 1024 / 1024).toFixed(2), // Size in MB
                type: file.type
            });
            setIsFileUploaded(true);

            setIsAnalyzing(true);

            // PDF
            if (fileType.includes('pdf')) {
                try {
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
                            const result = await performTextAnalysis(fullText, async (analysisResult) => {
                                await fetchHistory();
                            });
                            setAnalysisResult({ ...result, filename: file.name });
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
            // DOCX
            else if (fileType.includes('officedocument.wordprocessingml.document') || fileType.includes('msword') || fileName.endsWith('.docx')) {
                try {
                    const reader = new FileReader();
                    reader.onload = async function () {
                        try {
                            const arrayBuffer = this.result;
                            const { value } = await mammoth.extractRawText({ arrayBuffer });
                            const result = await performTextAnalysis(value, async (analysisResult) => {
                                await fetchHistory();
                            });
                            setAnalysisResult({ ...result, filename: file.name });
                        } catch (error) {
                            console.error('DOCX analysis failed:', error);
                            alert('DOCX analysis failed. Please try again.');
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
            // TXT
            else if (fileType.includes('plain') || fileName.endsWith('.txt')) {
                try {
                    const reader = new FileReader();
                    reader.onload = async function () {
                        try {
                            const text = this.result;
                            const result = await performTextAnalysis(text, async (analysisResult) => {
                                await fetchHistory();
                            });
                            setAnalysisResult({ ...result, filename: file.name });
                        } catch (error) {
                            console.error('TXT analysis failed:', error);
                            alert('TXT analysis failed. Please try again.');
                        } finally {
                            setIsAnalyzing(false);
                        }
                    };
                    reader.readAsText(file);
                } catch (error) {
                    console.error('File upload failed:', error);
                    alert('File upload failed. Please try again.');
                    setIsAnalyzing(false);
                }
            }
        }
    };

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

        // Set upload feedback
        setUploadedFile({
            name: file.name,
            size: (file.size / 1024 / 1024).toFixed(2), // Size in MB
            type: file.type
        });
        setIsFileUploaded(true);

        const reader = new FileReader();
        reader.onload = async (e) => {
            setUploadedImage(e.target?.result);

            setIsAnalyzing(true);
            try {
                const result = await performImageAnalysis(file);
                setAnalysisResult({...result, filename: file.name, isImage: true});
                await fetchHistory();
            } catch (error) {
                console.error('Image analysis failed:', error);
                alert('Image analysis failed. Please try again.');
            } finally {
                setIsAnalyzing(false);
            }
        };
        reader.readAsDataURL(file);
    };

    const handleThumbsUp = async () => {
        try {
            setIsSubmittingThumbsUp(true);

            // Check if user is authenticated
            if (!isUserAuthenticated || !authToken) {
                throw new Error('User not authenticated');
            }

            const response = await fetch(`${API_BASE_URL}/api/feedback/analysis/${analysisResult.analysisId}/submit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`,
                },
                body: JSON.stringify({
                    rating: "THUMBS_UP",
                    comment: ""
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Thank you for your positive feedback! Your input helps us improve.');
            } else {
                throw new Error(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Failed to submit feedback:', error);
            alert('Failed to submit feedback. Please try again.');
        } finally {
            setIsSubmittingThumbsUp(false);
        }
    };

    const handleThumbsDown = () => {
        setShowFeedback(true);
    };

    const submitFeedback = async () => {
        if (!feedbackText.trim()) return;
        
        try {
            setIsSubmittingFeedback(true);

            // Check if user is authenticated
            if (!isUserAuthenticated || !authToken) {
                throw new Error('User not authenticated');
            }

            const response = await fetch(`${API_BASE_URL}/api/feedback/analysis/${analysisResult.analysisId}/submit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`,
                },
                body: JSON.stringify({
                    rating: "THUMBS_DOWN",
                    comment: feedbackText
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                setFeedbackText('');
                setShowFeedback(false);
                alert('Thank you for your feedback! Your input helps us improve.');
            } else {
                throw new Error(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Failed to submit feedback:', error);
            alert('Failed to submit feedback. Please try again.');
        } finally {
            setIsSubmittingFeedback(false);
        }
    };

    //-------------------
    //history management
    //-------------------
    const fetchSubmissionDetails = async (submissionId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/submissions/${submissionId}/`, {
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Fetched submission details:', data); // Debug log
            
            if (data.success) {
                const submission = data.data.submission;
                const detailedItem = convertSubmissionToHistoryItem(submission);

                // Update the specific item in history with full details
                setHistoryItems(prev => prev.map(h => 
                    h.id === submissionId ? detailedItem : h
                ));

                return detailedItem;
            }

            throw new Error('Failed to fetch submission details');
        } catch (error) {
            console.error(`Failed to fetch submission details for ${submissionId}:`, error);
            throw error;
        }
    };

    // Convert a submission payload into a history item with result.
    const convertSubmissionToHistoryItem = (submission) => {
        const analysis = submission.analysis_result;
        
        // Check if this is an image submission
        const isImageSubmission = submission.image_url || submission.type === 'image';
        
        if (isImageSubmission) {
            // Handle image submission format
            return {
                id: submission.id,
                type: 'image',
                title: truncateText(submission.name, 25),
                fullTitle: submission.name,
                date: new Date(submission.created_at).toLocaleString(),
                content: 'Image analysis result',
                isLoaded: true,
                result: {
                    isAI: analysis.prediction?.is_ai_generated || analysis.detection_result === 'AI_GENERATED',
                    confidence: Math.round((analysis.prediction?.confidence || analysis.confidence || 0) * 100),
                    detectionReasons: analysis.analysis?.detection_reasons || analysis.detection_reasons || [],
                    analysisId: analysis.analysis_id || analysis.id,
                    isImage: true,
                    imageUrl: submission.image_url,
                    dimensions: submission.dimensions,
                    fileSize: submission.file_size_mb,
                    filename: submission.name,
                    metadata: analysis.metadata || {}
                }
            };
        } else {
            // Handle text submission format (existing logic)
            const highlightedText = generateHighlightedText(
                submission.content,
                analysis.analysis_details
            );

            return {
                id: submission.id,
                type: 'text',
                title: truncateText(submission.name, 25),
                fullTitle: submission.name,
                date: new Date(submission.created_at).toLocaleString(),
                content: submission.content?.substring(0, 100) + '...',
                isLoaded: true,
                result: {
                    isAI: analysis.detection_result === 'AI_GENERATED',
                    confidence: Math.round(analysis.confidence * 100),
                    highlightedText,
                    detectionReasons: analysis.detection_reasons || [],
                    statistics: {
                        totalWords: analysis.statistics?.total_words,
                        sentences: analysis.statistics?.sentences,
                        avgSentenceLength: analysis.statistics?.avg_sentence_length,
                        aiKeywordsCount: analysis.statistics?.ai_keywords_count,
                        transitionWordsCount: analysis.statistics?.transition_words_count,
                        corporateJargonCount: analysis.statistics?.corporate_jargon_count,
                        buzzwordsCount: analysis.statistics?.buzzwords_count,
                        suspiciousPatternsCount: analysis.statistics?.suspicious_patterns_count,
                        humanIndicatorsCount: analysis.statistics?.human_indicators_count,
                    },
                    analysisDetails: {
                        foundKeywords: analysis.analysis_details?.found_keywords || [],
                        foundPatterns: analysis.analysis_details?.found_patterns || [],
                        foundTransitions: analysis.analysis_details?.found_transitions || [],
                        foundJargon: analysis.analysis_details?.found_jargon || [],
                        foundBuzzwords: analysis.analysis_details?.found_buzzwords || [],
                        foundHumanIndicators: analysis.analysis_details?.found_human_indicators || [],
                    },
                    analysisId: analysis.analysis_id,
                }
            };
        }
    };

    const viewHistoryItem = async (item) => {
        try {
            setSelectedHistoryItem({ ...item, isLoading: true });
            setCurrentView('history-detail');

            const needsFetch = !item?.result || !item?.isLoaded;
            const detailedItem = needsFetch ? await fetchSubmissionDetails(item.id) : item;

            setSelectedHistoryItem({ ...detailedItem, isLoading: false });
        } catch (error) {
            console.error('Failed to load history item details:', error);
            alert('Failed to load history item details. Please try again.');
            setSelectedHistoryItem(null);
            setCurrentView('main');
        }
    };

    const deleteHistoryItem = async (id) => {
        try {
            updateHistoryItemState(id, { isDeleting: true });

            const response = await fetch(`${API_BASE_URL}/api/submissions/${id}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                setHistoryItems(prev => prev.filter(item => item.id !== id));
                // Clean up the state for this item
                setHistoryItemStates(prev => {
                    const newState = { ...prev };
                    delete newState[id];
                    return newState;
                });
            } else {
                throw new Error('Failed to delete history item');
            }
        } catch (error) {
            console.error('Failed to delete history item:', error);
            alert('Failed to delete history item. Please try again.');
        } finally {
            updateHistoryItemState(id, { isDeleting: false });
        }
    };

    const resetAnalysis = () => {
        setAnalysisResult(null);
        setTextContent('');
        setUploadedImage(null);
        setUploadedFile(null);
        setIsFileUploaded(false);
        if (fileInputRef.current){
            fileInputRef.current.value = '';
        }
        if (imageInputRef.current){
            imageInputRef.current.value = '';
        }
    };

    // Helper function to update individual item state
    const updateHistoryItemState = (itemId, updates) => {
        setHistoryItemStates(prev => ({
            ...prev,
            [itemId]: { ...prev[itemId], ...updates }
        }));
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
        {id: 'manage-user', label: 'Manage Account', icon: <Settings className="icon-sm"/>},
        {id: '', label: 'Landing Page', icon: <Home className="icon-sm"/>}
    ];

    // PDF export function
    const exportReportAsPDF = async (analysisId) => {
        try {
            setIsPDFExporting(true);
            
            if (!analysisId) {
                throw new Error('No submission ID provided for export');
            }

            if (!isUserAuthenticated || !authToken) {
                throw new Error('User not authenticated');
            }

            const response = await fetch(`${API_BASE_URL}/api/reports/analysis/${analysisId}/download/`, {
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Get the blob from the response
            const blob = await response.blob();
            
            // Create a download link
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            
            // Set filename
            const filename = `analysis-report-${analysisId.slice(0, 8)}.pdf`;
            link.download = filename;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            
            // Cleanup
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Failed to export PDF:', error);
            alert('Failed to export PDF. Please try again.');
        } finally {
            setIsPDFExporting(false);
        }
    };

    // Export Report as Email
    const exportReportAsEmail = async (analysisId) => {
        try {
            setIsEmailSending(true);
            
            if (!analysisId) {
                throw new Error('No submission ID provided for export');
            }

            if (!isUserAuthenticated || !authToken) {
                throw new Error('User not authenticated');
            }

            const response = await fetch(`${API_BASE_URL}/api/reports/analysis/${analysisId}/email/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                console.log('Email sent successfully:', result.message);
                console.log('Recipient:', result.data.recipient);
                alert("Email Sent successfully!")
            } else {
                throw new Error(result.error || 'Failed to send email');
            }
            
        } catch (error) {
            console.error('Failed to send email:', error);
            alert('Failed to send email. Please try again.');
        } finally {
            setIsEmailSending(false);
        }
    };

    return (
        <div className="detective-container">
            

            {/*sidebar*/}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="detective-logo">
                        <div className="logo-icon">
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
                        
                        {/*search bar*/}
                        <div className="history-search-container">
                            <div className="history-search-input-wrapper">
                                <Search className="icon-xs search-icon" />
                                <input
                                    type="text"
                                    placeholder="Search detections..."
                                    value={searchQuery}
                                    onChange={handleSearchChange}
                                    className="history-search-input"
                                />
                                {searchQuery && (
                                    <button
                                        onClick={clearSearch}
                                        className="clear-search-btn"
                                    >
                                        <X className="icon-xs" />
                                    </button>
                                )}
                            </div>
                        </div>
                        
                        {/* History Loading Indicator */}
                        {isHistoryLoading && (
                            <div className="history-loading">
                                <div className="history-loading-spinner">
                                    <Loader className="icon-sm animate-spin" />
                                </div>
                                <div className="history-loading-text">Loading detections...</div>
                            </div>
                        )}
                        
                        {/* History Items */}
                        {!isHistoryLoading && filteredHistoryItems.map((item) => {
                            const itemState = historyItemStates[item.id] || {};
                            return (
                                <div key={item.id} className="history-item">
                                    <div className="history-content" onClick={() => viewHistoryItem(item)}>
                                        {item.type === 'text' ?
                                            <FileText className="icon-xs" /> :
                                            <ImageIcon className="icon-xs" />
                                        }
                                        <div>
                                            <div 
                                                className="history-text"
                                                title={item.fullTitle || item.title}
                                            >
                                                {item.title}
                                            </div>
                                            <div style={{fontSize: '0.75rem', color: '#6b7280'}}>
                                                {item.date}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="history-actions">
                                        <button 
                                            className="history-action"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (item.result?.analysisId) {
                                                    updateHistoryItemState(item.id, { isExporting: true });
                                                    exportReportAsPDF(item.result.analysisId)
                                                        .finally(() => updateHistoryItemState(item.id, { isExporting: false }));
                                                } else {
                                                    alert('Analysis ID not available. Please view the item first.');
                                                }
                                            }}
                                            disabled={itemState.isExporting || itemState.isDeleting}
                                        >
                                            {itemState.isExporting ? (
                                                <Loader className="icon-xs animate-spin" />
                                            ) : (
                                                <Download className="icon-xs"/>
                                            )}
                                        </button>
                                        <button
                                            className="history-action"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (window.confirm('Are you sure you want to delete this analysis?')) {
                                                    deleteHistoryItem(item.id);
                                                }
                                            }}
                                            disabled={itemState.isExporting || itemState.isDeleting}
                                        >
                                            {itemState.isDeleting ? (
                                                <Loader className="icon-xs animate-spin" />
                                            ) : (
                                                <Trash2 className="icon-xs"/>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </nav>
            </div>



            {/*header*/}
            <header className={`detective-header ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="detective-header-inner">
                    <div className="header-left">
                        {/*Menu toggle button*/}
                        {!sidebarOpen && (
                            <button
                                className={`menu-toggle`}
                                onClick={toggleSidebar}
                            >
                                <Menu className="icon-sm"/>
                            </button>
                        )}
                        {/*logo*/}
                        <div className="detective-logo">
                            <div className="logo-icon">
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
                                                            Analysing...
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
                                            <div className="upload-area" onClick={!isFileUploaded ? () => fileInputRef.current?.click() : undefined}>
                                                {!isFileUploaded ? (
                                                    <>
                                                        <div className="upload-icon">
                                                            <FileText className="icon-lg" />
                                                        </div>
                                                        <h3 className="upload-title">Upload Document</h3>
                                                        <p className="upload-description">
                                                            Click here or drag and drop PDF, DOCX or TXT files (up to 25MB)
                                                        </p>
                                                        <button className="upload-button">
                                                            <Upload className="icon-sm" />
                                                            Choose Document
                                                        </button>
                                                    </>
                                                ) : (
                                                    <div className="upload-success">
                                                        <div className="upload-success-icon">
                                                            <CheckCircle className="icon-lg" />
                                                        </div>
                                                        <h3 className="upload-success-title">File Uploaded Successfully!</h3>
                                                        <div className="upload-file-info">
                                                            <p className="file-name">{uploadedFile?.name}</p>
                                                            <p className="file-size">{uploadedFile?.size} MB</p>
                                                        </div>
                                                    </div>
                                                )}
                                                <input
                                                    ref={fileInputRef}
                                                    type="file"
                                                    className="file-input"
                                                    accept=".pdf,.docx,.txt"
                                                    onChange={handleFileUpload}
                                                />
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Image Upload Area */}
                                {activeDetectionType === 'image' && (
                                    <div className="upload-area" onClick={!isFileUploaded ? () => imageInputRef.current?.click() : undefined}>
                                        {!isFileUploaded ? (
                                            <>
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
                                            </>
                                        ) : (
                                            <div className="upload-success">
                                                <div className="upload-success-icon">
                                                    <CheckCircle className="icon-lg" />
                                                </div>
                                                <h3 className="upload-success-title">Image Uploaded Successfully!</h3>
                                                <div className="upload-file-info">
                                                    <p className="file-name">{uploadedFile?.name}</p>
                                                    <p className="file-size">{uploadedFile?.size} MB</p>
                                                </div>
                                                {uploadedImage && (
                                                    <div className="uploaded-image-preview">
                                                        <img src={uploadedImage} alt="Uploaded preview" className="preview-image" />
                                                    </div>
                                                )}
                                            </div>
                                        )}
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
                                            {activeDetectionType === 'text' ? 'Analysing text patterns...' : 'Processing image...'}
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
                                                    
                                                    <div className="results-actions">
                                                        <button 
                                                            className="action-btn export" 
                                                            onClick={() => exportReportAsPDF(analysisResult.analysisId)}
                                                            disabled={isPDFExporting || isEmailSending}
                                                        >
                                                            {isPDFExporting ? (
                                                                <>
                                                                    <Loader className="icon-sm animate-spin" />
                                                                    Exporting...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Download className="icon-sm" />
                                                                    Export PDF
                                                                </>
                                                            )}
                                                        </button>
                                                        <button 
                                                            className="action-btn" 
                                                            onClick={() => exportReportAsEmail(analysisResult.analysisId)}
                                                            disabled={isPDFExporting || isEmailSending}
                                                        >
                                                            {isEmailSending ? (
                                                                <>
                                                                    <Loader className="icon-sm animate-spin" />
                                                                    Sending...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Mail className="icon-sm" />
                                                                    Email
                                                                </>
                                                            )}
                                                        </button>
                                                    </div>
                                                </div>
                                                
                                                {uploadedImage && (
                                                    <img src={uploadedImage} alt="Uploaded" className="result-image" />
                                                )}
                                                
                                                {/* Detection Factors for Images */}
                                                <div className="report-section">
                                                    <div className="section-header">
                                                        <Brain className="icon-sm" />
                                                        <h4 className="section-title">Detection Factors</h4>
                                                    </div>
                                                    <div className="factors-list">
                                                        {analysisResult.detectionReasons.map((reason, index) => (
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
                                                
                                                {/* Feedback buttons */}
                                                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
                                                    <button 
                                                        className="action-btn" 
                                                        onClick={handleThumbsUp}
                                                        disabled={isSubmittingThumbsUp || isSubmittingFeedback}
                                                        style={{ background: 'linear-gradient(135deg, #10b981, #059669)', color: 'white' }}
                                                    >
                                                        {isSubmittingThumbsUp ? (
                                                            <>
                                                                <Loader className="icon-sm animate-spin" />
                                                                Submitting...
                                                            </>
                                                        ) : (
                                                            <>
                                                                <ThumbsUp className="icon-sm" />
                                                                Accurate
                                                            </>
                                                        )}
                                                    </button>
                                                    <button 
                                                        className="action-btn" 
                                                        onClick={handleThumbsDown}
                                                        disabled={isSubmittingThumbsUp || isSubmittingFeedback}
                                                    >
                                                        <ThumbsDown className="icon-sm" />
                                                        Not Accurate
                                                    </button>
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
                                                        <button 
                                                            className="action-btn export" 
                                                            onClick={() => exportReportAsPDF(analysisResult.analysisId)}
                                                            disabled={isPDFExporting || isEmailSending}
                                                        >
                                                            {isPDFExporting ? (
                                                                <>
                                                                    <Loader className="icon-sm animate-spin" />
                                                                    Exporting...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Download className="icon-sm" />
                                                                    Export PDF
                                                                </>
                                                            )}
                                                        </button>
                                                        <button 
                                                            className="action-btn" 
                                                            onClick={() => exportReportAsEmail(analysisResult.analysisId)}
                                                            disabled={isPDFExporting || isEmailSending}
                                                        >
                                                            {isEmailSending ? (
                                                                <>
                                                                    <Loader className="icon-sm animate-spin" />
                                                                    Sending...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Mail className="icon-sm" />
                                                                    Email
                                                                </>
                                                            )}
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
                                                        onClick={handleThumbsUp}
                                                        disabled={isSubmittingThumbsUp || isSubmittingFeedback}
                                                        style={{ background: 'linear-gradient(135deg, #10b981, #059669)', color: 'white' }}
                                                    >
                                                        {isSubmittingThumbsUp ? (
                                                            <>
                                                                <Loader className="icon-sm animate-spin" />
                                                                Submitting...
                                                            </>
                                                        ) : (
                                                            <>
                                                                <ThumbsUp className="icon-sm" />
                                                                Accurate
                                                            </>
                                                        )}
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
                    <h2 className="history-detail-title">{selectedHistoryItem?.fullTitle || selectedHistoryItem?.title}</h2>
                    <button className="back-button" onClick={() => setCurrentView('main')}>
                        <ArrowLeft className="icon-sm" />
                        Back to Main
                    </button>
                </div>

                {selectedHistoryItem && (
                    <>
                        {(selectedHistoryItem.isLoading || !selectedHistoryItem.result) ? (
                            <div className="results-container" style={{ position: 'relative', minHeight: '240px' }}>
                                <div style={{
                                    position: 'absolute',
                                    inset: 0,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    flexDirection: 'column',
                                    background: 'rgba(255, 255, 255, 0.55)',
                                    backdropFilter: 'blur(2px)',
                                    zIndex: 10,
                                    borderRadius: '0.75rem'
                                }}>
                                    <div className="loading-spinner"></div>
                                    <div className="loading-text">Loading analysis...</div>
                                </div>
                            </div>
                        ) : (
                            <div className="results-container">
                                <div className="results-header">
                                    <div className="detection-result">
                                        <div className={`result-icon ${selectedHistoryItem.result.isAI ? 'ai-detected' : 'human-written'}`}>
                                            {selectedHistoryItem.result.isAI ? <AlertCircle className="icon-md text-white" /> : <CheckCircle className="icon-md text-white" />}
                                        </div>
                                        <div>
                                            <div className={`result-status ${selectedHistoryItem.result.isAI ? 'ai-detected' : 'human-written'}`}>
                                                {selectedHistoryItem.result.isAI ? 
                                                    (selectedHistoryItem.result.isImage ? 'AI Generated' : 'AI Generated Content Detected') : 
                                                    (selectedHistoryItem.result.isImage ? 'Likely Human Created' : 'Likely Human Written')
                                                }
                                            </div>
                                            <div className="result-confidence">
                                                Confidence: {selectedHistoryItem.result.confidence}%
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="results-actions">
                                        <button 
                                            className="action-btn export" 
                                            onClick={() => exportReportAsPDF(selectedHistoryItem.result.analysisId)}
                                            disabled={isPDFExporting || isEmailSending}
                                        >
                                            {isPDFExporting ? (
                                                <>
                                                    <Loader className="icon-sm animate-spin" />
                                                    Exporting...
                                                </>
                                            ) : (
                                                <>
                                                    <Download className="icon-sm" />
                                                    Export PDF
                                                </>
                                            )}
                                        </button>
                                        <button 
                                            className="action-btn" 
                                            onClick={() => exportReportAsEmail(selectedHistoryItem.result.analysisId)}
                                            disabled={isPDFExporting || isEmailSending}
                                        >
                                            {isEmailSending ? (
                                                <>
                                                    <Loader className="icon-sm animate-spin" />
                                                    Sending...
                                                </>
                                            ) : (
                                                <>
                                                    <Mail className="icon-sm" />
                                                    Email
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>

                                {/* Display image if it's an image submission */}
                                {selectedHistoryItem.result.isImage && selectedHistoryItem.result.imageUrl && (
                                    <div className="image-container">
                                        <img 
                                            src={selectedHistoryItem.result.imageUrl} 
                                            alt="Analyzed image" 
                                            className="result-image"
                                        />
                                    </div>
                                )}

                                {selectedHistoryItem.result.isImage ? (
                                    // Image analysis results - show detection factors only
                                    <>
                                        {selectedHistoryItem.result.detectionReasons && selectedHistoryItem.result.detectionReasons.length > 0 && (
                                            <div className="report-section">
                                                <div className="section-header">
                                                    <Brain className="icon-sm" />
                                                    <h4 className="section-title">Detection Factors</h4>
                                                </div>
                                                <div className="factors-list">
                                                    {selectedHistoryItem.result.detectionReasons.map((reason, index) => (
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
                                        )}
                                    </>
                                ) : (
                                    // Text analysis results - show full analysis report
                                    <>
                                        {/* Enhanced Analysis Report for text only */}
                                        <div ref={reportRef}>
                                            <AnalysisReport result={selectedHistoryItem.result} />
                                        </div>

                                        {/* Show highlighted text for text submissions */}
                                        {selectedHistoryItem.result.highlightedText && (
                                            <div className="analyzed-text" dangerouslySetInnerHTML={{ __html: selectedHistoryItem.result.highlightedText }} />
                                        )}
                                    </>
                                )}
                            </div>
                        )}
                    </>
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
                            <button 
                                className="modal-btn cancel" 
                                onClick={() => setShowFeedback(false)}
                                disabled={isSubmittingFeedback}
                            >
                                Cancel
                            </button>
                            <button 
                                className="modal-btn submit" 
                                onClick={submitFeedback}
                                disabled={isSubmittingFeedback || !feedbackText.trim()}
                            >
                                {isSubmittingFeedback ? (
                                    <>
                                        <Loader className="icon-sm animate-spin" />
                                        Submitting...
                                    </>
                                ) : (
                                    'Submit Feedback'
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
export default DetectivePage;