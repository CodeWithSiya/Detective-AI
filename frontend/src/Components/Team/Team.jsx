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
            </div>



        </div>
    );
}