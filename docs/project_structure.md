# DocuPlanAI Project Structure

## Directory Layout
```
/docuplanai/
├── frontend/
│   ├── src/
│   │   ├── api/              # API client configuration
│   │   │   ├── client.ts     # Axios client setup
│   │   │   └── endpoints.ts  # API endpoint definitions
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/          # Base UI components
│   │   │   ├── PDF/         # PDF handling components
│   │   │   ├── Task/        # Task management components
│   │   │   └── Project/     # Project management components
│   │   ├── contexts/        # React contexts
│   │   │   ├── AuthContext  # Authentication state
│   │   │   └── ThemeContext # Theme management
│   │   ├── layouts/         # Page layouts
│   │   │   └── MainLayout   # Main application layout
│   │   ├── pages/           # Page components
│   │   │   ├── Login       # Authentication pages
│   │   │   ├── Dashboard   # Main dashboard
│   │   │   └── Analysis    # PDF analysis pages
│   │   └── types/          # TypeScript definitions
│   └── public/             # Static assets
└── backend/
    └── app/
        ├── api/            # API endpoints
        │   └── v1/
        │       ├── auth    # Authentication endpoints
        │       ├── pdf     # PDF handling endpoints
        │       └── tasks   # Task management endpoints
        ├── core/           # Core functionality
        │   ├── auth.py     # Authentication logic
        │   ├── config.py   # Configuration management
        │   └── database.py # Database setup
        ├── models/         # Database models
        │   ├── user.py     # User model
        │   ├── project.py  # Project model
        │   └── task.py     # Task model
        ├── schemas/        # Pydantic schemas
        │   ├── user.py     # User schemas
        │   └── task.py     # Task schemas
        └── services/       # Business logic
            ├── pdf_analysis_service.py    # PDF processing
            └── openai_service.py          # OpenAI integration

## Key Files and Their Purposes

### Frontend
- `src/api/client.ts`: Axios client configuration with auth token management
- `src/contexts/AuthContext.tsx`: JWT token management and auth state
- `src/components/PDF/PDFUploader.tsx`: PDF file upload handling
- `src/components/Task/TaskList.tsx`: Task display and management
- `src/pages/Analysis/ProjectAnalysis.tsx`: PDF analysis workflow

### Backend
- `app/api/v1/endpoints/pdf.py`: PDF upload and analysis endpoints
- `app/api/v1/endpoints/auth.py`: Authentication endpoints
- `app/services/pdf_analysis_service.py`: PDF processing logic
- `app/services/openai_service.py`: OpenAI integration
- `app/core/auth.py`: JWT token handling and user authentication

## Configuration Files
- `backend/.env`: Environment variables
- `frontend/.env`: Frontend environment configuration
- `backend/alembic.ini`: Database migration configuration
- `frontend/tsconfig.json`: TypeScript configuration

## Test Files
- `frontend/src/components/**/__tests__/`: Component tests
- `backend/tests/`: Backend unit tests
```
