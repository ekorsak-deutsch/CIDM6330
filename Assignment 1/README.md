# Cloud-Based Account Detection and Response (ADR) Solution Requirements Specification

## Front Matter

### Front Page

**Project Name:** Cloud-Based ADR Solution  
**Version:** 1.0  
**Date:** 2/12/2024
**Status:** Draft  

---

## Introduction

### Scope and Constraints
The Cloud-Based ADR Solution is designed to provide cybersecurity monitoring capabilities for cloud-centric educational environments. Due to scope constraints, only the **Monitoring feature** will be implemented in this phase. This includes real-time tracking of logins, MFA modifications, and email rule changes via platform APIs. Advanced threat detection, file monitoring, response actions are **out of scope** for the current implementation.

### Table of Contents
1. [Requirements Statements](#requirements-statements)
2. [User Stories, Use Cases, Features, Gherkin Validation](#user-stories-use-cases-features-gherkin-validation)
3. [Specifications](#specifications)  
   - [Concept](#concept)  
   - [UX Notes](#ux-notes)  
   - [Interfaces (Controls)](#interfaces-controls)  
   - [Behaviors](#behaviors)  
4. [Feature/Package A (UML Diagrams)](#featurepackage-a-uml-diagrams)  
5. [Feature/Package N (UML Diagrams)](#featurepackage-n-uml-diagrams)  

---

## Requirements Statements

### Functional Requirements
- The system must track user logins.  
- The system must monitor MFA setting changes.  
- The system must detect email rule modifications.  
- The system must integrate with Google WorkspaceAPIs.  
- The system must generate alerts for any anomalous activities detected.  

### Non-Functional Requirements
- The system must provide data processing capabilities.  
- The system must offer an intuitive web-based interface.  
- The system must be capable of sending email alerts
- The system must encrypt stored and transmitted data.  

---

## User Stories, Use Cases, Features, Gherkin Validation

### User Stories
- **As a school IT administrator**, I want to monitor user logins so that I can detect unauthorized access.  
- **As a security analyst**, I want to track MFA setting changes to prevent account takeovers.  
- **As an auditor**, I want to review email rule modifications to identify potential security breaches.  

### Use Cases
- **UC01:** Monitoring Google Workspace logins.  
- **UC02:** Detecting changes in MFA settings.  
- **UC03:** Flagging suspicious email rule modifications.  

### Gherkin Validation
```gherkin
Scenario: Detecting an unauthorized login
  Given a user logs in from an unusual location
  When the system detects the anomaly
  Then an alert is generated for the administrator

Scenario: MFA modification detection
  Given a user changes their MFA settings
  When the system identifies the modification
  Then an alert is sent to the security team

Scenario: Email rule modification alert
  Given a user adds an external email forwarding rule
  When the system detects this change
  Then a security notification is triggered

Scenario: Administrator reviews security alerts  
  Given there are active security alerts in the system  
  When the administrator accesses the alert dashboard  
  Then they should see a list of recent alerts  
  And each alert should include details such as timestamp, user, and action taken  
```
## Specifications

### Concept
The system functions as a monitoring tool that integrates with cloud platforms, providing real-time security insights.

### UX Notes
- The dashboard must display login activities, MFA modifications, and email rule changes in an intuitive format.
- Administrators should be able to filter events based on time and severity.

### Interfaces (Controls)
- **Dashboard:** Displays real-time monitoring data.
- **Alert System:** Notifies administrators of detected anomalies.

### Behaviors
- **Login Monitoring:** Track user authentication events.
- **MFA Change Detection:** Log security setting changes.
- **Email Rule Monitoring:** Identify suspicious modifications.

---

### Feature/Package A: Monitoring System
**UML Diagram: Monitoring Use case**  

---

### Feature/Package N: Alert System
**UML Diagram: Alert Generation**  

---

> **Note:** This specification focuses solely on the monitoring functionality due to scope constraints, leaving advanced response actions for future phases.