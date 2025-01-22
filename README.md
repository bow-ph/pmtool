# Project Management Tool

Ein effizientes Projektplanungstool für die bow-agentur.

## Features

### Projektplanung
- PDF-Analyse für Aufgaben und Zeitschätzungen
- Projektplanung zwischen Start- und Enddatum
- Dynamische To-Do-Listen-Generierung
- Erkennung fehlerhafter Schätzungen
- CalDAV-Export für Outlook und andere Kalenderdienste

### Preismodelle
- **Trial:** Kostenfrei, limitiert auf ein Projekt in drei Monaten
- **Team:** 10 Projekte alle drei Monate
- **Enterprise:** Auf Anfrage

## Technischer Stack

### Frontend
- React mit TypeScript
- Tailwind CSS (inkl. Dark Mode)
- Domain: pm.bow-agentur.de

### Backend
- Python mit PostgreSQL
- PDF-Analyse: PyPDF2, pdfplumber
- CalDAV-Integration mit Radicale
- Domain: pmadmin.bow-agentur.de
- CalDAV-Server: pm.bow-agentur.de/caldav

### Integrationen
- Mollie für Zahlungsabwicklung
- SendGrid für System-E-Mails

## Entwicklung

### Frontend-Features
- Registrierung und Login mit 2FA
- Abonnement-Verwaltung über Mollie
- Automatische System-E-Mails
- Dashboard mit Menünavigation
- Projektübersicht und KI-Planung
- Light/Dark Mode

### Backend-Features
- Benutzerverwaltung und Rechtesystem
- Preispaket-Verwaltung
- Zahlungsüberwachung
- Mollie Webhook Integration
- CalDAV-Endpunkt für Kalendersynchronisation
