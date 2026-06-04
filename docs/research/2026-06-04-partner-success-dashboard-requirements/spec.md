# Partner Success Command Center Dashboard — Requirements (verbatim)

_Captured: 2026-06-04. Source: Matt's wife (Partner Success Manager, edtech)._
_Format: requirements spec for a single source-of-truth dashboard combining Salesforce, Planhat, Snowflake, Support data, Contracts, Success Plans, Calendar._
_Status: scope expansion of the in-flight Partner Success dashboard work (see `project_data_viz_designer_in_flight` memory + `docs/research/2026-06-02-data-viz-agent/` strategic + build plans)._

_Filed verbatim by the parent session 2026-06-04 after a background `/wrap` agent flagged a gap in its prompt (only the Objective fragment had been pasted). The text below is the complete spec as the user provided it._

---

# Partner Success Command Center Dashboard Requirements

## Objective

Create a single source of truth that combines Salesforce, Planhat, Snowflake, Support data, Contracts, Success Plans, and Calendar activities into one dashboard that allows me to manage my entire portfolio of partners from one location.

The dashboard should answer these questions every day:

- Which partners need attention today?
- Why do they need attention?
- What action should I take?
- When is my next required touchpoint?
- Which accounts are at risk?
- Which accounts are approaching renewal?
- Which accounts are expansion opportunities?
- What is the overall health of my portfolio?

---

# Home Dashboard

## Portfolio Summary

Display:

- Total partners
- Active partners
- Top 15 partners
- Partners in renewal window
- At risk partners
- Partners with open escalations
- Partners requiring outreach this week

## Portfolio Health Snapshot

Display:

- Average health score
- Average sentiment score
- Average engagement score
- Accounts with declining usage
- Accounts with no touchpoint in 90+ days

---

# Daily Action Center

Automatically generate a prioritized task list.

Display:

- Partner Name
- Priority Score
- Reason for outreach
- Recommended action
- Due date

Examples:

- Renewal approaching
- Health score decline
- Usage decline
- No recent touchpoint
- Open escalation
- Support ticket aging
- Success plan overdue

---

# Calendar View

Automatically generate all required partner motions and activities.

Display:

- Check-ins
- QBRs
- Renewal meetings
- Strategic planning meetings
- Success plan reviews
- Sentiment updates
- Health checks
- Professional Development sessions

Allow:

- Monthly view
- Weekly view
- Upcoming tasks view

Show countdowns such as:

- 15 days until next check-in
- 45 days until QBR
- 90 days until renewal planning
- 120 days until renewal outreach

---

# Partner 360 View

When selecting a partner, display a complete account profile.

## Account Information

- District name
- Segment
- ARR
- State
- Assigned PSM
- Salesforce Account Owner
- Renewal date
- Contract start date
- Contract end date
- Funding source

## Contacts

- Champion
- Executive Sponsor
- Superintendent
- Technology Lead
- Family Engagement Lead
- Additional stakeholders

Include:

- Last interaction date
- Contact role
- Influence level
- Sentiment

---

# Account Timeline

Display complete partner history.

Merge data from:

- Salesforce
- Planhat
- Support
- Snowflake
- Success Plans
- Meetings

Timeline should include:

- Closed Won
- Kickoff
- Data Mapping
- Go Live
- Trainings
- QBRs
- Check-ins
- Success Plans
- Escalations
- Sentiment changes
- Renewal conversations
- Expansion conversations

---

# Lifecycle Tracking

Track where each partner is in the lifecycle.

## Deployment

- Needs Assessment
- Data Mapping
- Data Upload
- Validation
- Configuration

## BOI

- Training
- Go Live
- Adoption

## MOI

- Data Review
- Insights & Analysis

## Renewal

- Strategic Planning
- Success & Growth

Display:

- Current stage
- Date entered stage
- Days in stage
- Next milestone
- Next required activity

---

# Contract Center

Display all contract related information.

## Contract Documents

- Current contract PDF
- Previous contracts
- Amendments
- Renewal quotes
- Order forms

## Contract Details

- Contract start date
- Contract end date
- Renewal date
- Renewal type
- ARR
- Multi-year agreement status
- Schools included
- Licensed users
- Products purchased
- Professional Development purchased
- Professional Development remaining

## Contract Alerts

- 180 day renewal notice
- 120 day renewal notice
- 90 day renewal notice
- 60 day renewal notice
- 30 day renewal notice
- PD expiration alerts

---

# Usage & Adoption Dashboard

Pull directly from Snowflake.

## District Metrics

Display:

- Active users
- Active teachers
- Active administrators
- Messages sent
- Messages received
- Family engagement rate
- Family activation rate

## Trends

Display:

- Month over month growth
- Year over year growth
- Usage trends
- Adoption trends

Graphs:

- Messages over time
- Active users over time
- Family engagement over time

---

# School Level Adoption View

For districts with multiple schools.

Display:

- School name
- Usage level
- Health score
- Last activity date
- Adoption trend

Highlight:

- Highest performing schools
- Lowest performing schools
- Schools requiring intervention

---

# Family Engagement Dashboard

Display:

- Families invited
- Families activated
- Activation percentage
- Families reached
- Languages translated
- Read rates
- Response rates
- Two way conversation rates

Show trends:

- Current year vs previous year
- Current quarter vs previous quarter

---

# Top 15 Dashboard

Dedicated page for Community Top 15 partners.

Display:

- Health score
- Sentiment score
- Renewal date
- Usage trend
- Last touchpoint
- Next touchpoint
- Open risks
- Success plan status

Use color coding:

- Green = Healthy
- Yellow = Monitor
- Red = Risk

---

# Health Dashboard

Display health metrics.

Include:

- Usage
- Adoption
- Engagement
- Support activity
- Escalations
- Renewal risk
- Product utilization

Show:

- Current score
- Historical trend
- Health changes over time

---

# Sentiment Dashboard

Display:

- Current sentiment
- Last sentiment update
- Sentiment trend

Track:

- Green
- Yellow
- Red

Include:

- Reason for score
- Notes
- Action plan

---

# Success Plan Dashboard

Display:

- Success plan goals
- Goal owners
- Due dates
- Progress percentages
- Current status

Track:

- Goals completed
- Goals at risk
- Upcoming milestones

---

# Renewal Command Center

Organize renewals by timeline.

## Buckets

- 180 Days
- 120 Days
- 90 Days
- 60 Days
- 30 Days

Display:

- Renewal amount
- Health score
- Sentiment
- Renewal risk
- Expansion opportunity
- Renewal owner
- Status

---

# Support & Escalation Dashboard

Display:

- Open tickets
- Escalations
- Ticket aging
- Ticket themes
- Resolution history

Highlight:

- Accounts with multiple tickets
- High risk escalations
- Unresolved issues

---

# Expansion Opportunity Dashboard

Automatically identify accounts with:

- High adoption
- High usage
- High sentiment
- Strong engagement
- Additional school opportunities
- Additional product opportunities

Display:

- Potential opportunity
- Estimated value
- Reason flagged

---

# Professional Development Tracker

Display:

- PD purchased
- PD completed
- PD remaining
- Upcoming sessions
- Expiring sessions

Highlight:

- Unscheduled PD
- Expiring PD
- Underutilized PD

---

# Relationship Mapping

Display stakeholder relationships.

For each stakeholder:

- Name
- Title
- Role
- Influence level
- Sentiment
- Last interaction date

---

# AI Features (Future State)

- AI generated account summary
- AI generated QBR preparation
- AI generated renewal risk alerts
- AI generated outreach recommendations
- Weekly portfolio summary
- Automated executive briefing

### Example AI Summary

> ABC District is currently in MOI. Usage is up 12% over last quarter. Family activation is 78%. Renewal occurs in 114 days. No open support escalations. Sentiment remains Green. Recommended next action: schedule strategic planning meeting.

---

# Data Sources

## Salesforce

- Account data
- Contacts
- Opportunities
- Contracts
- Renewal information
- Quotes
- Product entitlements

## Planhat

- Success plans
- Notes
- Sentiment
- Health scores
- Activity history

## Snowflake

- Product usage
- Family engagement metrics
- Adoption metrics
- Activation metrics
- Messaging metrics
- School level usage

## Support Platform

- Tickets
- Escalations
- Resolution history

## Calendar

- QBRs
- Check-ins
- Renewal meetings
- Professional Development sessions

---

# Dashboard Priority Ranking Logic

Create a priority score using:

- Renewal timing
- Health score decline
- Sentiment decline
- Days since last touchpoint
- Open escalations
- Support ticket volume
- ARR
- Top 15 status
- Usage decline

Output:

## Today's Top Accounts Requiring Attention

Display:

- Partner
- Priority Score
- Reason
- Recommended Action

---

# Success Criteria

When I open the dashboard each morning, I should immediately know:

- Which partners need my attention today
- Why they need attention
- What action I should take
- Which renewals are approaching
- Which partners are at risk
- Which partners are growing
- Which partners are expansion opportunities

The dashboard should function as my daily operating system for managing my entire Partner Success portfolio.
