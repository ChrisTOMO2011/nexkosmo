# Nexkosmo Repository Protection Policy

Status: APPROVED ENGINEERING GOVERNANCE
Owner: Director
Alignment steward: ChatGPT
Last updated: 2026-08-19

## Purpose

Protect `main` so repository canon, CI evidence, and approved implementation cannot be bypassed by an accidental direct push or an unvalidated merge.

## Current verified repository state

As verified on 2026-08-19, `main` is not protected and required status checks are not enforced by GitHub settings. This is a governance STOP GATE.

Repository files such as `CODEOWNERS`, `AGENTS.md`, CI workflows, and alignment scripts do not by themselves prevent a repository administrator from bypassing the intended process. GitHub branch protection or a branch ruleset must enforce the merge path.

## Minimum safe configuration for the current owner-led repository

Target branch: `main`

Required rules:

1. Require a pull request before merging.
2. Require the `quality-and-integration` status check to pass before merging.
3. Require the branch to be up to date before merging when GitHub exposes that option for the selected status check policy.
4. Require conversation resolution before merging.
5. Block force pushes.
6. Block deletion of `main`.
7. Apply the rules to repository administrators/owners as well; do not create a standing bypass that makes the protection advisory.

## Solo-owner review constraint

Do not require a numeric approving review or required CODEOWNER review while the only available approver is also the pull-request author.

GitHub does not allow a pull-request author to approve their own pull request. Enabling a mandatory approval or mandatory CODEOWNER approval with no independent eligible reviewer can deadlock the repository.

Until an independent reviewer is available, Director approval is recorded explicitly in the pull-request conversation and the merge gate is:

`Director decision -> PR -> green required CI -> resolved conversations -> merge`

`CODEOWNERS` remains useful for ownership documentation and automatic review routing, but it must not be configured as a required approval gate until at least one independent eligible reviewer exists.

## Team hardening when an independent reviewer exists

Once Nexkosmo has at least one trusted independent reviewer with the required repository access, strengthen the ruleset to add:

- at least 1 approving review;
- required review from Code Owners for owned paths;
- dismissal of stale approvals when new commits are pushed;
- approval of the most recent reviewable push where practical.

At that point the merge gate becomes:

`Director-approved direction -> PR -> independent review -> required CI -> resolved conversations -> merge`

## Required checks

The required CI check is the GitHub Actions job:

`quality-and-integration`

That job currently covers canonical asset verification, alignment verification, Ruff, mypy, migration compilation, CI environment preparation, and Docker integration tests.

A future change may split this into multiple required checks, but no replacement may reduce coverage silently.

## Change rule

Changes to this protection policy require explicit Director approval and must be reviewed together with any affected `CODEOWNERS`, CI, alignment, or current-state changes.

The alignment steward must re-check actual GitHub settings after material governance changes. Repository documentation is not proof that the settings are active.
