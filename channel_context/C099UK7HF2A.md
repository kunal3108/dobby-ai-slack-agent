# Channel Context: C099UK7HF2A

## 🏷️ Channel Metadata
- **Channel ID**: `C099UK7HF2A`
- **Channel Name**: `#metrics-digest`
- **Purpose**: This channel is used for posting, summarizing, and retrieving daily/weekly/monthly metrics digests from the banking analytics system.

---

## 🔎 Common Intents in this Channel
- **lookup**: Retrieve a single data point from a digest.  
  - Example: "What was yesterday’s disbursement count?"  
  - Example: "Give me the TAT for CE-1 this week."  

- **file summary**: Summarize a file that was uploaded.  
  - Example: "Summarize the attached Excel report."  
  - Example: "Give me key highlights from today’s CSV."  

- **publish slack**: Post/publish digest updates into Slack.  
  - Example: "Publish today’s metrics digest."  
  - Example: "Push the weekly summary for deposits."  

- **summarize thread**: Summarize a long Slack thread of metrics discussion.  
  - Example: "Summarize this thread with key points."  

- **create jira_ticket / update jira ticket**: Rare in this channel, but may happen if a data quality issue is found.  

---

## 📊 Relevant Tables / Data Sources
- `bank_bankos_db_gold.asset_sourcing_application_details`
- `asset_sourcing_assignment_history`
- `loan_application_details`
- `bsgaccounting_gold.account_balance`

---

## 📈 Common Metrics
- CE-1 / CE-2 Turnaround Time (TAT)  
- Pending Disbursement Aging  
- Deposit Movement (credit/debit counts, balances)  
- Loan origination funnel drop-offs  

---

## 🛠️ Preferred Tools
- **publish_slack** → For sharing digest into channel  
- **lookup** → For retrieving numbers from knowledge base  
- **file summary** → For Excel/CSV uploads  
- **summarize thread** → For Slack thread digests  

---
