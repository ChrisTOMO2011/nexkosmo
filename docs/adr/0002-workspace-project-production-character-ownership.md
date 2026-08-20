# ADR 0002: Ownership hierarchy

Status: accepted.

Canonical ownership is Workspace -> Project -> Production -> Character.
Membership authorises Project access and every child repeats the workspace key
so foreign keys and forced RLS can enforce tenant isolation.
