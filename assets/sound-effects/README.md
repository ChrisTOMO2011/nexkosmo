# Nexkosmo Sound Effects Library

This directory is the canonical home for reusable sound effects registered with the Nexkosmo Brain.

## Storage model

```text
sound-effects/
├── source/          # Original files, preserved unchanged
├── library/         # Approved, organised production assets
│   ├── ambience/
│   ├── animals/
│   ├── crowds/
│   ├── foley/
│   ├── impacts/
│   ├── machinery/
│   ├── nature/
│   ├── sci-fi/
│   ├── ui/
│   ├── vehicles/
│   ├── voices/
│   ├── weather/
│   ├── weapons/
│   └── miscellaneous/
├── previews/        # Lightweight audition copies and waveform images
├── metadata/        # Brain-readable asset records and index
└── schemas/         # Validation rules for sound asset metadata
```

## Brain registration

Every approved sound receives a stable `asset_id` and one metadata record based on `schemas/sound-effect.schema.json`. The Brain uses the metadata index to search, filter, relate and reuse sounds without relying on filenames.

The original recording must remain in `source/`. Processing, renaming, normalisation and conversion produce a separate approved file under `library/`.

## Naming convention

```text
sfx_<category>_<subject>_<action-or-state>_<variant>_<asset-id>.<ext>
```

Example:

```text
sfx_animals_horse_gallop_dirt_001_nks-sfx-000001.wav
```

## Required metadata

- Stable asset ID
- Title and description
- Category and tags
- Source and approved file paths
- Duration, channels, sample rate and bit depth
- Loudness and peak level when measured
- Loopable and seamless-loop status
- Recording perspective and environment
- Licence, creator and provenance
- Quality and approval state
- Related 3D assets, scenes, projects and sounds
- Checksum for duplicate detection and integrity

Do not delete or overwrite source recordings after import. The Brain must retain provenance and be able to trace every derivative back to its original file.
