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
}