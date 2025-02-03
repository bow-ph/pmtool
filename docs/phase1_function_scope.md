# DocuPlanAI Function Scope

## Phase 1 (MVP)
### 1. Authentication System
#### Login
- Basic JWT token-based authentication
- Support for both form and JSON request formats
- Token storage in localStorage with automatic header management
- Protected routes using AuthContext

#### Registration
- Basic email/password registration
- Form validation with error handling
- Package selection during registration
- Automatic login after successful registration

Note: Advanced authentication features (password reset, 2FA) are planned for Phase 3

## 2. PDF Analysis
### Upload
- PDF file validation and storage
- User-specific storage directories
- Secure file access control
- Support for large files with chunk processing

### Analysis
- Text extraction using pdfplumber
- OpenAI GPT-4 integration for task extraction
- Rate limit handling with exponential backoff
- Confidence scoring for extracted tasks

### Task Generation
- Automatic task creation from PDF analysis
- Time estimation with confidence scores
- Task prioritization
- Project context analysis

## 3. Task Management
### Task Properties
- Title and description
- Duration and hourly rate estimates
- Confidence scores with rationale
- Status tracking (pending/in-progress/completed)
- Priority levels (low/medium/high)

### Task Operations
- Create tasks from PDF analysis
- Update task status
- Track estimated vs actual hours
- View task details and confidence metrics

## 4. Project Analysis
### Document Analysis
- Document type detection
- Context extraction
- Client type identification
- Complexity assessment
- Clarity scoring

### Risk Assessment
- Task confidence scoring
- Project complexity analysis
- Time estimation validation
- Dependency risk evaluation

## 5. Core Infrastructure
### Database
- PostgreSQL with separate test tables
- User and project management tables
- Task and analysis storage
- Subscription tracking

### API Structure
- RESTful endpoints with /api/v1/ prefix
- Protected routes with JWT validation
- Error handling with detailed messages
- Rate limiting for OpenAI requests

### Frontend Architecture
- React with TypeScript
- Protected route management
- Component-based UI
- Real-time form validation

## Future Phases

### Phase 2
- Task planning workflow ("Planung" button)
- Task editing (title, description, time)
- Calendar integration
- Task scheduling via "Einplanen" button
- Outlook calendar integration
- Complete planning export to Outlook

### Phase 3
- Enhanced authentication (login, registration, password reset)
- Subscription package management
- Admin interface for customer and subscription management
- Customer account management

### Not Included in Phase 1
- Calendar integration (moved to Phase 2)
- Subscription management (moved to Phase 3)
- Admin interface (moved to Phase 3)
- Email notifications
- Multi-factor authentication (moved to Phase 3)
