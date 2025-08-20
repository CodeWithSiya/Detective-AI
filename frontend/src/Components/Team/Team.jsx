import React, {useState} from 'react';
import './Team.css';
import{
    Search,
    Eye,
    X,
    ChevronRight,
    ArrowLeft,
    Mail,
    GitHub,
    Linkedin,
    Users,
    Code,
    Brain,
    Palette,
    Coffe,
    Music,
    Gamepad2,
    Book,
    Camera,
    Headphones,
    Dumbbell,
    Plane,
    Plus,
    FileText,
    Image as ImageIcon,
    BarChart3,
    Play,
    History,
    Share,
    Trash2
} from 'lucide-react';

const Team = ({ onBackToDetective, sidebarOpen, toggleSidebar }) => {
    const [navigationItems] = useState([
        {id: 'detector', label: 'Detector', icon: <Search className="icon-sm"/>},
        {id: 'team', label: 'Team', icon: <Users className="icon-sm"/>, active: true},
        {id: 'dashboard', label: 'Dashboard', icon: <BarChart3 className="icon-sm"/>},
        {id: 'demo', label: 'Demo', icon: <Play className="icon-sm"/>}
    ]);

    const teamMembers = [
        {
            id: 1,
            name: "Siyabonga Madondo",
            initials: "SLM",
            university: "University of Cape Town",
            degree: "BSc Computer Science and Applied Statistics",
            role: "Team Leader & Backend Developer",
            description: "Strong leadership qualities with excellent time management skills. Leads project coordination, backend development, and API integration while ensuring seamless collaboration across the team.",
            interests: ["Leadership", "Backend Development", "APIs", "Database Design", "Project Management"],
            email: "MDNSIY014@myuct.ac.za",
            github: "siyabonga-madondo",
            linkedin: "siyabonga-madondo"
        },
        {
            id: 2,
            name: "Lindokuhle Mdlalose",
            initials: "LBM",
            university: "University of Cape Town",
            degree: "BSc Computer Science and Computer Engineering",
            role: "Architect & Frontend Developer",
            description: "Great in software architecture and frontend development with creative problem-solving abilities. Designs system architecture and creates responsive, user-friendly interfaces.",
            interests: ["Systems Architecture", "Frontend Design", "UI/UX", "React", "Problem Solving"],
            email: "MDLLIN028@myuct.ac.za",
            github: "Lindokuhle239",
            linkedin: "lindokuhle-mdlalose-883ba7265"
        },
        {
            id: 3,
            name: "Ethan Ngwetjana",
            initials: "EN",
            university: "University of Cape Town",
            degree: "BSc Computer Science and Computer Engineering",
            role: "Communicator & AI Engineer",
            description: "Excellent communication skills and attention to detail in documentation. Specializes in AI model research and integration while managing stakeholder communications.",
            interests: ["AI/ML", "Documentation", "Communication", "Model Integration", "Research"],
            email: "NWETH001@myuct.ac.za",
            github: "ethan-ngwetjana",
            linkedin: "ethan-ngwetjana"
        }
    ];

    const teamStats = [
        {number: "3", label: "Team Members"},
        {number: "UCT", label: "University"},
        {number: "CS", label: "Degree Program"},
        {number: "2026", label: "Graduation Year"}
    ];

    const handleNavigation = (itemId) => {
        if (itemId === 'detector'){
            onBackToDetective();
        }
        //other navigation items
    };

    return (
        <div className="team-container">
            {/*menu toggle button*/}
            <button
                className={`menu-toggle ${sidebarOpen ? 'sidebar-open' : ''}`}
                onClick={toggleSidebar}
                style={{
                    position: 'fixed',
                    top: '1rem',
                    left: sidebarOpen ? '300px' : '1rem',
                    zIndex: 70,
                    background: 'linear-gradient(to-right, #1f2937, #7c3aed)',
                    border: none,
                    color: 'white',
                    width: '40px',
                    height: '40px',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                }}
            >
                <X className="icon-md"/>
            </button>

            {/*sidebar*/}
            <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
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
                <button className="new-detection" onClick={() => handleNavigation('detector')}>
                    <Plus className="icon-sm"/>
                    <span>New Detection</span>
                </button>

                {/*navigation*/}
                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">Navigation</div>
                        {navigationItems.map((item) => (
                            <button
                                key={item.id}
                                className={`nav-item ${item.active ? 'active' : ''}`}
                                onClick={() => handleNavigation(item.id)}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                                <ChevronRight className="icon-xs" style={{ marginLeft: 'auto'}}/>
                            </button>
                        ))}
                    </div>

                    {/* History Section */}
                    <div className="nav-section history-section">
                        <div className="nav-section-title">Recent Detections</div>
                        <div className="history-item">
                            <div className="history-content">
                                <FileText className="icon-xs"/>
                                <div>
                                    <div className="history-text">Academic Essay Analysis</div>
                                    <div style={{fontSize: '0.75rem', color: '#6b7280'}}>
                                        2 hours ago
                                    </div>
                                </div>
                            </div>
                            <div className="history-actions">
                                <button className="history-action">
                                    <Share className="icon-xs"/>
                                </button>
                                <button className="history-action">
                                    <Trash2 className="icon-xs"/>
                                </button>
                            </div>
                        </div>
                    </div>
                </nav>
            </div>

            {/*sidebar overlay*/}
            <div
                className={`sidebar-overlay ${sidebarOpen ? 'active' : ''}`}
                onClick={toggleSidebar}
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.3)',
                    zIndex: 55,
                    opacity: sidebarOpen ? 1 : 0,
                    visibility: sidebarOpen ? 'visible' : 'hidden',
                    transition: 'all 0.3s ease'
                }}
            />

            {/* Header */}
            <header className={`team-header ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="team-header-inner">
                    {/* Logo */}
                    <div className="team-logo">
                        <div className="team-logo-icon">
                            <Search className="icon-md text-white"/>
                        </div>
                        <div>
                            <h1 className="team-title">Detective AI</h1>
                            <p className="team-subtitle">Meet Our Team</p>
                        </div>
                    </div>
                    
                    {/* Sign in button */}
                    <button className="btn-signin">
                        <span>Sign In</span>
                        <ChevronRight className="icon-sm"/>
                    </button>
                </div>
            </header>

            {/*main content*/}
            <main className={`team-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
                <div className="team-content">
                    {/*back button*/}
                    <button className="back-button" onClick={onBackToDetective}>
                        <ArrowLeft className="icon-sm"/>
                        Back to Detective
                    </button>

                    {/*page header*/}
                    <div className="page-header">
                        <h1 className="page-title">Meet the Deep Detectives</h1>
                        <p className="page-subtitle">
                            A talented team of Computer Science students from the University of Cape Town, 
                            working together to build AI detection technology.
                        </p>
                    </div>

                    {/*team grid*/}
                    <div className="team-grid">
                        {teamMembers.map((member) =>(
                            <div key={member.id} className="team-card">
                                <div className="member-photo">
                                    {member.initials}
                                </div>

                                <h3 className="member-name">{member.name}</h3>
                                <p className="member-university">{member.university}</p>
                                <p className="member-degree">{member.degree}</p>

                                <div className="member-role">{member.role}</div>

                                <p className="member-description">{member.description}</p>

                                <div className="member-interests">
                                    <div className="interests-title">Areas of Interest</div>
                                    <div className="interests-list">
                                        {member.interests.map((interest, index) => (
                                            <span key={index} className="interest-tag">
                                                {interest}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                
                                <div className="member-links">
                                    <a 
                                        href={`mailto:${member.email}`} 
                                        className="social-link"
                                        title="Email"
                                    >
                                        <Mail className="icon-sm" />
                                    </a>
                                    <a 
                                        href={`https://github.com/${member.github}`} 
                                        className="social-link"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        title="GitHub"
                                    >
                                        <Github className="icon-sm" />
                                    </a>
                                    <a 
                                        href={`https://linkedin.com/in/${member.linkedin}`} 
                                        className="social-link"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        title="LinkedIn"
                                    >
                                        <Linkedin className="icon-sm" />
                                    </a>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/*team stats*/}
                    <div className="team-stats">
                        <h3 className="stats-title">Team Overview</h3>
                        <div className="states-grid">
                            {teamStats.map((stat, index) => (
                                <div key={index} className="stat-item">
                                    <div className="stat-number">{stat.number}</div>
                                    <div className="stat-label">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};
export default Team;