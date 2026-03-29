# Ethical Use Policy

## Purpose

This document defines the conditions under which BackDoors_1.1 may be used legally and ethically. Read this document in full before using this software.

---

## When This Tool Should Be Used

BackDoors_1.1 is appropriate for the following activities, **provided written authorization has been obtained from the relevant system owner**:

- **Authorized penetration testing**: Testing the security of systems, networks, or endpoints you have contracted permission to test.
- **Red team operations**: Simulating real adversaries for an organization that has commissioned the engagement.
- **Security research**: Studying malware behavior, C2 communication patterns, or persistence mechanisms in an isolated lab environment.
- **Defensive tool development**: Building detection rules, SIEM signatures, or endpoint detection logic by replicating attack behaviors in a controlled environment.
- **Education and training**: Teaching penetration testing, incident response, or malware analysis in a classroom or lab context where all systems are owned or controlled by the instructor or institution.

---

## When This Tool Must NOT Be Used

This tool must never be used for:

- Accessing any computer system, network, or device without explicit written permission from its owner.
- Harvesting credentials, data, or information from systems you do not own or are not authorized to test.
- Deploying persistence mechanisms on systems without written authorization.
- Surveillance, stalking, or monitoring any individual without their knowledge and legal consent.
- Any activity that violates applicable local, national, or international law.
- Commercial purposes that involve unauthorized access to third-party systems.

---

## Legal Requirements

### Written Authorization

Before using this tool against any system, you must obtain:

1. Written authorization from the system owner (not just verbal agreement).
2. A clearly defined scope: which systems, networks, and time windows are included.
3. Explicit permission for each capability you plan to use (e.g., persistence, exfiltration, propagation).
4. An agreed-upon emergency contact and abort procedure.

See the Authorization Letter Template section below.

### Applicable Laws by Region

| Jurisdiction | Relevant Law | Key Provision |
|--------------|-------------|----------------|
| United States | Computer Fraud and Abuse Act (CFAA), 18 U.S.C. § 1030 | Criminalizes unauthorized access to computers and networks. Penalties up to 10+ years imprisonment. |
| European Union | Directive 2013/40/EU | Harmonizes criminal law on attacks against information systems across EU member states. |
| United Kingdom | Computer Misuse Act 1990 | Unauthorized access, with or without further criminal intent, is a criminal offense. |
| Canada | Criminal Code, Sections 342.1 and 430 | Unauthorized use of computer and mischief in relation to computer data. |
| Australia | Criminal Code Act 1995, Part 10.7 | Computer offenses include unauthorized access, modification, and impairment. |
| Germany | Strafgesetzbuch (StGB), Sections 202a–202d | Data espionage, interception, and preparation of such acts. |
| Brazil | Lei 12.737/2012 (Lei Carolina Dieckmann) | Criminalizes unauthorized access to computer devices. |

**This list is not exhaustive.** Nearly every jurisdiction in the world has laws that criminalize unauthorized computer access. When in doubt, consult a lawyer.

---

## Reporting Requirements

For professional engagements, you are responsible for:

1. **Pre-engagement**: Documenting the written authorization and scope agreement.
2. **During engagement**: Logging all actions taken (the server's logging module supports this).
3. **Post-engagement**: Providing a full report to the client, including all systems accessed, techniques used, and data handled.
4. **Data handling**: Destroying any sensitive data collected during the test per the agreed data handling policy.
5. **Incident escalation**: Immediately notifying the client if you discover evidence of an ongoing real attack during your engagement.

---

## Authorization Letter Template

Use the following template as a starting point. Have it reviewed and signed before any engagement. This template is provided for reference only and does not constitute legal advice.

---

**PENETRATION TESTING AUTHORIZATION LETTER**

Date: [DATE]

To Whom It May Concern,

I, [AUTHORIZED REPRESENTATIVE NAME], [TITLE], on behalf of [ORGANIZATION NAME] ("the Owner"), hereby authorize [TESTER NAME / COMPANY] to conduct authorized security testing on the systems and networks described below.

**Authorized Systems:**
- IP ranges / hostnames: [LIST SPECIFIC SYSTEMS]
- Network segments: [IF APPLICABLE]

**Testing Period:**
- Start: [DATE AND TIME]
- End: [DATE AND TIME]

**Authorized Activities:**
- [ ] Network scanning and enumeration
- [ ] Vulnerability scanning
- [ ] Exploitation and proof-of-concept attacks
- [ ] Post-exploitation activities (specify: [LIST])
- [ ] Persistence mechanisms
- [ ] Social engineering (specify: [LIST])
- [ ] Physical security testing

**Out of Scope:**
- [LIST EXPLICITLY EXCLUDED SYSTEMS, TECHNIQUES, OR ACTIONS]

**Emergency Contact:**
- Name: [NAME]
- Phone: [NUMBER] (available 24/7 during testing period)

**Data Handling:**
All data collected during testing will be [DESTROYED / RETURNED] within [NUMBER] days of engagement completion.

**Signature:** _________________________
**Printed Name:** [NAME]
**Title:** [TITLE]
**Organization:** [ORGANIZATION]
**Date:** [DATE]

---

This authorization is valid only for the systems, time period, and activities listed above. Any activity outside this scope is not authorized.

---

## Acknowledgment

By using BackDoors_1.1, you acknowledge that:

1. You have read this Ethical Use Policy in full.
2. You hold or will hold written authorization before deploying this tool against any system.
3. You accept full legal and ethical responsibility for how you use this software.
4. The authors and contributors of this software bear no responsibility for your actions.
