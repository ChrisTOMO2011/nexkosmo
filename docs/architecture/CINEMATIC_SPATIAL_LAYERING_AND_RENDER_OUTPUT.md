# Cinematic Spatial Layering and Render Output Contract

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD, READY, PRODUCTION, STUDIO, Brain, Continuity Engine, Render Orchestrator, Renderer Adapters, compositing and finishing  
**Related contracts:** `PHYSICS_FIRST_CINEMATOGRAPHY.md`, `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`, `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`, `BUILD_PROGRESSIVE_DISCLOSURE_UI.md`

## 1. Purpose

This contract defines two different forms of layering that must not be confused:

1. **Cinematic spatial layering** — how a Shot is constructed as a believable volume in front of the camera.
2. **Render/output layering** — how physically and creatively useful image information is preserved as separate outputs for compositing, finishing, validation and targeted revision.

The governing rules are:

> A cinematic frame is treated as a structured volume, not merely a flat picture. Brain should reason about foreground, subject, midground, background and deeper spatial relationships through real geometry, distance, occlusion, parallax, focus, lighting, contrast, atmosphere and movement.

> Preserve the richest physically meaningful output for as long as practical and flatten only when delivery requires it.

These rules extend the physics-first cinematography contract. They do not require every Shot to use every spatial or render layer, and they do not prohibit intentional flatness or stylisation.

## 2. Spatial layering is not file layering

A foreground object and a foreground render pass are not the same thing.

Spatial layering describes where things exist relative to the camera and each other.

Render/output layering describes how the resulting image information is separated or preserved after execution.

Nexkosmo must keep these concepts distinct in canonical state, UI terminology and renderer contracts.

## 3. Cinematic spatial volume

A Shot may contain any useful combination of spatial zones such as:

```text
camera
-> extreme foreground
-> foreground
-> principal subject plane
-> secondary subject / midground
-> background
-> deep background / atmosphere
```

These zones are descriptive, not mandatory slots.

A strong Shot may contain only one dominant plane. Another may deliberately use many depth relationships. The Director's intent governs the design.

## 4. What creates perceived depth

Spatial depth should emerge from coherent physical and perceptual relationships including, where relevant:

- camera-to-object distance;
- relative object scale;
- perspective;
- occlusion;
- parallax during camera or subject movement;
- focal plane and optical focus falloff;
- depth of field;
- atmospheric perspective;
- haze, mist, rain, smoke and volume density;
- illumination falloff;
- shadow placement;
- contrast separation;
- colour separation;
- reflected light;
- edge separation;
- foreground motion;
- background motion;
- lens characteristics;
- exposure and tone response.

A blur mask alone is not sufficient evidence of true spatial depth.

## 5. Parallax as physical evidence

When the camera moves, objects at different physical distances should produce distance-consistent relative motion where the route claims geometric fidelity.

Conceptually:

```text
near foreground -> largest apparent screen displacement
subject plane   -> intermediate displacement
far background  -> smallest apparent displacement
```

The exact relationship depends on camera path, orientation, field of view and geometry.

If an AI route creates visually plausible movement but does not preserve physically coherent depth/parallax, Nexkosmo must not label that result geometry-valid or physics-valid for that requirement.

## 6. Occlusion and continuity

Objects that occupy the same world must occlude one another consistently with geometry and camera position unless the Director intentionally overrides physical behaviour.

Spatial layering must therefore remain coupled to:

- canonical transforms;
- character blocking;
- prop placement;
- environment geometry;
- camera state;
- lens/filmback state;
- continuity revisions.

A foreground element does not become a purely decorative overlay merely because it is close to camera.

## 7. Focus is one depth cue, not the definition of layering

Cinematic layering must not be reduced to shallow depth of field.

A deeply focused frame may have powerful spatial depth through perspective, overlap, movement, lighting, atmosphere, production design and scale.

Likewise, a heavily blurred background may still feel flat if the underlying geometry, perspective and light relationships are inconsistent.

The permanent rule is:

> Depth of field can reveal or suppress spatial layers; it does not create the underlying spatial truth.

## 8. Lighting across depth

Lighting should support the Shot's spatial and emotional structure without requiring every plane to be separately lit.

Brain/Producer may reason about:

- foreground silhouette or exposure;
- subject-key relationship;
- midground separation;
- practical lights in depth;
- background luminance structure;
- negative fill;
- pools of light;
- motivated light falloff;
- atmospheric light shafts or scattering;
- reflective continuity between planes.

The goal is not to maximize separation. The Director may deliberately merge subject and background, obscure a plane or compress tonal depth.

## 9. Layering for audience attention

Spatial layering is a cinematographic tool for directing attention and emotion.

Possible perceptual uses include:

- revealing information gradually through foreground occlusion;
- isolating a subject through distance or contrast;
- making a subject feel trapped by near foreground elements;
- establishing scale with deep background reference;
- creating intimacy by reducing perceived distance;
- creating surveillance or observational distance;
- increasing tension through partial visibility;
- preserving environmental context while keeping a subject dominant;
- using motion in one plane to redirect attention to another.

These are strategies, not formulas.

## 10. Sarah proof example

A Sarah Shot may resolve as:

```text
foreground:
  Chris shoulder, 0.45m from camera, intentionally soft

subject plane:
  Sarah, 1.4m from camera, focus on near eye

midground:
  table and story-critical prop, approximately 2.2m from camera

background:
  practical lamp and room architecture, 4-5m from camera

deep background:
  rain/window/street/buildings, beyond room boundary
```

The physical camera/lens/light setup then determines perspective, parallax, focus behaviour, occlusion, reflections, light falloff and motion relationships.

The Director may choose another arrangement. The example demonstrates the contract, not a mandatory composition.

## 11. Intentional flatness remains valid

Physics-first spatial coherence does not require maximum three-dimensional depth.

The Director may intentionally choose:

- graphic flat composition;
- telephoto spatial compression through increased camera distance;
- deep focus;
- silhouette;
- symmetrical tableau;
- animation/anime/cartoon spatial language;
- theatrical staging;
- deliberately artificial or impossible space.

Nexkosmo should distinguish intentional design from accidental renderer inconsistency.

## 12. Render/output layers

Where supported and useful, render execution should preserve separable information rather than returning only a flattened display image.

Possible output layers/passes include:

- beauty/combined image;
- alpha;
- depth/Z;
- normals;
- motion vectors;
- object IDs;
- material IDs;
- character mattes;
- environment mattes;
- effect mattes;
- Cryptomatte or equivalent ID mattes where supported;
- diffuse/direct/indirect components;
- specular/direct/indirect components;
- transmission/refraction;
- subsurface scattering;
- emission;
- volume/atmosphere;
- shadow data;
- ambient occlusion where technically/creatively useful;
- light groups / light-select passes;
- reflection/refraction components;
- renderer-specific AOVs that remain useful and traceable.

The exact required set is Shot- and route-dependent. Nexkosmo must not require meaningless passes merely because a renderer can produce them.

## 13. Production layer preservation

Nexkosmo should preserve reusable production components when doing so materially improves editability, targeted rerendering, continuity or finishing.

Examples include:

```text
environment
characters
props
lighting contributions
atmosphere
VFX/simulation
overlays/practicals
colour/finish operations
```

These production layers may map to renderer-native passes, separate renders, masks, deep data, compositing elements or hybrid outputs.

They are execution artifacts linked to canonical truth; they do not become independent competing canonical worlds.

## 14. Rich master versus delivery output

The working/master output and the final delivery file are different concepts.

Where practical, Nexkosmo should retain a high-quality intermediate/master capable of downstream finishing before creating compressed or display-targeted deliverables.

A render/output specification may include:

- resolution;
- aspect ratio;
- frame rate;
- duration/frame range;
- bit depth;
- channel layout;
- alpha mode;
- scene-linear or display-referred state;
- working colour space;
- colour primaries/gamut;
- transfer function / display transform;
- white point;
- SDR/HDR target;
- mastering/display target;
- metadata required for interpretation;
- codec/container for delivery;
- image-sequence format for master/intermediate;
- compression level;
- chroma subsampling where applicable;
- audio sync/timecode where applicable;
- filename/version/revision identifiers;
- checksum/provenance references.

Exact formats are selected according to project needs and renderer/finishing capability.

## 15. Scene-referred preservation

Where the production route supports it, physically based render output should normally preserve scene-referred or otherwise high-dynamic-range working data until the appropriate viewing/display transform is applied.

A display transform is not canonical scene illumination.

Nexkosmo should therefore preserve the distinction between:

```text
scene/light transport data
-> working colour transform
-> creative grade / look
-> display/mastering transform
-> delivery encode
```

The exact colour-management implementation may evolve, but the stages must not be silently collapsed when doing so would destroy required editability or evidence.

## 16. Colour pipeline evidence

A result must not claim exact camera or display reproduction merely because a similarly named LUT/look was applied.

Where material, evidence should record:

- source/render working space;
- transforms applied;
- renderer colour-management configuration;
- camera-response profile class where relevant;
- creative look/grade revision;
- output/display transform;
- target gamut/transfer function;
- whether operations were baked or remained non-destructive.

## 17. Baked versus non-destructive operations

Nexkosmo should explicitly distinguish operations that are baked into pixels from operations retained as editable state.

Examples include:

- lens distortion;
- chromatic aberration;
- flare/ghosting;
- depth of field;
- motion blur;
- grain;
- halation;
- bloom;
- vignette;
- colour grade;
- sharpening/softening;
- denoise;
- display transform.

There is no universal requirement that these remain unbaked. The correct choice depends on renderer physics, artistic intent, reconstruction needs and finishing workflow.

But Nexkosmo must know which choice was made.

## 18. Output Contract

Every production-quality Render Manifest should resolve a versioned Output Contract appropriate to the Shot and route.

Conceptually:

```text
Canonical Shot State
+ Continuity Snapshot
+ Physical Cinematography State
+ Spatial Layering Intent
-> Render Manifest
-> Renderer / Hybrid Route
-> Rich Render Result
-> Compositing / Finishing
-> Master Output
-> Delivery Output(s)
```

An Output Contract may specify:

```text
picture:
  resolution
  aspect ratio
  frame rate
  bit depth
  channels

colour:
  working space
  scene/display referred state
  gamut
  transfer/view transform
  mastering target

required auxiliary outputs:
  alpha
  depth
  normals
  motion vectors
  mattes/IDs
  required AOVs/light groups

preservation:
  unflattened elements required
  baked/non-baked operations
  master/intermediate format

final delivery:
  codec/container or image sequence
  SDR/HDR target
  compression/chroma requirements
```

The implementation must use typed schemas rather than relying on free-form text.

## 19. Renderer capability matching for output

A Renderer Adapter must explicitly declare which requested outputs it can produce faithfully.

Capabilities may include:

- high-bit-depth output;
- float/scene-linear output;
- alpha;
- depth;
- normals;
- motion vectors;
- object/material IDs;
- Cryptomatte/equivalent;
- light groups;
- AOV components;
- deep image data where supported;
- HDR output;
- colour-management integration;
- unbaked lens-effect support;
- separate atmosphere/volume output;
- deterministic auxiliary-pass alignment;
- frame-accurate metadata/timecode.

A renderer that cannot produce a requested auxiliary output may still be valid if that output is optional or another hybrid stage can produce it. Required output capabilities must not be silently dropped.

## 20. AI renderer output

An AI renderer may return only flattened RGB/RGBA video or images, or may provide masks/depth/motion/latent/control outputs of varying reliability.

Nexkosmo must distinguish true measured/derived render passes from AI-estimated auxiliary data.

For example:

- renderer-native physical depth from a 3D scene;
- AI-predicted depth inferred after generation;

are not equivalent evidence classes.

The same distinction applies to normals, motion, segmentation and optical effects.

## 21. Compositing and STUDIO

STUDIO should receive the richest approved result that is useful for finishing.

This may allow:

- selective colour correction;
- light-group adjustment;
- atmosphere refinement;
- character isolation;
- reflection/FX adjustment;
- depth-aware effects;
- relighting within the limits of available data;
- targeted replacement of a failed element;
- preservation of successful layers while rerendering only affected dependencies.

STUDIO does not rewrite canonical scene truth merely because a composite adjustment is possible.

## 22. Render early, flatten late

The existing Nexkosmo production principle is made explicit here:

> Render early. Flatten late.

This means Nexkosmo may create previews and intermediate images early, but should avoid prematurely destroying useful structure when that structure can materially support finishing, continuity, revision or targeted rerendering.

Flattening is appropriate when required for delivery, interoperability, performance or a deliberate creative decision.

## 23. Validation

A Render Result may be validated independently for:

- spatial-geometry fidelity;
- parallax fidelity;
- occlusion fidelity;
- focus/optical-depth fidelity;
- lighting-depth coherence;
- beauty output validity;
- alpha validity;
- depth validity;
- normals validity;
- motion-vector validity;
- matte/ID validity;
- AOV alignment;
- colour-management validity;
- master-output validity;
- delivery-output validity.

A valid beauty image does not automatically prove valid auxiliary passes, and valid auxiliary passes do not automatically prove creative approval.

## 24. Evidence and provenance

For every rich Render Result and final output, Nexkosmo should retain sufficient evidence to determine:

- canonical Scene/Shot revisions;
- Continuity Snapshot revision;
- physical cinematography specification revision;
- spatial-layering state/intent where material;
- Render Manifest and Output Contract revision;
- renderer/adapter/model/engine/version;
- generated layers/passes/AOVs;
- which requested outputs were unavailable or approximated;
- colour transforms and finishing operations;
- baked versus non-destructive operations;
- compositing graph/version where material;
- master and delivery derivation;
- validation outcomes;
- approvals and provenance.

## 25. Permanent rules

> A cinematic frame is a volume before it is a flat image.

> Spatial layering means physical/perceptual depth relationships; render layering means preserved image/production components. They are related but not interchangeable.

> Foreground, subject, midground and background are useful spatial concepts, not mandatory composition slots.

> Depth of field may reveal depth, but it does not create the underlying spatial truth.

> Parallax, occlusion, perspective, lighting and atmosphere should remain coherent with geometry where physical fidelity is claimed.

> Preserve the richest physically meaningful output for as long as practical and flatten only when delivery requires it.

> A final delivery file is not necessarily the production master.

> Required output passes and colour-management properties must be capability-matched; unsupported outputs are not silently invented.

> AI-estimated depth, normals, motion or masks must not be represented as equivalent to renderer-native physical passes unless validated to the required evidence class.

> Render early. Flatten late.

> The Director remains authoritative over whether depth, flatness, optical behaviour and final image treatment serve the intended story.