"""
Script to create sample data for the questionnaire answering tool.
This creates the Excel questionnaire and other sample files.
"""

import pandas as pd
import os

# Create directories
os.makedirs('sample_data/reference_docs', exist_ok=True)

# Create the questionnaire as CSV (can be opened as Excel)
questionnaire_data = {
    'Question Number': list(range(1, 16)),
    'Category': [
        'Company Overview',
        'Security Governance',
        'Compliance',
        'Data Protection',
        'Access Control',
        'Infrastructure',
        'Incident Response',
        'Business Continuity',
        'Vendor Management',
        'Data Privacy',
        'Encryption',
        'Employee Training',
        'Vulnerability Management',
        'Logging and Monitoring',
        'Data Retention'
    ],
    'Question': [
        'What is your company\'s primary business and industry sector?',
        'Who is responsible for information security within your organization and to whom do they report?',
        'What security compliance certifications does your organization currently hold?',
        'How do you classify and handle sensitive data within your organization?',
        'What authentication methods are required for accessing your systems?',
        'Which cloud service providers do you use and in which regions are your services hosted?',
        'What is your process for detecting and responding to security incidents?',
        'What are your Recovery Time Objective (RTO) and Recovery Point Objective (RPO)?',
        'How do you assess and manage security risks from third-party vendors?',
        'How do you handle data subject access requests under GDPR or similar regulations?',
        'What encryption standards do you use for data at rest and in transit?',
        'What security awareness training do you provide to employees?',
        'How frequently do you conduct vulnerability assessments and penetration testing?',
        'What logging and monitoring capabilities do you have for security events?',
        'What are your data retention and deletion policies?'
    ]
}

df = pd.DataFrame(questionnaire_data)
df.to_excel('sample_data/questionnaire.xlsx', index=False)
print("Created: sample_data/questionnaire.xlsx")

# Also create as CSV for easier viewing
df.to_csv('sample_data/questionnaire.csv', index=False)
print("Created: sample_data/questionnaire.csv")

# Create additional reference documents
code_of_conduct = """# CloudSecure Solutions - Code of Conduct

## 1. Ethical Standards

### 1.1 Integrity
All employees must act with honesty and integrity in all business dealings. This includes:
- Accurate reporting of work hours and expenses
- Truthful communication with customers and colleagues
- Proper handling of company assets and resources

### 1.2 Confidentiality
Employees must protect confidential information:
- Customer data is strictly confidential
- Trade secrets and intellectual property protection
- Non-disclosure agreements honored

### 1.3 Conflict of Interest
Employees must avoid conflicts of interest:
- No outside employment with competitors
- No acceptance of gifts over $100 from vendors
- Personal investments disclosed

## 2. Security Responsibilities

### 2.1 Acceptable Use
- Company systems used for business purposes only
- No installation of unauthorized software
- Social engineering awareness and reporting

### 2.2 Data Protection
- Customer data accessed only on need-to-know basis
- Secure disposal of confidential documents
- Immediate reporting of lost or stolen devices

### 2.3 Incident Reporting
- All security incidents must be reported within 1 hour
- Phishing attempts reported to security@cloudsecure.com
- Suspicious activity immediately escalated

## 3. Compliance Requirements

### 3.1 Regulatory Compliance
- All employees complete annual compliance training
- Industry-specific regulations followed
- Export control regulations observed

### 3.2 Policy Acknowledgment
- Annual acknowledgment of security policies
- Code of conduct signed by all employees
- Regular policy updates communicated
"""

with open('sample_data/reference_docs/code_of_conduct.md', 'w') as f:
    f.write(code_of_conduct)
print("Created: sample_data/reference_docs/code_of_conduct.md")

# Create privacy policy
privacy_policy = """# CloudSecure Solutions - Privacy Policy

## 1. Data Collection

### 1.1 Information We Collect
We collect the following types of information:
- Account information (name, email, company)
- Usage data and system logs
- Customer cloud infrastructure metadata
- Support communications

### 1.2 How We Collect Data
- Directly provided by customers during signup
- Automatically collected through platform usage
- Third-party integrations with customer consent

## 2. Data Use

### 2.1 Primary Purposes
- Provide GuardianCloud security services
- Customer support and communication
- Product improvement and development
- Security monitoring and threat detection

### 2.2 Data Processing
- Automated processing for security analysis
- Manual review for customer support
- No sale of personal data to third parties

## 3. Data Sharing

### 3.1 Third-Party Processors
We share data only with:
- AWS (cloud infrastructure)
- Okta (identity management)
- Zendesk (customer support)
- Data processors under contract

### 3.2 Legal Requirements
We may disclose data when required by:
- Valid legal process
- Protection of rights and safety
- Compliance with applicable laws

## 4. Data Rights

### 4.1 Individual Rights
Data subjects have the right to:
- Access their personal data
- Request correction or deletion
- Object to processing
- Data portability

### 4.2 Exercising Rights
Contact privacy@cloudsecure.com to exercise data rights.

## 5. Data Security

### 5.1 Security Measures
- Encryption at rest and in transit
- Access controls and monitoring
- Regular security assessments
- Employee training on data protection

### 5.2 Data Breaches
- Notification within 72 hours
- Regulatory notification as required
- Customer notification when appropriate
"""

with open('sample_data/reference_docs/privacy_policy.md', 'w') as f:
    f.write(privacy_policy)
print("Created: sample_data/reference_docs/privacy_policy.md")

print("\\nAll sample data files created successfully!")
print("\\nYou can now:")
print("1. Upload the reference documents (sample_data/reference_docs/*.md)")
print("2. Upload the questionnaire (sample_data/questionnaire.xlsx)")
print("3. Generate answers using the RAG system")
