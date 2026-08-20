# ADR 0005: Forced RLS and membership

Status: accepted.

Application authorisation and database isolation are complementary. Services
enforce Owner/Admin/Editor/Viewer permissions; tenant tables force RLS using the
transaction workspace setting. Neither layer may be bypassed for convenience.
