# DocuPlanAI Project Structure

## Directory Layout by Phase

### Phase 1 (MVP)
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
│   │   │   ├── Task/        # Task list components
│   │   │   └── Analysis/    # PDF analysis components
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

### Phase 2 (Task Planning & Calendar)
```
/docuplanai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Calendar/    # Calendar integration components
│   │   │   │   ├── CalendarView.tsx
│   │   │   │   └── OutlookSync.tsx
│   │   │   └── Task/       # Enhanced task components
│   │   │       ├── TaskEditor.tsx
│   │   │       └── TaskPlanner.tsx
│   │   └── services/
│   │       └── outlook.ts   # Outlook calendar integration
└── backend/
    └── app/
        ├── api/v1/
        │   └── calendar/    # Calendar sync endpoints
        └── services/
            └── calendar/    # Calendar integration services
```

### Phase 3 (Admin & Subscription)
```
/docuplanai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Admin/      # Admin interface components
│   │   │   │   ├── CustomerManagement.tsx
│   │   │   │   └── SubscriptionManagement.tsx
│   │   │   └── Account/    # Enhanced account components
│   │   │       ├── Profile.tsx
│   │   │       └── Subscription.tsx
│   │   └── pages/
│   │       └── admin/      # Admin pages
│   │           ├── Customers.tsx
│   │           └── Subscriptions.tsx
└── backend/
    └── app/
        ├── api/v1/
        │   ├── admin/      # Admin endpoints
        │   └── account/    # Account management
        └── services/
            └── billing/    # Subscription services
```

## Key Files and Their Purposes

### Phase 1 (MVP)
#### Frontend
- `src/api/client.ts`: Axios client configuration with auth token management
- `src/contexts/AuthContext.tsx`: JWT token management and auth state
- `src/components/PDF/PDFUploader.tsx`: PDF file upload handling
- `src/components/Task/TaskList.tsx`: Task display and management
- `src/pages/Analysis/ProjectAnalysis.tsx`: PDF analysis workflow

### Phase 2 (Task Planning & Calendar)
#### Frontend
- `src/components/Calendar/CalendarView.tsx`: Calendar integration UI
- `src/components/Task/TaskPlanner.tsx`: Task planning interface
- `src/services/outlook.ts`: Outlook calendar sync service

### Phase 3 (Admin & Subscription)
#### Frontend
- `src/pages/admin/Customers.tsx`: Customer management interface
- `src/components/Account/Subscription.tsx`: Subscription management
- `src/components/Admin/SubscriptionManagement.tsx`: Admin subscription tools

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
