# Eng State - my-saas-app

## Last Updated
2025-01-15 14:32 UTC

## Current Focus
Implementing user authentication with OAuth providers (Google, GitHub)

## Active Work
| Task | Status | Notes |
|------|--------|-------|
| OAuth integration | In Progress | Google working, GitHub in review |
| Session management | Done | Using JWT with 7-day refresh |
| Rate limiting | Blocked | Waiting on Redis setup (DevOps) |

## Blockers
- [ ] Need Redis instance for rate limiting - raised with DevOps

## Recent Decisions
- 2025-01-15: Chose JWT over session cookies for stateless scaling
- 2025-01-14: Using Lucia for auth library (lighter than NextAuth for our needs)

## Context for Next Session
GitHub OAuth PR is ready for review. Tests pass locally but need to verify callback URL config in production. Rate limiting is the next priority once Redis is available—see `src/lib/rate-limit.ts` for the placeholder implementation.
