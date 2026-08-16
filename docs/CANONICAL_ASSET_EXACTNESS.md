# Canonical Asset Exactness Rule

Status: adopted

For any Nexkosmo visual asset marked `FROZEN` or `APPROVED`, **exact means exact**.

A frozen canonical asset must be reused from its authoritative source file. It must not be recreated from memory, redrawn by an image model, approximated by a prompt, recolored, retraced, or visually reconstructed.

When a frozen asset must appear inside a screenshot, mockup, or generated composition, the asset itself must be inserted deterministically from the canonical source. Generative tools may create or edit the surrounding content, but they must not regenerate the frozen asset.

If the available tooling cannot perform exact deterministic placement, the operation must stop and report that limitation rather than returning an approximation and calling it exact.

For partial page edits, only the explicitly requested region may change. Unrequested regions and frozen assets must remain unchanged.

Acceptance rule:

`exact source retrieval -> deterministic placement -> identity validation -> accept`

A visually similar result is a failure when exact identity is required.

This rule applies to the Nexkosmo logo, approved character identities, canonical props, approved environments, locked screenplay material, approved UI brand assets, and any future asset or state explicitly promoted to canon.
