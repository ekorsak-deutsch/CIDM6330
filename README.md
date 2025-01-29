# Software System: Cloud-Based Account Detection and Response (ADR) Solution

## What is EDR?  
Most organizations today use cybersecurity software to monitor user activity on devices, block malware threats, and enable IT teams to respond to incidents via a centralized dashboard. These solutions are known as **Endpoint Detection and Response (EDR)** tools.

## Why EDR Falls Short in Cloud-Only Educational Environments  
As a cybersecurity consultant for a public school district, I’ve observed that traditional EDR solutions are ill-suited for modern educational settings, particularly those relying on **Chromebooks**. In such environments, workflows differ significantly from the scenarios EDRs are designed to address.  

In a typical office setup, users work on locally stored files (e.g., drafting a document in MS Word, like I did for this essay). However, Chromebook-centric schools operate almost exclusively in the cloud: files are stored in **Google Drive** or **Microsoft OneDrive**, and collaboration occurs via **browser-based apps** or **shared links**. Crucially, cybersecurity threats in these environments often bypass local devices entirely. For example:  

- A user might receive a **malicious link** to a Google Drive document designed to steal credentials. Since the file isn’t downloaded locally or sent via email, traditional spam filters and EDR tools fail to detect it.  
- Once an **account is compromised**, attackers can alter **multi-factor authentication (MFA) settings** or **email forwarding and filters** directly in the cloud to maintain access and conceal their activity.  

## The Need for a Cloud Account-Centric EDR  
Traditional EDR consoles focus on **devices**, displaying alerts, activity logs, and options to isolate compromised machines. In **cloud environments** like **Google Workspace** and **Microsoft 365**, the fundamental unit is the **user account**. A solution should instead provide:  

- An admin **dashboard** listing user accounts with associated risk indicators (e.g., suspicious logins, MFA changes, or unusual email rules).  
- **Visibility into cloud storage activity** (e.g., files in Google Drive/OneDrive, especially externally shared ones).  
- **Direct response actions**, such as disabling compromised accounts or triggering malware scans, within the same interface.  

## Limitations of Existing Solutions  
Current tools like **Microsoft Defender for Office 365** or **SIEM platforms** are either:  

- **Platform-specific** (e.g., incompatible with Google Workspace).  
- **Lack real-time response** capabilities.  
- **Generate insufficiently detailed alerts**.  

To address these gaps, I developed **Python scripts** that use **Google Workspace APIs** to monitor email rules, MFA settings, and file activity. While functional, this approach has drawbacks:  

- Requires **advanced programming skills** and ongoing maintenance.  
- Lacks **real-time alerts** and integrated response actions.  
- Relies on **manual investigation** via SIEM or admin consoles.  

## Proposed Cloud ADR Workflow  
An ideal **Cloud ADR solution** would integrate the following:  

### API-Driven Data Collection  
Leverage **Google Workspace** and **Microsoft 365 APIs** to pull real-time data on user activity, MFA settings, email rules, and cloud storage.  

### Automated Threat Detection  
- **Scan cloud-stored files** for malicious links using services like **VirusTotal**.  
- **Flag suspicious account changes** (e.g., MFA resets, email forwarding rules).  

### Unified Admin Console  
A **SaaS-based interface** enabling:  
- **Real-time alerts** with contextual data (e.g., "_User X added an external email forwarding rule after an anomalous login_").  
- **Immediate response actions** (e.g., disable accounts, revoke file access, or force password resets).  

## Implementation Example  
- **File Protection**: Use APIs to retrieve files from **Google Drive/OneDrive**, scan them for threats, and discard non-malicious files after analysis.  
- **Real-Time Monitoring**: Continuously track **logins, MFA modifications, and email rule changes** via platform APIs.  
- **Automated Response**: Enable **one-click actions** (e.g., isolating accounts, reverting suspicious settings) directly from the ADR dashboard.  

## Conclusion  
A **Cloud ADR solution** would bridge critical gaps in securing **cloud-only educational environments**. By shifting focus from **endpoints to user accounts** and integrating **monitoring, scanning, and response capabilities** into a single platform, organizations could **mitigate risks** unique to cloud workflows while reducing reliance on **complex, fragmented tools**.  
