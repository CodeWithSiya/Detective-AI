# Detective AI

A web-based application designed to detect AI-generated content in both text and images using advanced machine learning models. Detective AI provides confidence scores and detailed explanations to help users distinguish between human-created and artificially generated content.

## Features

- **Text Analysis**: Detect AI-generated written content (up to 5,000 characters)
  - Supports direct text input, PDF files, and DOCX files
- **Image Analysis**: Identify AI-generated images (JPG, JPEG, PNG formats)
- **Confidence Scoring**: Percentage-based reliability scores for all analyses
- **Guest & Registered Access**: Basic features for guests, full functionality for registered users
- **Submission History**: Track and review past analyses (registered users)
- **Export Functionality**: Download PDF reports or receive via email
- **Feedback System**: User feedback to improve detection accuracy

## Live Demo

**Web Application**: https://detective-ai-virid.vercel.app

## Tech Stack

**Frontend:**
- React 19.1.1
- Vite 7.1.2
- Chakra UI 3.24.2
- Framer Motion 12.23.12
- Tailwind CSS 4.1.12

**Backend:**
- Django 4.2.24
- Django REST Framework 3.16.1
- PostgreSQL
- Supabase (database hosting)
- PyTorch 2.8.0
- Transformers 4.55.4
- Anthropic 0.64.0
- Gunicorn 23.0.0

**AI Models:**
- Transformer-based text detection models
- Hugging Face image detection models
- Claude AI for analysis explanations

## Quick Start

### Option 1: Use the Web Application
Simply visit https://detective-ai-virid.vercel.app and start analyzing content immediately.

### Option 2: Local Development Setup

#### Prerequisites
- Python 3.8+
- Node.js 18.0+
- PostgreSQL 12+

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CodeWithSiya/Detective-AI
   cd Detective-AI
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment configuration**
   Create `.env` file in backend directory:
   ```bash
   SECRET_KEY=your_django_secret_key
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=localhost
   DB_PORT=5432
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   FRONTEND_URL=http://localhost:5173
   ```

4. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional
   ```

5. **Frontend setup**
   ```bash
   cd ../frontend
   npm install
   ```

6. **Start the application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python manage.py runserver
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

   Access the application at http://localhost:5173

## Usage

### For Guest Users
- Visit the landing page
- Click "Enter Detective Mode" for basic analysis
- Analyze text content with limited features

### For Registered Users
- Create an account and verify your email
- Access full analysis features including:
  - Text and image analysis
  - Submission history
  - PDF/email exports
  - Feedback system

### Analysis Process
1. Choose content type (text or image)
2. Input content (type, paste, or upload file)
3. Submit for analysis
4. Review confidence scores and detailed explanations
5. Export results (registered users)

## API Endpoints

The Django backend provides RESTful API endpoints:

- `POST /api/analysis/text/` - Analyze text content
- `POST /api/analysis/image/` - Analyze image content
- `GET /api/submissions/` - Get user submission history
- `POST /api/feedback/` - Submit analysis feedback

## System Requirements

**For Users:**
- Modern web browser (Chrome 100+, Firefox 100+, Safari 15+, Edge 100+)
- Stable internet connection
- JavaScript enabled

**For Development:**
- Python 3.9+
- Node.js 16.0+
- PostgreSQL 12+
- 4GB+ RAM recommended
- 4GB+ free storage space

## Contributing

1. Fork the repository
2. Create a branch (`git checkout -b new-branch`)
3. Make your changes
4. Run tests and ensure code quality
5. Commit your changes (`git commit -m 'Add new feature'`)
6. Push to the branch (`git push origin new-branch`)
7. Open a Pull Request

## Project Structure

```
Detective-AI/
├── backend/                    # Django backend
│   ├── config/                # Django project configuration
│   │   ├── __init__.py
│   │   ├── settings.py        # Django settings & environment variables
│   │   ├── urls.py           # Main URL configuration
│   │   ├── wsgi.py           # WSGI configuration
│   │   └── asgi.py           # ASGI configuration
│   ├── app/                   # Main Django application
│   │   ├── models/           # Database models
│   │   │   ├── user.py
│   │   │   ├── text_submission.py
│   │   │   ├── image_submission.py
│   │   │   ├── text_analysis_result.py
│   │   │   ├── image_analysis_result.py
│   │   │   └── feedback.py
│   │   ├── views/            # API endpoints & views
│   │   │   ├── analysis_views.py
│   │   │   ├── user_views.py
│   │   │   ├── admin_views.py
│   │   │   ├── feedback_views.py
│   │   │   ├── report_views.py
│   │   │   └── submission_history_views.py
│   │   ├── services/         # Business logic services
│   │   ├── serializers/      # DRF serializers
│   │   ├── ai/              # AI models & detection logic
│   │   │   ├── ai_text_model.py
│   │   │   ├── ai_image_model.py
│   │   │   └── ai_model.py
│   │   ├── migrations/       # Database migrations
│   │   ├── management/       # Django management commands
│   │   ├── templates/        # Email templates
│   │   └── urls.py          # App URL configuration
│   ├── tests/               # Backend tests
│   │   ├── models/
│   │   ├── views/
│   │   └── conftest.py
│   ├── wheels/              # Python wheel files for dependencies
│   ├── manage.py            # Django management script
│   ├── requirements.txt     # Python dependencies
│   └── pytest.ini         # Pytest configuration
├── frontend/               # React frontend
│   ├── src/               # React source files
│   │   ├── components/    # React components
│   │   │   ├── UserAuthentication/  # Auth components
│   │   │   │   ├── Login/
│   │   │   │   ├── Signup/
│   │   │   │   ├── ForgotPassword/
│   │   │   │   └── ChangePassword/
│   │   │   ├── DetectivePage/      # Main analysis interface
│   │   │   ├── Basic-DetectivePage/ # Guest analysis interface
│   │   │   ├── Admin/              # Admin dashboard
│   │   │   ├── UserManagement/     # User management
│   │   │   ├── DemoLandingPage/    # Landing page
│   │   │   ├── Team/               # Team page
│   │   │   ├── Assets/             # Image assets
│   │   │   ├── ui/                 # UI components
│   │   │   └── ScrollToTop/        # Utility components
│   │   ├── assets/        # Static assets
│   │   ├── App.jsx        # Main App component
│   │   ├── App.css        # Global styles
│   │   ├── main.jsx       # React entry point
│   │   └── index.css      # Global CSS
│   ├── public/            # Static assets
│   │   ├── Logo.png
│   │   ├── confidence-analysis.png
│   │   ├── detection-factors.png
│   │   └── *.mp4         # Demo videos
│   ├── test/              # Frontend tests
│   │   ├── __mocks__/
│   │   └── msw/
│   ├── .notebook/         # Development notebooks
│   ├── package.json       # Node.js dependencies
│   ├── requirements.txt   # Frontend requirements (custom)
│   ├── vite.config.js     # Vite configuration
│   ├── babel.config.cjs   # Babel configuration
│   ├── eslint.config.js   # ESLint configuration
│   ├── jsconfig.json      # JavaScript configuration
│   └── index.html         # HTML entry point
└── README.md              # Project documentation
```

## Documentation

- **User Manual**: Available in `/frontend/public/DetectiveAI_User_Manual.pdf`
- **API Endpoints**: Django REST API available at `https://detective-ai.up.railway.app/api/`
- **Demo Videos**: Interactive guides available in `/frontend/public/` (*.mp4 files)
- **Frontend Documentation**: Component documentation in `/frontend/src/components/`
- **Backend API**: RESTful endpoints documented in `/backend/app/views/`

## Testing

```bash
# Backend tests (unit and integration)
cd backend
pip install pytest
pytest
```

## Deployment

The application is deployed on:
- **Frontend**: Vercel (https://detective-ai-virid.vercel.app)
- **Backend**: Railway (https://detective-ai.up.railway.app)
- **Database**: Supabase (PostgreSQL)

## License

This project was developed as a capstone project for academic purposes.

## Team

Detective AI was developed by Computer Science students as part of their capstone project:
- Siyabonga Madondo
- Lindokuhle Mdlalose  
- Ethan Ngwetjana

## Acknowledgments

- University of Cape Town Computer Science Department
- Prof. Geoff Nitschke (Project Supervisor)
- Hugging Face for AI models
- Anthropic Claude for analysis explanations

## Support

For technical issues or questions:
1. Check the [User Manual](frontend/public/DetectiveAI_User_Manual.pdf) for troubleshooting
2. Open an issue in this repository
3. Visit the [Team page](https://detective-ai-virid.vercel.app/team) to contact the development team
---

**Note**: This is an academic project focused on AI content detection research and education.
