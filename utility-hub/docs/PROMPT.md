# Utility Hub Enhancement and Module Integration

## Objective

Enhance the existing **Utility Hub** application by integrating selected features from another Python project while preserving all existing functionality.

---

# Project Information

## Current Project

```
python/utility-hub
```

## Source Project (Features to Merge)

```
python/monitor-system
```

---

# General Requirements

1. The application title must be changed (or verified) as:

```
Utility Hub
```

2. Review the complete functionality of the existing project located at:

```
python/utility-hub
```

Understand its:

* Architecture
* Folder structure
* Database design
* UI
* Navigation
* APIs
* Existing features

Do **not** modify or break any existing functionality.

3. Review the project located at:

```
python/monitor-system
```

Analyze:

* Folder structure
* Database
* Business logic
* APIs
* Services
* Dependencies
* UI implementation

Identify everything required to merge its features into **Utility Hub**.

---

# Features to Integrate

Merge the following modules from **monitor-system** into **Utility Hub** as independent modules.

## 1. Address Validation

## 2. URL Monitoring

## 3. Health

# Navigation

Add the above modules to the main navigation menu.

Example:

* Dashboard
* Existing menus...
* Address Validation
* URL Monitoring
* Health

Ensure the new modules follow the same UI design, layout, styling, and navigation patterns as the current Utility Hub application.

---

# Existing Features

Do **not** modify, remove, or refactor any existing functionality unless it is strictly required for integration.

The following existing features must continue working exactly as they do now:

* Dashboard
* Full Database Backup
* History Cleanup
* All other existing modules

Maintain backward compatibility.

---

# Dashboard Review

Review the existing Dashboard implementation.

Determine whether the newly integrated modules should contribute additional dashboard metrics or widgets.

If appropriate:

* Add new dashboard cards
* Add summary statistics
* Add monitoring charts
* Add recent activity
* Preserve the current dashboard layout and functionality

---

# Database Review

Review the existing database schema.

Merge any required tables from the monitor-system project.

Requirements:

* Avoid duplicate tables
* Maintain referential integrity
* Preserve existing data
* Use migrations where appropriate
* Follow existing naming conventions

---

# Documentation

Update all project documentation to reflect the new architecture in docs folder.


---

# Port Configuration

Configure the application to run on:

```
5000
```

Ensure:

* Flask configuration is updated
* Launch scripts are updated
* Environment variables are updated (if used)
* Documentation reflects the new port

---

# Code Quality Requirements

* Preserve existing code style.
* Follow modular architecture.
* Avoid duplicate code.
* Reuse existing utilities wherever possible.
* Maintain clean separation of concerns.
* Ensure proper error handling and logging.
* Maintain consistent naming conventions.
* Keep the project scalable and maintainable.
* Both system database records should be merged, so I don't need to configuration and other data engry again.
* Do the changes in current system, if mandatory.

---

# Deliverables

The final solution should include:

* Fully integrated Utility Hub application
* Existing functionality preserved
* Address Validation module integrated
* URL Monitoring module integrated
* Health module integrated
* Updated navigation
* Updated dashboard (if required)
* Updated database schema
* Updated documentation
* Application configured to run on port 5000
* Clean, production-ready code with no broken functionality
