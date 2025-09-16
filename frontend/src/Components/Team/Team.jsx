import React from 'react';
import './Team.css';
import siyaImg from '../Assets/siya.jpg';
import lindoImg from '../Assets/lindo.jpg';
import ethanImg from '../Assets/ethan.jpg';
import Logo from '../Assets/Logo.png';
import { Link as RouterLink } from "react-router-dom";
import { ArrowLeft, Mail, Github, Linkedin } from 'lucide-react';

const Team = ({ onBackToDetective }) => {
    const teamMembers = [
        {
            id: 1,
            name: "Siyabonga Madondo",
            photo: siyaImg,
            university: "University of Cape Town",
            degree: "BSc Computer Science and Applied Statistics",
            role: "Team Leader & Backend Developer",
            description: "Strong leadership qualities with excellent time management skills. Leads project coordination, backend development, and API integration while ensuring seamless collaboration across the team.",
            interests: ["Leadership", "Backend Development", "APIs", "Database Design", "Project Management"],
            email: "MDNSIY014@myuct.ac.za",
            github: "CodeWithSiya",
            linkedin: "siyabongamadondo"
        },
        {
            id: 2,
            name: "Lindokuhle Mdlalose",
            photo: lindoImg,
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
            photo: ethanImg,
            university: "University of Cape Town",
            degree: "BSc Computer Science and Computer Engineering",
            role: "Communicator & AI Engineer",
            description: "Excellent communication skills and attention to detail in documentation. Specializes in AI model research and integration while managing stakeholder communications.",
            interests: ["AI/ML", "Documentation", "Communication", "Model Integration", "Research"],
            email: "NWETH001@myuct.ac.za",
            github: "EpicE88",
            linkedin: "ethan-ngwetjana-69430a35a"
        }
    ];

    const teamStats = [
        {number: "3", label: "Team Members"},
        {number: "UCT", label: "University"},
        {number: "CS", label: "Degree Program"},
        {number: "2026", label: "Graduation Year"}
    ];

    return (
        <div className="team-container">
            {/* Header */}
            <header className="team-header">
                <div className="team-header-inner">
                    {/* Logo */}
                    <div className="team-logo">
                        <div className="team-logo-icon">
                            <img src={Logo} alt="Detective AI Logo" className="logo-img"/>
                        </div>
                        <div>
                            <h1 className="team-title">Detective AI</h1>
                            <p className="team-subtitle">Meet Our Team</p>
                        </div>
                    </div>
                </div>
            </header>

            {/*main content*/}
            <main className="team-main">
                <div className="team-content">
                    {/*back button*/}
                    <RouterLink to="/detective">
                        <button className="back-button" onClick={onBackToDetective}>
                            <ArrowLeft className="icon-sm"/>
                            Back to Detective
                        </button>
                    </RouterLink>

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
                                    <img
                                        src={member.photo}
                                        alt={member.name}
                                        className="member-img"
                                    />
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
                        <div className="stats-grid">
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