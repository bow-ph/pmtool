# Backend Files to Remove

## Duplicate API Files
- [ ] /backend/app/api/projects.py
  - Duplicate of /api/v1/endpoints/projects.py
  - All functionality exists in v1 endpoint
  - No unique implementations

## Moved Dependencies
- [ ] /backend/app/api/deps.py
  - Functionality moved to /core/dependencies.py
  - Authentication dependencies consolidated
  - Database session handling moved

## Consolidated Services
- [ ] /backend/app/services/pdf_service.py
  - Merged into pdf_analysis_service.py
  - Text extraction methods consolidated
  - OpenAI integration streamlined

## Deprecated Database Files
- [ ] /backend/app/db/*
  - All functionality moved to /core/database.py
  - Session management consolidated
  - Model imports centralized

## Legacy API Files
- [ ] /backend/app/api/api_v1/*
  - Duplicate of current /api/v1/*
  - All endpoints migrated
  - No unique implementations

Note: These files have been identified as safe to remove because:
1. Their functionality exists in other maintained files
2. They are not referenced by active code
3. They are not required for MVP features
4. Test coverage exists for their replacements
