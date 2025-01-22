# Technische Analyse

## Projektplanungs-Features

### 1. PDF-Analyse
- **Anforderung:** Extraktion von Aufgaben und Zeitschätzungen aus PDFs
- **Technologie:** PyPDF2 und pdfplumber für Python
- **Komponenten:**
  - PDF-Parser für Textextraktion
  - NLP für Aufgabenerkennung
  - Zeitschätzungs-Extraktor
  - Strukturierte Ausgabe für Weiterverarbeitung

### 2. Projektplanung
- **Anforderung:** Scheduling zwischen Start/End mit Berücksichtigung anderer Termine
- **Komponenten:**
  - Terminkalender-Integration
  - Konflikterkennungs-Algorithmus
  - Lastverteilungs-Optimierung
  - Überlastungsvermeidung-Logik

### 3. To-Do-Listen
- **Anforderung:** Dynamische Generierung, manuelle Anpassung, automatische Synchronisation
- **Komponenten:**
  - CRUD-Operationen für Tasks
  - Echtzeit-Synchronisation
  - Versionierung für Änderungsverfolgung
  - Kalendersynchronisation via CalDAV

### 4. Schätzungsfehler-Erkennung
- **Anforderung:** Erkennung und Meldung fehlerhafter Schätzungen
- **Komponenten:**
  - Zeiterfassungs-System
  - Abweichungsanalyse
  - Benachrichtigungssystem
  - Reporting-Funktionen

### 5. CalDAV-Export
- **Anforderung:** Export in Outlook/andere Kalenderdienste
- **Technologie:** Radicale CalDAV-Server
- **Komponenten:**
  - CalDAV-Endpunkt (pm.bow-agentur.de/caldav)
  - iCal-Formatierung
  - Synchronisations-Handler
  - Authentifizierung

## Preismodell-Implementation

### Pakete
1. **Trial**
   - 1 Projekt
   - 3 Monate Laufzeit
   - Kostenfrei
   
2. **Team**
   - 10 Projekte
   - 3 Monate Laufzeit
   - Kostenpflichtig
   
3. **Enterprise**
   - Individuelle Konditionen
   - Auf Anfrage
   - Custom Pricing

### Admin-Backend Features
- Paket-Verwaltung (CRUD)
  - Name
  - Preis
  - Beschreibung
  - Button-Text
  - Sichtbarkeits-Toggle
- Mollie-Integration
  - Webhook-Handler
  - Zahlungsverifikation
  - Automatische Aktivierung

## Frontend-Architektur

### Authentifizierung
- Registrierung
- Login
- Passwort-Reset
- 2FA-Integration

### Abonnement-Management
- Paketauswahl
- Mollie-Checkout
- Abo-Verwaltung
- Rechnungs-PDF

### Dashboard
- Navigation
  - Einstellungen
  - Projektübersicht
  - KI-Planung
- Kalendervorschau
- Light/Dark Mode

## Backend-Architektur

### Technologie-Stack
- Python
- PostgreSQL
- PyPDF2/pdfplumber
- Radicale (CalDAV)
- SendGrid (E-Mail)

### Datenbank-Schema (Vorläufig)
```sql
-- Benutzer
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    two_factor_enabled BOOLEAN,
    subscription_type VARCHAR(50),
    subscription_end_date TIMESTAMP
);

-- Projekte
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(50)
);

-- Aufgaben
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    description TEXT,
    estimated_hours FLOAT,
    actual_hours FLOAT,
    status VARCHAR(50),
    calendar_sync_id VARCHAR(255)
);

-- Preispakete
CREATE TABLE pricing_packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10,2),
    button_text VARCHAR(255),
    visible BOOLEAN,
    max_projects INTEGER
);

-- Zahlungen
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    package_id INTEGER REFERENCES pricing_packages(id),
    mollie_payment_id VARCHAR(255),
    amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP
);
```

### API-Endpunkte (Vorläufig)

#### Authentifizierung
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/reset-password
- POST /api/auth/2fa/enable
- POST /api/auth/2fa/verify

#### Projekte
- GET /api/projects
- POST /api/projects
- GET /api/projects/{id}
- PUT /api/projects/{id}
- DELETE /api/projects/{id}
- POST /api/projects/{id}/analyze-pdf
- GET /api/projects/{id}/tasks

#### Aufgaben
- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/{id}
- DELETE /api/tasks/{id}
- POST /api/tasks/{id}/sync-calendar

#### Abonnements
- GET /api/subscriptions/packages
- POST /api/subscriptions/checkout
- GET /api/subscriptions/current
- POST /api/subscriptions/cancel

#### Admin
- GET /api/admin/users
- GET /api/admin/packages
- PUT /api/admin/packages/{id}
- GET /api/admin/payments
- POST /api/admin/webhooks/mollie

#### CalDAV
- Endpunkt: pm.bow-agentur.de/caldav
- Authentifizierung via Basic Auth
- Unterstützung für PROPFIND, REPORT, etc.

## Integrationen

### Mollie
- Test-API-Key: test_ENdGpCBJjm67KQCPfPWPqRjd6nBafw
- Live-API-Key: live_q3v2sAKHnAAd6BeSR4uahJ3QcKWGND
- Webhook-URL: https://pmadmin.bow-agentur.de/api/admin/webhooks/mollie

### SendGrid
- System-E-Mails für:
  - Registrierung
  - Passwort-Reset
  - Zahlungsbestätigung
  - Rechnungs-PDF

### Domains
- Frontend: pm.bow-agentur.de
- Backend: pmadmin.bow-agentur.de
- CalDAV: pm.bow-agentur.de/caldav
