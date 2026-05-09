# Vibe Coding & AI Integration Patterns for Code Apps

## What Is Vibe Coding?

Vibe Coding is AI-assisted application generation where natural language descriptions
of business problems are translated into working Power Apps. The developer describes
intent, and an AI agent generates the solution architecture and code.

## The Plan Designer Workflow

When a user gives you a high-level description, act as the Plan Designer:

### Phase 1: Decompose Requirements

Ask the user to clarify:
- **Who** -- User personas and roles
- **What** -- Core data entities and relationships
- **How** -- Key workflows and business rules
- **Where** -- Integration points (connectors, external systems)

### Phase 2: Propose Data Model

Generate a Dataverse table structure:

```
Example for "Employee Leave Management App":

Tables:
  - Employee (extends Contact)
    - department: Choice (Engineering, Sales, HR, Marketing)
    - manager: Lookup(Employee)
    - leaveBalance: Number

  - LeaveRequest
    - employee: Lookup(Employee)
    - startDate: DateTime
    - endDate: DateTime
    - type: Choice (Annual, Sick, Personal, Parental)
    - status: Choice (Pending, Approved, Rejected, Cancelled)
    - approver: Lookup(Employee)
    - notes: Text (multiline)
```

### Phase 3: Design Component Hierarchy

```
App
├── Layout (sidebar nav + main content)
├── Pages
│   ├── Dashboard
│   │   ├── LeaveBalanceCard
│   │   ├── PendingRequestsList
│   │   └── TeamCalendar
│   ├── NewRequest
│   │   └── LeaveRequestForm
│   ├── MyRequests
│   │   └── RequestsTable (filterable)
│   └── Approvals (manager only)
│       └── ApprovalQueue
└── Shared Components
    ├── StatusBadge
    ├── DateRangePicker
    └── UserAvatar
```

### Phase 4: Generate Code

Only after the plan is approved, scaffold and implement:

1. `npx degit github:microsoft/PowerAppsCodeApps/templates/starter leave-app`
2. Set up data sources with `pac code add-data-source`
3. Implement screen by screen, starting with the data layer
4. Wire up routing, state management, and UI

## Prompt Patterns for Power Apps

### Definition Prompt (Initial Creation)
```
"Build a [type of app] that allows [persona] to [key action].
It should track [data entities] and support [key workflows].
The main screens should include [screen list]."
```

### Clarification Prompt (Understanding Generated Code)
```
"What does the [component name] do? How does it connect to [data source]?
What happens when [user action]?"
```

### Change Request Prompt (Modifying Specific Elements)
```
"Change the [component] to [new behavior]. Add a [new field] to [table].
Make the [screen] show [filtered data] instead of all records."
```

### Data Enhancement Prompt
```
"Add validation to ensure [business rule]. Create a calculated field
for [derived value]. Add a lookup relationship to [related table]."
```

## AI Builder Integration (Optional)

Code Apps can integrate with AI Builder custom prompts via Power Fx connectors.

### Pattern: Custom AI Prompt in Code App

1. Create an AI Builder custom prompt in the Power Platform
2. Add it as a data source: `pac code add-data-source --dataset <ai-prompt-name>`
3. Call the generated service:

```typescript
import { MyPromptService } from "./generated/services/MyPromptService";

const result = await MyPromptService.predict({
  inputText: userQuery,
  context: additionalContext,
});

// result contains the AI-generated response
```

### Available AI Models
- GPT-4o Mini (faster, cheaper)
- GPT-4o (more capable)
- Via Azure OpenAI Service

## Iterative Refinement Pattern

When building with Vibe Coding, follow this cycle:

```
1. DESCRIBE  →  User provides natural language intent
2. PLAN      →  Agent proposes data model + screens + flows
3. APPROVE   →  User reviews and approves (or modifies)
4. BUILD     →  Agent generates code, screen by screen
5. TEST      →  Run locally with `npm run dev`
6. REFINE    →  User provides feedback, agent adjusts
7. DEPLOY    →  `npm run build | pac code push`
```

**Key Rule:** Never skip from DESCRIBE to BUILD. Always go through PLAN and APPROVE.

## Common App Patterns

### CRUD App
- List view with search/filter
- Detail view with edit form
- Create form
- Delete confirmation dialog
- Data: single Dataverse table

### Dashboard App
- KPI cards at top
- Charts/graphs in middle
- Recent activity list at bottom
- Data: aggregated queries across multiple tables

### Approval Workflow App
- Submission form
- Queue/list view for approvers
- Status tracking timeline
- Notification triggers
- Data: request table + approval history table

### Data Entry / Forms App
- Multi-step wizard
- Validation at each step
- Draft save capability
- Summary before submission
- Data: complex entity with related records

## React Patterns for Code Apps

### Recommended Stack (from Starter Template)
- **React** -- UI framework
- **TanStack Query** -- Server state management (data fetching/caching)
- **React Router** -- Client-side routing
- **Zustand** -- Client state management
- **Radix UI** -- Accessible component primitives
- **Tailwind CSS** -- Utility-first styling

### Data Fetching with TanStack Query
```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ContactService } from "../generated/services/ContactService";

// Read
function useContacts(filter?: string) {
  return useQuery({
    queryKey: ["contacts", filter],
    queryFn: () => ContactService.getAll({ filter }),
  });
}

// Create
function useCreateContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Contact>) => ContactService.create(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contacts"] }),
  });
}

// Update
function useUpdateContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Contact> }) =>
      ContactService.update(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contacts"] }),
  });
}
```

### Routing
```typescript
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  { path: "/", element: <Dashboard /> },
  { path: "/contacts", element: <ContactList /> },
  { path: "/contacts/:id", element: <ContactDetail /> },
  { path: "/contacts/new", element: <ContactForm /> },
]);

function App() {
  return <RouterProvider router={router} />;
}
```

### State Management with Zustand
```typescript
import { create } from "zustand";

interface AppState {
  selectedContactId: string | null;
  setSelectedContact: (id: string | null) => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

const useAppStore = create<AppState>((set) => ({
  selectedContactId: null,
  setSelectedContact: (id) => set({ selectedContactId: id }),
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
```
