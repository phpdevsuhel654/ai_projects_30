Act as a Senior Python Software Architect, Flask Expert, DevOps Engineer, and Database Designer.

I want to build a production-ready Python application step-by-step for learning purposes. Follow a professional software engineering approach and generate the project incrementally. Do not skip any steps. Before writing code for a step, explain the purpose, architecture decisions, folder structure, and implementation approach.

## Technology Stack

* Language: Python 3.x
* Framework: Flask
* Database: SQLite
* ORM: SQLAlchemy
* API Communication: Requests
* Background Jobs: APScheduler (if required)
* Frontend: Jinja2 + Bootstrap 5
* Configuration: Environment Variables
* Logging: Python Logging Module
* Architecture: Modular, Scalable, Production-Ready

---

# Application Name

Infrastructure Utility Portal

---

# Feature 1: Address Validation & Correction Module

## Business Requirement

Every day I manually verify customer addresses before label creation.

Users will provide an address in JSON format:

```json
{
  "BuildingName": "Green Side 5",
  "StreetAddress": "400 Avenue Roumanille",
  "Suburb": "Biot",
  "City": "Biot",
  "PostCode": "06410",
  "CountryCode": "FR"
}
```

The system must:

1. Accept address JSON input.
2. Validate the address.
3. Search and verify address details using a free address validation/geocoding API whenever possible.
4. Return:

   * Original Address
   * Corrected Address
   * Validation Status
   * Confidence Score
   * Validation Timestamp
5. Save validation history in SQLite.
6. Allow viewing previous validations.
7. Expose REST APIs for validation.
8. Provide a simple web UI.
9. Use python\monitor-system folder as root folder

## Preferred Free APIs

Evaluate and implement the best available free option:

* Nominatim (OpenStreetMap)
* Photon API
* Geoapify Free Tier
* OpenCage Free Tier

Use the most suitable free service.

## Sample Output Format

```json
{
  "BuildingName": "Green Side 5",
  "StreetAddress": "400 Avenue Roumanille",
  "Suburb": "Biot",
  "City": "Biot",
  "PostCode": "06410",
  "CountryCode": "FR"
}
```

---

# Feature 2: Server URL Health Check Module

## Business Requirement

Every month during the 4th Sunday patching activity, I manually verify multiple server URLs.

Example URLs:

```text
https://web4.omniparcelreturns.com
https://web4.omnirps.com
```

I want a module where:

1. URLs can be added, edited, deleted.
2. URLs are stored in SQLite.
3. One-click execution checks all URLs.
4. The system performs:

   * DNS Resolution Check
   * HTTP Status Check
   * HTTPS Validation
   * Response Time Check
   * Availability Check
5. Generate a detailed execution report.

## Report Should Include

* URL
* Status (UP/DOWN)
* HTTP Status Code
* Response Time
* Error Message
* Execution Start Time
* Execution End Time
* Total Duration

## Dashboard Requirements

Display:

* Total URLs
* Active URLs
* Failed URLs
* Last Execution Time
* Execution History

## APIs

Create REST APIs for:

* Add URL
* Update URL
* Delete URL
* Execute Checks
* View Reports
* View History

---

# Database Design

Create normalized SQLite tables for:

## Address Module

* address_validations

## URL Monitoring Module

* monitored_urls
* execution_history
* execution_details

Provide complete ERD and relationships.

---

# Architecture Requirements

Use the following structure:

```text
monitor-system/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── repositories/
│   ├── utils/
│   ├── templates/
│   ├── static/
│   └── config/
│
├── migrations/
├── tests/
├── logs/
├── database/
│
├── app.py
├── requirements.txt
├── .env
└── README.md
```

Follow:

* Service Layer Pattern
* Repository Pattern
* Dependency Separation
* SOLID Principles
* Clean Code Practices

---

# Development Process

Build the application step-by-step.

For each step provide:

1. Objective
2. Folder/File Creation
3. Code
4. Explanation
5. Testing Procedure

Start with:

Step 1:

* System Architecture
* Database Design
* Folder Structure
* Required Packages

Wait for my approval before moving to the next step.

Keep responses concise and minimize unnecessary tokens while maintaining production-quality implementation.
