# Standard Operating Procedures (SOPs) - Broking Operations

**Compiled By:** Motilal Oswal Operations Team | **Effective:** 2026 | **Classification:** Internal

---

## SOP 1: ACCOUNT OPENING AND KYC VERIFICATION

### 1.1 Initial Contact and Documentation Request

**Initiator:** Sales Team / Front Desk  
**Timeline:** Immediate on customer inquiry

**Steps:**
1. Customer visits branch or registers online
2. Sales representative explains account types and products
3. Provide KYC checklist and required documents
4. Explain SEBI regulations and disclosure requirements

**Required Documents Checklist:**
- [ ] PAN card (copy and original for verification)
- [ ] Aadhaar/Voter ID/Passport (address proof)
- [ ] Bank statement or utility bill (not older than 3 months)
- [ ] Passport-size photograph (2 copies)
- [ ] Income proof (salary slip/ITR/business docs)
- [ ] Occupation and income details form
- [ ] Risk profile questionnaire
- [ ] Client agreement (signed)
- [ ] Mandate form for digital operations

### 1.2 KYC Document Verification

**Responsible Person:** KYC Officer / Back Office  
**Timeline:** 24-48 hours

**Verification Process:**
1. Receive physical/scanned documents
2. Verify PAN with Income Tax portal (real-time validation)
3. Match documents for consistency (name, address, signatures)
4. Check for duplicate PAN in system
5. Perform CIBIL/credit history check
6. Screen for Politically Exposed Person (PEP) status
7. Mark KYC status as "Pending" in system

### 1.3 Video-based or In-Person KYC

**Method 1: Video-based (eKYC)**
- Use NSDL/CDSL approved vendor
- Verification through Aadhaar OTP
- Real-time verification
- Approval: Same day (within 2-4 hours)

**Method 2: In-Person Verification (IPV)**
- Relationship Manager visits customer location
- Physical document verification
- Customer signature authentication
- Photo verification against ID
- Timeline: Approval within 48 hours of IPV

### 1.4 Account Activation

**Responsible Person:** Back Office Coordinator  
**Timeline:** After KYC approval + 24 hours

**Steps:**
1. Receive KYC approval notification
2. Generate Client ID and credentials
3. Set up Demat account with NSDL/CDSL
4. Link bank account for fund transfers
5. Provide login credentials via secure channel
6. Send account activation notification
7. Document all registration details

**Completion:** Mail physical welcome kit within 3 days

---

## SOP 2: ACCOUNT FUNDING AND CASH MANAGEMENT

### 2.1 Deposit/Fund Receipt

**Responsible Person:** Operations Team  
**Timeline:** Real-time to 2 hours

**Bank Transfer (NEFT/RTGS):**
1. Customer initiates transfer from their registered bank account
2. Funds should be deposited to broker's designated ESCROW account
3. Account number: ESCROW-[BROKER-CODE]-[EXCHANGE]
4. Check funds receipt in real-time dashboard
5. System automatically credits trading account
6. Confirmation email sent to customer

**Process:**
```
Customer Bank → NEFT/RTGS → Broker Escrow Account (SEBI-mandated segregation)
→ Real-time booking in trading terminal → Available for trading
```

### 2.2 Fund Reconciliation

**Daily Process:**
1. Morning: Prepare opening balance report
2. Reconcile bank deposits vs system bookings (within 1 hour)
3. Identify discrepancies
4. Follow-up on unmatched transactions
5. EOD (End of Day): Prepare closing statement
6. Reconciliation report to compliance: 10:00 AM next day

**Discrepancy Resolution:**
- If unmatched > ₹1 lakh: Immediate escalation to senior management
- Timeline: Resolve within 24 hours
- Documentation: Maintain discrepancy register

### 2.3 Withdrawal Processing

**Customer Request:**
1. Customer requests withdrawal (online portal, phone, branch)
2. Verify KYC and account status
3. Check available balance (must include 1-2 day T+1 settlement pending amount)
4. Confirm beneficiary bank account (same as account opening)

**Processing:**
1. Prepare withdrawal slip with customer signature
2. Verify authorization limits (manager approval for >₹5 lakh)
3. Initiate bank transfer via NEFT/RTGS
4. Processing time: 1-2 business days
5. Send confirmation email with transaction reference

**Restrictions:**
- Cannot withdraw settlement-pending amounts until T+1 completion
- Margin requirement enforcement: Cannot withdraw if margin < maintenance level
- Peak period (market hours): May take 2-3 hours longer

---

## SOP 3: TRADE EXECUTION AND ORDER MANAGEMENT

### 3.1 Pre-Trade Validation

**Responsible Person:** Trading Terminal System (Automated) + Manual Review  
**Timeline:** Within seconds of order entry

**Automated Checks:**
1. Client active status verification
2. KYC compliance status check
3. Account suspension/blocking verification
4. Order quantity vs available margin calculation
5. Price band checking (±10% for most stocks, ±20% for volatile)
6. Corporate action order restrictions
7. Position limit checks vs NSE/BSE regulations

**Manual Intervention Points:**
- If margin shortfall: Order rejected, notification sent
- If price suspicious: Trading desk supervisor review
- If high volume order: Risk management check
- If unusual pattern detected: Surveillance team alert

### 3.2 Order Entry and Acknowledgment

**Order Entry Process:**
1. Customer places order through trading terminal/app
2. Order forwarded to exchange within 100 milliseconds
3. Exchange validates order against market rules
4. Confirmation sent back to broker terminal
5. Status updated to "Pending" on customer terminal

**Order Confirmation Sent To:**
- Customer trading terminal (real-time)
- Customer registered email/SMS (within 30 seconds)
- Broker order record system

**Order States:**
```
Pending → Executed (Partial/Full) → Settled → Closed
      ↓          ↓            ↓           ↓
   Rejected  Cancelled    Cancellation  Delivery/
            Expired       Processed     Settlement
```

### 3.3 Trade Execution

**Execution Mechanism:**
1. Order matched at exchange (NSE/BSE automated matching)
2. Execution confirmation received
3. Price recorded: Entry price for accounting
4. Quantity executed: Partial/full execution possible
5. Execution ID generated (NSE reference number)

**Execution Notification:**
- Real-time update on trading terminal
- Execution slip generated (downloadable)
- Email notification with execution details
- SMS alert to mobile (optional feature)

**Post-Execution:**
- Trade captured in customer statement
- Margin requirements updated
- Risk parameters recalculated
- M2M (Mark-to-Market) calculation begins

---

## SOP 4: SETTLEMENT AND DELIVERY PROCESS

### 4.1 T+1 Settlement Preparation

**Timeline:** Next business day after trade execution  
**Responsible Party:** Settlement Team

**Pre-Settlement (Day T):**
1. 5:00 PM: Collect all executed trades from exchange
2. Netting process: Combine buy/sell for each security
3. Net settlement obligation calculated
4. Margin requirement finalized
5. Failed trade reporting (if any)

**Settlement Obligation Example:**
- Customer buys 100 HDFC @ ₹2,500 = ₹2,50,000 obligation
- Customer sells 50 TCS @ ₹3,500 = ₹1,75,000 credit
- Net obligation: Pay ₹2,50,000, receive ₹1,75,000
- Final: Pay ₹75,000 (or less if other pending settlements)

### 4.2 Settlement Execution

**Settlement Day (T+1) Process:**

**Morning (Before 2:00 PM):**
1. Download settlement file from exchange (NSCC/NSDL)
2. Verify settlement amounts vs system records
3. Prepare cash settlement instruction
4. Release funds via RTGS to exchange account

**Funds Flow:**
```
Broker's Bank Account → RTGS → NSCC Settlement Account
→ Security Delivery (NSDL/CDSL) → DPs (Depository Participants)
→ Customer's Demat Account
```

**Settlement Status Verification (3:30 PM onwards):**
1. Check settlement completion status at exchange
2. Verify security credit in Demat account
3. Log failed settlements (if any) for next day
4. Generate settlement confirmation report

### 4.3 Failed Settlement Recovery

**On Settlement Failure:**
1. Document reason for failure (fund shortage, technical issue)
2. Contact customer for additional funds (if applicable)
3. Prepare contingency settlement for next day
4. Interest charges apply for failed settlements (broker's responsibility)
5. Report to compliance and exchange within 24 hours

**Interest Calculation:**
- For cash shortage: 2-3% per day from T+1 date
- For security shortage: As per exchange rules
- Recovery process: Auto-debit from customer margin account

---

## SOP 5: MARGIN CALL AND POSITION MANAGEMENT

### 5.1 Margin Requirement Calculation

**Real-time Monitoring:**

**Initial Margin (IM):**
- Equity Delivery: 20-25% of transaction value
- Equity Intraday: 5-10% depending on stock liquidity
- Futures: 8-15% (SPAN margin based on Greeks)
- Options: Complex calculation based on strike, expiry, Greeks

**Maintenance Margin (MM):**
- Typically 75-80% of Initial Margin
- Position auto-closed if MM breached

### 5.2 Margin Call Process

**Trigger Point:**
- Daily end-of-day M2M loss exceeds MM threshold

**Margin Call Initiation (Real-time during trading, Daily EOD review):**

| Time | Action | Details |
|------|--------|---------|
| **EOD (3:40 PM)** | M2M Calculation | Day's profit/loss calculated |
| **3:45-4:00 PM** | Margin Status Check | Maintenance margin evaluated |
| **4:00-4:15 PM** | Notification Send | Email/SMS if shortfall exists |
| **4:15 PM-6:00 PM** | Customer Response | Customer can deposit or close positions |
| **6:00 PM** | Auto-Liquidation Start | If no response, broker initiates forced closure |

**Margin Call Notification Content:**
- Shortfall amount
- Available margin balance
- Margin requirement
- Deadline for remediation (typically 1-3 hours)
- Action items: Deposit funds or close positions

### 5.3 Position Liquidation

**Forced Liquidation Procedure:**

**If Margin Call Not Remedied:**
1. Broker initiated forced closure at market price
2. Positions squared-off starting high-volatility positions
3. Auto-square-off happens at best available market price
4. Losses crystallized and debited to customer account
5. Confirmation immediately sent to customer
6. Written notice within 24 hours with full details

**Liquidation Order Priority:**
1. Highest loss-making positions first (to minimize cascade)
2. Most liquid counters first (highest probability of execution)
3. Leveraged positions priority (reduce broker's risk)

**Post-Liquidation:**
- Margin shortfall covered from customer's cash balance
- If insufficient: Amount converted to account receivable
- Recovery process initiated
- Account suspension till recovery

---

## SOP 6: GRIEVANCE REDRESSAL

### 6.1 Grievance Reception

**Channels Available:**
1. Online portal: www.brokersite.com/grievance
2. Email: grievances@broker.com
3. Phone: 1800-BROKER-1 (weekdays 9 AM - 6 PM)
4. Physical: Branch visit with written complaint
5. SMS: COMPLAINT [Details] to broker's registered number

**Recording:**
- Generate ticket number immediately
- Acknowledge receipt within 1 hour
- Assign to grievance officer
- Enter into system with timestamp

### 6.2 Grievance Investigation

**Timeline:** 3-7 days for resolution

**Process:**
1. **Day 1:** Detailed investigation plan prepared
2. **Day 2-3:** Evidence collection (trade records, confirmations, communications)
3. **Day 4:** Root cause analysis and fact-finding
4. **Day 5-6:** Escalation if needed (to compliance/management)
5. **Day 7:** Resolution decision communicated to customer

**Resolution Options:**
- Adjustment/reversal (if broker error): Same day
- Compensation (if applicable): 3-5 days processing
- Explanation letter: 1 day
- Escalation to management: 7 days
- Referral to SEBI if unresolved: 10 days

### 6.3 Escalation Process

**If Customer Unsatisfied (Post 7 days):**
1. Escalate to Head of Compliance
2. Re-investigation with fresh perspective
3. Senior management review
4. Written decision letter within 15 days
5. If still unsatisfied: SEBI SCORES portal referral

---

## SOP 7: DAILY COMPLIANCE REPORTING

### 7.1 Intraday Reporting (Real-time)

**Automated Reports:**
- Member position monitoring (Every 15 minutes)
- Margin adequacy status (Real-time)
- Risk threshold alerts (If exceeded)
- Surveillance flag tracking (Ongoing)

**Manual Reviews:**
- Unusual trading patterns (End of each hour during market hours)
- Large trade scrutiny (Every ₹5 crore+ transaction)
- Related party transactions (Daily monitoring)

### 7.2 Daily End-of-Day Reporting

**Submission to NSE/BSE (by 12:00 noon next day):**
- [ ] Daily member report (DMR)
- [ ] Settlement status report
- [ ] Margin status and adequacy
- [ ] Risk utilization report
- [ ] Grievance count and resolution status
- [ ] Failed transactions detail
- [ ] Unusual transaction reporting

### 7.3 Regulatory Certifications

**Weekly Compliance Certificate (by Friday 12:00 PM):**
- Audit report on margin adequacy
- Compliance with position limits
- Client fund segregation verification
- Insurance coverage status

**Monthly Reporting:**
- Trading statistics: Volume, value, customer count
- Error and exception log
- Compliance officer certification
- Board approval (if required)

**Quarterly Audit:**
- Independent audit of settlement processes
- Customer fund verification
- IT security audit
- Risk assessment review

---

## SOP 8: CLIENT STATEMENT AND REPORTING

### 8.1 Daily Account Statement

**Generation:** After market close (4:00 PM daily)

**Contents:**
- Opening balance
- Transactions: Buy/sell trades
- Current positions with M2M value
- Available margin balance
- Settlement pending amounts
- Closing balance
- Margin utilization status

**Delivery Method:**
- Email (primary)
- Portal download option
- SMS summary (optional)
- Paper copy (on request)

### 8.2 Monthly Comprehensive Statement

**Generation:** By 5th of every month

**Contents:**
- Full month transaction summary
- All trades executed (quantity, price, date)
- Settlement and delivery confirmations
- Profit/loss statement (with tax data)
- Margin charges and interest (if applicable)
- Brokerage and other charges breakdown
- Quarter-end valuation (if applicable)
- Tax lot identification (for FIFO method)

**Delivery:**
- Email automatically
- Portal download with digital signature
- Paper copy if earlier statement requested

---

## SOP 9: ACCOUNT SUSPENSION AND CLOSURE

### 9.1 Account Suspension

**Triggers for Suspension:**
- Margin shortfall not remedied (>3 days)
- Regulatory action by SEBI
- Breach of compliance norms
- Fraudulent activity suspected
- Customer request for temporary suspension

**Suspension Process:**
1. Notify customer in writing (email + registered mail)
2. Provide reason for suspension
3. Timeline for resolution (usually 7 days)
4. Block order entry capability
5. Allow only order cancellations and position closures

**During Suspension:**
- Customer can close existing positions only
- Cannot place new orders
- Margin still collected for open positions
- Pending settlements processed normally

### 9.2 Account Closure

**Customer-initiated Closure:**
1. Written closure request submitted
2. Verify all positions squared-off
3. Verify settlement completion (T+1 settlement)
4. Verify no pending grievances
5. Demat account status check
6. Final statement generation
7. Refund of balance (if any) to registered bank account
8. Account marked as "Closed" in system
9. Archive records (minimum 5 years)

**Broker-initiated Closure (Force Closure):**
- Applicable post regulatory action
- Outstanding dues collection first
- Customer intimation 30 days advance notice
- All positions automatically squared-off
- Remaining balance refunded after 90 days

---

## SOP 10: SECURITY AND DATA PROTECTION

### 10.1 Customer Credential Management

**Password Requirements:**
- Minimum 8 characters: Mix of upper, lower, numbers, special characters
- Change every 90 days mandatory
- Previous 4 passwords cannot be reused
- Lost password: OTP-based reset (never email/SMS password)

**Multi-factor Authentication (MFA):**
- SMS OTP required for every trade execution
- Email verification for fund withdrawal
- Security question as additional layer
- Biometric option for mobile app (recommended)

### 10.2 Data Security

**Encryption Standards:**
- HTTPS (SSL/TLS) for all web connections
- AES-256 encryption for sensitive data storage
- End-to-end encryption for email communications

**Access Control:**
- Role-based access control (RBAC) for staff
- Segregation of duties (order entry ≠ settlement)
- Audit trail for all system access
- Monthly access review and recertification

### 10.3 Business Continuity

**Disaster Recovery:**
- Real-time backup at secondary data center
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 30 minutes
- Quarterly disaster recovery drills
- Documented recovery procedures

---

**Document Version:** 4.2 | **Last Updated:** May 2026  
**Approvals:** Chief Compliance Officer, Chief Operating Officer  
**Next Review Date:** May 2027
