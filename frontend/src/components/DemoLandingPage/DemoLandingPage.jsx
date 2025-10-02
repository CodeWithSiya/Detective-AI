import React, { useState, useEffect } from 'react';
import './DemoLandingPage.css';
import Logo from '../../assets/images/Logo.png';
import DetectiveBg from '../../assets/images/vecteezy.jpg';
import { ChevronRight, Search, Eye, Shield, Zap, Award, Clock, Users, Image as BarChart3, Target, History, FileSearch, Download, Loader2 } from 'lucide-react';
import { Link as RouterLink } from "react-router-dom";


const DemoLandingPage = () => {
    const [isVisible, setIsVisible] = useState(false);
    const [isDownloading, setIsDownloading] = useState(false);

    useEffect(() => {
        setIsVisible(true);
    }, []);

    // Function to handle user manual download
    const handleDownloadManual = async () => {
        setIsDownloading(true);
        try {
            // Create a link element to trigger download
            const link = document.createElement('a');
            link.href = '/DetectiveAI_User_Manual.pdf';
            link.download = 'DetectiveAI_User_Manual.pdf';
            link.target = '_blank';
            
            // Append to body, click, and remove
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Add a small delay to show loading state
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.error('Error downloading manual:', error);
        } finally {
            setIsDownloading(false);
        }
    };

    const features = [
        {
            icon: <Eye className="icon-lg" />,
            title: "Advanced Detection",
            description: "AI models identify generated content with ~85% accuracy",
            gradient: "gradient-blue-cyan"
        },
        {
            icon: <Shield className="icon-lg" />,
            title: "Secure Analysis",
            description: "Your content is analysed securely with encrypted processing and storage",
            gradient: "gradient-purple-pink"
        },
        {
            icon: <Zap className="icon-lg" />,
            title: "Reasonably Fast",
            description: "Get detection results in under 15 seconds for text and 20 seconds for images",
            gradient: "gradient-yellow-orange"
        }
    ];

    const stats = [
        { number: "85%+", label: "Accuracy Rate", icon: <Award className="icon-md"/>},
        { number: "<15%", label: "False Positive", icon: <Shield className="icon-md" /> },
        { number: "20s", label: "Analysis Time", icon: <Clock className="icon-md" /> },
    ];

    const showcaseFeatures = [
        {
            icon: <History className="icon-md" />,
            title: "Analysis History",
            description: "Track all your previous detections with organized sidebar history",
            type: "video",
            content: "/history.mp4",
            thumbnail: "/history-img.png"
        },
        {
            icon: <Target className="icon-md" />,
            title: "Keyword Highlighting",
            description: "AI-generated content highlighted with intelligent keyword detection",
            type: "video", 
            content: "/highlight-text-vid.mp4",
            thumbnail: "/highlighted-text.png"
        },
        {
            icon: <FileSearch className="icon-md" />,
            title: "Detailed Analysis",
            description: "Comprehensive breakdown of detection results and explanations",
            type: "image",
            content: "/detection-factors.png"
        },
        {
            icon: <BarChart3 className="icon-md" />,
            title: "Confidence Score",
            description: "Visual confidence indicators showing detection accuracy levels",
            type: "image",
            content: "/confidence-analysis.png"
        }
    ];

    const demoContent = [
        {
            type: "text",
            title: "Text Detection Demo",
            description: "See how we identify AI-generated text patterns",
            preview: "This cutting-edge technology seamlessly integrates artificial intelligence with advanced machine learning algorithms..."
            },
            {
            type: "image", 
            title: "Image Detection Demo",
            description: "Advanced analysis of AI-generated images",
            preview: "Upload any image to detect AI-generated content."
        }
    ];

    return (
        <div className="demo-container">
            {/*Header*/}
            <header className="demo-header">
                <div className="demo-header-inner">
                    {/*Logo*/}
                    <div className="demo-logo">
                        <div className="relative">
                            <div className="demo-logo-icon">
                                <img src={Logo} alt="Detective AI Logo" className="logo-img"/>
                                {/*<Search className="icon-md text-white" />*/}
                            </div>
                        </div>
                        <div>
                            <h1 className="demo-title">Detective AI</h1>
                            <p className="demo-subtitle">Content Detection</p>
                        </div>
                    </div>

                    {/*Sign in button*/}
                    <div className="header-buttons">
                        <RouterLink to="login">
                            <button className="btn-signin">
                                <span>Sign In</span>
                                <ChevronRight className="icon-sm" />
                            </button>
                        </RouterLink>
                    </div>
                </div>
            </header>

            {/*hero section */}
            <section className="hero">
                <div className={`hero-inner ${isVisible ? 'visible' : 'hidden'}`} style={{position: 'relative', overflow: 'hidden'}}>
                    {/* Detective background image */}
                    <img 
                        src={DetectiveBg} 
                        alt="Detective background" 
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            opacity: 0.07,
                            zIndex: 0,
                            pointerEvents: 'none',
                            maskImage: 'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(0,0,0,1) 35%, rgba(0,0,0,0) 100%)',
                            WebkitMaskImage: 'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(0,0,0,1) 35%, rgba(0,0,0,0) 100%)',
                        }}
                    />
                    <div style={{position: 'relative', zIndex: 1}}>
                        <div className="hero-badge">
                            <Shield className="icon-sm text-blue" />
                            <span>Trusted by UCT & Academic Institutions</span>
                        </div>
                        <h1 className="hero-heading">
                            Detect AI-Generated
                            <span className="hero-heading-gradient">
                                Content with Precision
                            </span>
                        </h1>
                        <p className="hero-text">
                            Advanced AI detection technology that identifies machine-generated text and images. 
                            Built for students, educators, and professionals who demand reliability.
                        </p>
                        {/* Action Buttons */}
                        <div className="hero-buttons">
                            <RouterLink to="/detective-basic">
                                <button className="btn-primary">
                                    <Eye className="icon-sm" />
                                    <span>Enter Detective Mode</span>
                                    <ChevronRight className="icon-sm" />
                                </button>
                            </RouterLink>
                            <button 
                                className="btn-secondary" 
                                onClick={handleDownloadManual}
                                disabled={isDownloading}
                            >
                                {isDownloading ? (
                                    <>
                                        <Loader2 className="icon-sm animate-spin" />
                                        <span>Downloading...</span>
                                    </>
                                ) : (
                                    <>
                                        <Download className="icon-sm" />
                                        <span>User Manual</span>
                                    </>
                                )}
                            </button>
                        </div>
                        {/* Performance Stats */}
                        <div className="stats-grid">
                            {stats.map((stat, i) => (
                                <div key={i} className={`stat-card ${isVisible ? 'visible' : 'hidden'}`} style={{transitionDelay: `${i * 100}ms`}}>
                                    <div className="stat-icon">{stat.icon}</div>
                                    <div className="stat-number">{stat.number}</div>
                                    <div className="stat-label">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>
            
            {/* Video Showcase Section */}
            <section className="video-showcase">
                <div className="video-showcase-inner">
                    <div className="video-stack">
                        {/* Top Video - Text Detection */}
                        <div 
                            className="video-container top"
                            onMouseEnter={(e) => {
                                e.currentTarget.style.zIndex = '10';
                                e.currentTarget.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.zIndex = '1';
                                e.currentTarget.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                            }}
                        >
                            <div className="macbook-container">
                                {/* Top bar */}
                                <div className="macbook-topbar">
                                    <div className="macbook-buttons">
                                        <span className="macbook-btn macbook-btn-red"></span>
                                        <span className="macbook-btn macbook-btn-yellow"></span>
                                        <span className="macbook-btn macbook-btn-green"></span>
                                    </div>
                                    <div className="macbook-title">Text Detection - Detective AI</div>
                                </div>
                                
                                {/* Screen */}
                                <div className="macbook-screen">
                                    <video 
                                        className="demo-video"
                                        autoPlay 
                                        muted 
                                        loop
                                        playsInline
                                    >
                                        <source src="/text-notai.mp4" type="video/mp4" />
                                        Your browser does not support the video tag.
                                    </video>
                                </div>
                                
                                {/* Bottom curve */}
                                <div className="macbook-bottom"></div>
                            </div>
                        </div>
                        
                        {/* Bottom Video - Image Detection */}
                        <div 
                            className="video-container bottom"
                            onMouseEnter={(e) => {
                                e.currentTarget.style.zIndex = '10';
                                e.currentTarget.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.zIndex = '2';
                                e.currentTarget.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                            }}
                        >
                            <div className="macbook-container">
                                {/* Top bar */}
                                <div className="macbook-topbar">
                                    <div className="macbook-buttons">
                                        <span className="macbook-btn macbook-btn-red"></span>
                                        <span className="macbook-btn macbook-btn-yellow"></span>
                                        <span className="macbook-btn macbook-btn-green"></span>
                                    </div>
                                    <div className="macbook-title">Image Detection - Detective AI</div>
                                </div>
                                
                                {/* Screen */}
                                <div className="macbook-screen">
                                    <video 
                                        className="demo-video"
                                        autoPlay 
                                        muted 
                                        loop
                                        playsInline
                                    >
                                        <source src="/image-upload-ai.mp4" type="video/mp4" />
                                        Your browser does not support the video tag.
                                    </video>
                                </div>
                                
                                {/* Bottom curve */}
                                <div className="macbook-bottom"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/*feature section*/}
            <section className="features">
                <div className="features-inner">
                    <div className="features-header">
                        <h2 className="section-heading">
                        Why Choose Detective AI?
                        </h2>
                        <p className="section-subtext">
                            Our advanced detection system combines multiple AI models with forensic analysis 
                            to provide the most accurate content detection available.
                        </p>
                    </div>

                    <div className="features-grid">
                        {features.map((feature, i) => (
                            <div key={i} className="feature-card">
                                <div className={`feature-icon ${feature.gradient}`}>{feature.icon}</div>
                                <h3 className="feature-title">{feature.title}</h3>
                                <p className="feature-text">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Showcase Section */}
            <section className="features-showcase">
                <div className="features-showcase-inner">
                    <div className="features-header">
                        <h2 className="section-heading">
                            Experience Our Powerful Features
                        </h2>
                        <p className="section-subtext">
                            Discover the comprehensive tools that make Detective AI one of the the best content detection platforms.
                        </p>
                    </div>

                    <div className="showcase-grid">
                        {showcaseFeatures.map((feature, i) => (
                            <div 
                                key={i} 
                                className="showcase-card"
                                onMouseEnter={(e) => {
                                    if (feature.type === 'video') {
                                        const card = e.currentTarget;
                                        const thumbnail = card.querySelector('.showcase-thumbnail');
                                        const video = card.querySelector('.showcase-video');
                                        if (thumbnail && video) {
                                            thumbnail.style.display = 'none';
                                            video.style.display = 'block';
                                            video.play();
                                        }
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (feature.type === 'video') {
                                        const card = e.currentTarget;
                                        const thumbnail = card.querySelector('.showcase-thumbnail');
                                        const video = card.querySelector('.showcase-video');
                                        if (thumbnail && video) {
                                            video.pause();
                                            video.currentTime = 0;
                                            video.style.display = 'none';
                                            thumbnail.style.display = 'block';
                                        }
                                    }
                                }}
                            >
                                <div className="showcase-header">
                                    <div className="showcase-icon">
                                        {feature.icon}
                                    </div>
                                    <h3 className="showcase-title">{feature.title}</h3>
                                </div>
                                
                                <p className="showcase-description">
                                    {feature.description}
                                </p>
                                
                                <div className="showcase-content">
                                    {feature.type === 'video' ? (
                                        <div className="video-container-showcase">
                                            {/* Thumbnail image - shown by default */}
                                            <img 
                                                className="showcase-thumbnail"
                                                src={feature.thumbnail}
                                                alt={`${feature.title} preview`}
                                                onError={(e) => {
                                                    // If thumbnail fails to load, hide it and show video
                                                    e.target.style.display = 'none';
                                                    e.target.nextSibling.style.display = 'block';
                                                }}
                                            />
                                            {/* Video - hidden by default, shows on hover */}
                                            <video 
                                                className="showcase-video"
                                                muted 
                                                loop
                                                playsInline
                                                style={{ display: 'none' }}
                                            >
                                                <source src={feature.content} type="video/mp4" />
                                                Your browser does not support the video tag.
                                            </video>
                                        </div>
                                    ) : feature.type === 'image' ? (
                                        <img 
                                            className="showcase-image"
                                            src={feature.content}
                                            alt={feature.title}
                                            onError={(e) => {
                                                e.target.style.display = 'none';
                                                e.target.nextSibling.style.display = 'flex';
                                            }}
                                        />
                                    ) : null}
                                    
                                    {/* Fallback placeholder */}
                                    <div className="showcase-placeholder" style={{ display: 'none' }}>
                                        <div className="placeholder-content">
                                            <div className="placeholder-icon">
                                                {feature.icon}
                                            </div>
                                            <div className="placeholder-text">
                                                {feature.type === 'video' ? 'Video Preview' : 'Image Preview'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>


            {/*cta section*/}
            <section className="cta">
                <div className="cta-inner">
                    <h2 className="section-heading">
                        Ready to Start Your Investigation?
                    </h2>
                    <p className="section-subtext">
                        Join thousands of users who trust Detective AI for accurate content detection
                    </p>
                
                    <div className="cta-buttons">
                        <RouterLink to="/detective-basic">
                            <button className="btn-primary">
                                <Search className="icon-sm" />
                                <span>Start Detection</span>
                                <ChevronRight className="icon-sm" />
                            </button>
                        </RouterLink>
                        
                        <div className="header-buttons">
                            <RouterLink to="/signup">
                                <button className="btn-secondary">
                                    <Users className="icon-sm" />
                                    <span>Create Account</span>
                                </button>
                            </RouterLink>
                        </div>

                    </div>
                </div>
            </section>

            {/*footer*/}
            <footer className="demo-footer">
                <div className="footer-inner">
                    <div className="footer-logo">
                        <div className="footer-logo-icon">
                            <Search className="icon-sm text-white" />
                        </div>
                        <span className="footer-title">Detective AI</span>
                    </div>
                    <p className="footer-text">
                        Built by the Deep Detectives team for CSC3003S Capstone Project
                    </p>
                    <p className="footer-subtext">
                        University of Cape Town • Computer Science Department
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default DemoLandingPage;