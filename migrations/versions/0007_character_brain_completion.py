"""complete the pre-production character brain

Revision ID: 0007_character_brain_completion
Revises: 0006_foundation_least_privilege
"""

from alembic import op

revision = "0007_character_brain_completion"
down_revision = "0006_foundation_least_privilege"
branch_labels = None
depends_on = None


SPECIES = (
    (
        "human",
        ("Identity", "Face", "Hair", "Skin", "Eyes", "Beard", "Age", "Expression"),
        0,
        120,
        120,
        230,
        "Skin Tone",
        ("hair", "beard", "wears-accessories"),
    ),
    (
        "elf",
        ("Identity", "Face", "Hair", "Skin", "Eyes", "Age", "Expression"),
        0,
        500,
        130,
        240,
        "Skin Tone",
        ("hair", "wears-accessories"),
    ),
    (
        "goblin",
        ("Identity", "Face", "Skin", "Eyes", "Age", "Expression"),
        0,
        180,
        70,
        170,
        "Skin Tone",
        ("wears-accessories",),
    ),
    (
        "orc",
        ("Identity", "Face", "Hair", "Skin", "Eyes", "Beard", "Age", "Expression"),
        0,
        180,
        140,
        260,
        "Skin Tone",
        ("hair", "beard", "wears-accessories"),
    ),
    (
        "robot",
        ("Identity", "Face", "Skin", "Eyes", "Expression"),
        0,
        500,
        60,
        320,
        "Surface Finish",
        ("modular-body",),
    ),
    (
        "dragon",
        ("Identity", "Skin", "Eyes", "Age", "Expression"),
        0,
        2000,
        80,
        400,
        "Scale Tone",
        ("creature-rig",),
    ),
    (
        "alien",
        ("Identity", "Face", "Skin", "Eyes", "Age", "Expression"),
        0,
        600,
        80,
        300,
        "Surface Tone",
        ("modular-body", "wears-accessories"),
    ),
    (
        "monkey",
        ("Identity", "Face", "Hair", "Skin", "Eyes", "Age", "Expression"),
        0,
        80,
        50,
        220,
        "Fur Tone",
        ("hair", "wears-accessories"),
    ),
    (
        "demon",
        ("Identity", "Face", "Skin", "Eyes", "Age", "Expression"),
        0,
        1000,
        100,
        300,
        "Skin Tone",
        ("wears-accessories",),
    ),
)


def _uuid(namespace: int, sequence: int) -> str:
    return f"{namespace:08x}-0000-4000-8000-{sequence:012x}"


def _array(values: tuple[str, ...]) -> str:
    return (
        "ARRAY[" + ",".join("'" + value.replace("'", "''") + "'" for value in values) + "]::text[]"
    )


def _seed_asset(
    *,
    asset_id: str,
    name: str,
    category: str,
    subcategory: str,
    species_id: str | None,
    capability: str | None = None,
    metadata: str = "{}",
) -> None:
    required = _array((capability,)) if capability else "ARRAY[]::text[]"
    op.execute(
        f"""
        INSERT INTO character_asset_manifests (
            asset_id, workspace_id, name, category, subcategory,
            thumbnail_reference, preview_reference, source, status, tags,
            required_capabilities, provenance, visibility, profile_metadata
        ) VALUES (
            '{asset_id}', NULL, '{name.replace("'", "''")}', '{category}', '{subcategory}',
            'brain://assets/{asset_id}/thumbnail', 'brain://assets/{asset_id}/preview',
            'development-seed', 'development-placeholder',
            ARRAY['development-seed','phase-3']::text[], {required},
            '{{"seed": true, "phase": 3}}'::jsonb, 'global', '{metadata}'::jsonb
        )
        ON CONFLICT (asset_id) DO UPDATE SET
            name = EXCLUDED.name, category = EXCLUDED.category,
            subcategory = EXCLUDED.subcategory,
            required_capabilities = EXCLUDED.required_capabilities,
            profile_metadata = EXCLUDED.profile_metadata, updated_at = now()
        """
    )
    if species_id:
        op.execute(
            f"""
            INSERT INTO character_asset_species (workspace_id, asset_id, species_id)
            VALUES (NULL, '{asset_id}', '{species_id}')
            ON CONFLICT (asset_id, species_id) DO NOTHING
            """
        )


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE characters
            ADD COLUMN identity_type text NOT NULL DEFAULT 'Human Male',
            ADD COLUMN age integer NOT NULL DEFAULT 35 CHECK (age BETWEEN 0 AND 2000),
            ADD COLUMN apparent_age integer NOT NULL DEFAULT 35
                CHECK (apparent_age BETWEEN 0 AND 2000),
            ADD COLUMN height_cm integer NOT NULL DEFAULT 180 CHECK (height_cm BETWEEN 30 AND 400),
            ADD COLUMN body_type text NOT NULL DEFAULT 'Athletic' CHECK (btrim(body_type) <> ''),
            ADD COLUMN skin_tone integer NOT NULL DEFAULT 89 CHECK (skin_tone BETWEEN 0 AND 100),
            ADD COLUMN gender_presentation text,
            ADD COLUMN physical_profile_version bigint NOT NULL DEFAULT 1
                CHECK (physical_profile_version > 0),
            ADD COLUMN style_profile_id uuid
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            ADD COLUMN readiness_status text NOT NULL DEFAULT 'incomplete'
                CHECK (readiness_status IN (
                    'incomplete','invalid','processing-required','ready-for-set'
                )),
            ADD COLUMN validation_issues jsonb NOT NULL DEFAULT '[]'::jsonb,
            ADD COLUMN validated_version bigint,
            ADD COLUMN validated_at timestamptz;

        ALTER TABLE species
            ADD COLUMN min_age integer NOT NULL DEFAULT 0 CHECK (min_age >= 0),
            ADD COLUMN max_age integer NOT NULL DEFAULT 250 CHECK (max_age >= min_age),
            ADD COLUMN min_height_cm integer NOT NULL DEFAULT 30 CHECK (min_height_cm >= 30),
            ADD COLUMN max_height_cm integer NOT NULL DEFAULT 400
                CHECK (max_height_cm >= min_height_cm),
            ADD COLUMN surface_control_label text NOT NULL DEFAULT 'Skin Tone';

        ALTER TABLE character_asset_manifests
            ADD COLUMN visibility text NOT NULL DEFAULT 'global'
                CHECK (visibility IN ('global','workspace','project','private')),
            ADD COLUMN attachment_point text,
            ADD COLUMN compatible_body_regions text[] NOT NULL DEFAULT '{}',
            ADD COLUMN profile_metadata jsonb NOT NULL DEFAULT '{}'::jsonb;

        UPDATE characters SET style_profile_id = type_id
        WHERE type_id IN (
            SELECT asset_id FROM character_asset_manifests
            WHERE category = 'identity' AND subcategory = 'visual-style'
        );
        UPDATE characters SET type_id = NULL WHERE style_profile_id IS NOT NULL;
        UPDATE character_asset_manifests
        SET category = 'style-profile',
            profile_metadata = jsonb_build_object(
                'render_style', lower(replace(name, ' ', '-')),
                'shader_family', lower(replace(name, ' ', '-')),
                'texture_profile', 'default',
                'material_profile', 'default',
                'geometry_profile', 'default',
                'preview_profile', 'development-placeholder'
            )
        WHERE category = 'identity' AND subcategory = 'visual-style';
        CREATE INDEX characters_readiness_idx
            ON characters(workspace_id, readiness_status, updated_at DESC);
        """
    )

    capability_by_tab = {
        "Identity": "customises-identity",
        "Face": "customises-face",
        "Skin": "customises-skin",
        "Eyes": "customises-eyes",
        "Age": "customises-age",
        "Expression": "customises-expression",
    }
    for index, (key, tabs, min_age, max_age, min_height, max_height, label, legacy) in enumerate(
        SPECIES, start=1
    ):
        capabilities = tuple(
            dict.fromkeys(
                (
                    "facial-animation",
                    "voice",
                    *(capability_by_tab[tab] for tab in tabs if tab in capability_by_tab),
                    *legacy,
                )
            )
        )
        op.execute(
            f"""
            UPDATE species SET capabilities = {_array(capabilities)},
                supported_tabs = {_array(tabs)},
                min_age = {min_age}, max_age = {max_age}, min_height_cm = {min_height},
                max_height_cm = {max_height}, surface_control_label = '{label}',
                version = version + 1, updated_at = now()
            WHERE key = '{key}'
            """
        )
        species_id = _uuid(0x20000000 + index, index)
        category_specs = (
            ("face", "customises-face", ("Default Face", "Strong Jaw", "Soft Features")),
            ("skin", "customises-skin", ("Natural", "Warm", "Cool")),
            ("eyes", "customises-eyes", ("Brown Eyes", "Blue Eyes", "Amber Eyes")),
            ("age-preset", "customises-age", ("Young Adult", "Adult", "Mature")),
            ("expression", "customises-expression", ("Neutral", "Focused", "Concerned")),
        )
        if "Hair" in tabs:
            category_specs += (("hair", "hair", ("Short", "Wavy", "Slicked Back")),)
        if "Beard" in tabs:
            category_specs += (("beard", "beard", ("Clean Shaven", "Stubble", "Full Beard")),)
        sequence = index * 100
        for category_offset, (category, capability, names) in enumerate(category_specs, start=1):
            for name_offset, name in enumerate(names, start=1):
                _seed_asset(
                    asset_id=_uuid(0x42000000 + category_offset, sequence + name_offset),
                    name=f"{name} ({key.title()})",
                    category=category,
                    subcategory="preset",
                    species_id=species_id,
                    capability=capability,
                )

    accessory_groups = (
        ("hats", ("Fedora", "Beanie", "Wide Brim")),
        ("facial-hair", ("Moustache", "Goatee", "Sideburns")),
        ("smoke-pipes", ("Classic Pipe", "Slim Cigarette", "Cigar")),
        ("pimples-skin", ("Light Freckles", "Skin Texture", "Weathered")),
        ("scars-marks", ("Brow Scar", "Cheek Scar", "Face Mark")),
        ("earrings-jewelry", ("Stud", "Hoop", "Chain")),
        ("masks", ("Half Mask", "Respirator", "Tactical Mask")),
    )
    accessory_species = (1, 2, 3, 4, 7, 8, 9)
    for group_index, (subcategory, names) in enumerate(accessory_groups, start=1):
        for name_index, name in enumerate(names, start=1):
            asset_id = _uuid(0x43000000 + group_index, name_index)
            _seed_asset(
                asset_id=asset_id,
                name=name,
                category="accessory",
                subcategory=subcategory,
                species_id=None,
                capability="wears-accessories",
            )
            for species_index in accessory_species:
                species_id = _uuid(0x20000000 + species_index, species_index)
                op.execute(
                    f"""
                    INSERT INTO character_asset_species (workspace_id, asset_id, species_id)
                    VALUES (NULL, '{asset_id}', '{species_id}')
                    ON CONFLICT (asset_id, species_id) DO NOTHING
                    """
                )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
