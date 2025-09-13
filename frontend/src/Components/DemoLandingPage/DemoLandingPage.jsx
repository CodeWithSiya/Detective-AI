import React, { useState, useEffect } from 'react';
import './DemoLandingPage.css';
import Logo from '../Assets/Logo.png';
import { ChevronRight, Search, Eye, Shield, Zap, Award, Clock, Users, Play, FileText, Image as ImageIcon } from 'lucide-react';
import { title } from 'framer-motion/client';
import { Link as RouterLink } from "react-router-dom";


const DemoLandingPage = () => {
    const [isVisible, setIsVisible] = useState(false);
    /*const [currentDemo, setCurrentDemo] = useState(0);*/

    useEffect(() => {
        setIsVisible(true);
    }, []);

    const features = [
        {
            icon: <Eye className="icon-lg" />,
            title: "Advanced Detection",
            description: "State-of-art AI models identify generated content with 85% accuracy",
            gradient: "gradient-blue-cyan"
        },
        {
            icon: <Shield className="icon-lg" />,
            title: "Secure Analysis",
            description: "Your content is analyzed securely with encrypted processing and storage",
            gradient: "gradient-purple-pink"
        },
        {
            icon: <Zap className="icon-lg" />,
            title: "Lightning Fast",
            description: "Get detection results in under 10 seconds for text and 30 seconds for images",
            gradient: "gradient-yellow-orange"
        }
    ];

    const stats = [
        { number: "85%+", label: "Accuracy Rate", icon: <Award className="icon-md"/>},
        { number: "<15%", label: "False Positive", icon: <Shield className="icon-md" /> },
        { number: "10s", label: "Analysis Time", icon: <Clock className="icon-md" /> },
        { number: "1000+", label: "Daily Analyses", icon: <Users className="icon-md" /> }
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
                            <div className="demo-logo-badge">
                                <Eye className="icon-xs text-white" />
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
                <div className={`hero-inner ${isVisible ? 'visible' : 'hidden'}`}>
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
                        Advanced AI detection technology that identifies machine-generated text and images 
                        with industry-leading accuracy. Built for students, educators, and professionals who demand reliability.
                    </p>
                    
                    {/* Action Buttons */}
                    <div className="hero-buttons">
                        <RouterLink to="/detective">
                            <button className="btn-primary">
                                <Eye className="icon-sm" />
                                <span>Enter Detective Mode</span>
                                <ChevronRight className="icon-sm" />
                            </button>
                        </RouterLink>
                        
                        <button className="btn-secondary">
                            <Play className="icon-sm" />
                            <span>Watch Demo</span>
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

            {/*demo preview section*/}
            <section className="demo-preview">
                <div className="demo-preview-inner">
                    <div className="features-header">
                        <h2 className="section-header">
                            See Detective AI in Action
                        </h2>
                        <p className="section-subtext">
                            Experience the power of our detection technology
                        </p>
                    </div>

                    <div className="demo-grid">
                        {demoContent.map((demo, i) => (
                            <div key={i} className="demo-card">
                                <div className="demo-card-header">
                                    <div className="demo-icon">
                                        {demo.type === 'text' ? <FileText className="icon-md" /> : <ImageIcon className="icon-md"/>}
                                    </div>
                                    <div>
                                        <h3 className="demo-title">{demo.title}</h3>
                                        <p className="demo-subtitle">{demo.description}</p>
                                    </div>
                                </div>
                                <div className="demo-preview-box">
                                    <p>{demo.preview}</p>
                                </div>
                                <button className="btn-demo">
                                    <Play className="icon-sm"/>
                                    <span>Try This Demo</span>
                                </button>
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
                        <RouterLink to="/detective">
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