# Canonical Asset Identification

Every asset registered by the Brain receives:

1. A permanent Canonical Asset ID (human readable)
2. A UUID (machine identifier)
3. Registration timestamp
4. Version number
5. Metadata manifest

Examples:
- NK-HUM-00000001
- NK-WRW-00000042
- NK-3DM-00001258
- NK-SFX-00000491
- NK-VFX-00000123
- NK-CGI-00000076

The Canonical Asset ID never changes, even if the file is renamed, moved, reconstructed or versioned.

Every asset registration must create a metadata manifest containing the Canonical ID, UUID, taxonomy, provenance, relationships and version history.

The Brain must use the Canonical ID as the primary human reference across the entire platform.