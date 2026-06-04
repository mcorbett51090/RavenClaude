# Use predefined/custom roles, not primitive

The primitive roles (Owner/Editor/Viewer) grant sweeping access and should never be the answer in production. Grant the predefined role that matches the job, or author a custom role when none fits, and use IAM Conditions to scope further. Owner on a project 'to make it work' is the most common over-grant in GCP.
