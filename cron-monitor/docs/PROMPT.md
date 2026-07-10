Act as a Senior Python Software Architect and Senior Flask Developer.

I want to build a production-ready **Cron Job URL Automation & Monitoring System** step by step.

### Objective

Currently, I manually execute multiple cron job URLs every day. Some URLs must be executed multiple times. I need a web-based system that automatically manages cron execution, stores execution history, and generates detailed reports.

### Technology Stack

* Backend: Python 3.x
* Framework: Flask
* Database: SQLite
* ORM: SQLAlchemy
* Scheduler: APScheduler
* HTTP Client: Requests
* Frontend: HTML, Bootstrap 5, Jinja2
* API Style: RESTful APIs
* Configuration: Environment Variables (.env)
* Logging: Python Logging Module

### Project Structure

Use clean architecture and enterprise-grade folder structure:

```text
cron-monitor/
│
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── scheduler/
│   │   ├── reports/
│   │   ├── utils/
│   │   ├── templates/
│   │   ├── static/
│   │   └── config/
│   │
│   ├── database/
│   ├── logs/
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
│
├── docs/
└── README.md
```

### Functional Requirements

#### 1. Cron URL Management

* Add Cron URL
* Edit Cron URL
* Delete Cron URL
* Enable/Disable Cron URL
* Store description
* Store execution frequency
* Store number of executions required

Example:

```text
URL:
https://web7.omnirps.com/cron/cron_delete_and_archive_log_table_data/return_order

Execution Count:
5
```

#### 2. Cron Execution Engine

* Execute URLs automatically
* Execute URLs manually
* Support running same URL multiple times
* Configurable timeout
* Retry failed requests
* Capture:

  * HTTP Status Code
  * Response Time
  * Response Body
  * Error Message
  * Execution Timestamp

#### 3. Scheduler

* Daily execution
* Hourly execution
* Custom schedule
* APScheduler integration
* Prevent duplicate execution

#### 4. Execution History

Store:

* URL
* Execution Number
* Status
* Start Time
* End Time
* Duration
* Response
* Error

#### 5. Reporting Dashboard

Show:

* Total URLs
* Total Executions
* Success Count
* Failure Count
* Success Percentage
* Average Response Time
* Last Execution Time

#### 6. Detailed Reports

Generate:

* Daily Report
* Weekly Report
* Monthly Report

Include:

* URL
* Run Count
* Success Count
* Failure Count
* Response Time
* Error Summary

#### 7. Notifications

Provide:

* Execution Summary
* Failed Cron URLs
* Success/Failure Statistics

#### 8. REST APIs

Create APIs for:

```text
POST   /api/cron
GET    /api/cron
GET    /api/cron/<id>
PUT    /api/cron/<id>
DELETE /api/cron/<id>

POST   /api/run/<id>
POST   /api/run-all

GET    /api/history
GET    /api/report
GET    /api/dashboard
```

### Database Design

#### cron_jobs

```text
id
name
url
execution_count
schedule_type
is_active
description
created_at
updated_at
```

#### execution_logs

```text
id
cron_job_id
execution_no
status
status_code
response_time
response_body
error_message
executed_at
```

### Non-Functional Requirements

* SOLID Principles
* Clean Architecture
* Repository Pattern
* Service Layer Pattern
* Modular Code
* Scalable Design
* Proper Exception Handling
* Logging
* Unit Testing
* API Validation
* Security Best Practices
* Environment-Based Configuration

### Development Rules

* Build the application step by step.
* Explain each step before generating code.
* Generate complete code for every file.
* Mention file path before code.
* Do not skip any implementation.
* Follow production-grade standards.
* Generate SQLite migrations.
* Create sample seed data.
* Create API testing examples.
* Create README.md.
* Keep responses concise and token-efficient.
* Use python\cron-monitor folder for current application

Start with:

1. High-Level Architecture
2. Database Design
3. Folder Structure
4. Development Roadmap
5. Phase-1 Project Setup
