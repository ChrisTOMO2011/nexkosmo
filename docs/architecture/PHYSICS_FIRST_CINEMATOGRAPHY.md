# Physics-First Cinematography Contract

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD, READY, PRODUCTION, Brain, Continuity Engine, Render Orchestrator, Renderer Adapters, cinematography intelligence and future camera/lens systems  
**Related contracts:** `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`, `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`, `SHOT_COVERAGE_SUFFICIENCY.md`, `BUILD_PROGRESSIVE_DISCLOSURE_UI.md`

## 1. Purpose

Nexkosmo must not reduce cinematography to a collection of independent style labels such as `cinematic`, `35mm`, `shallow depth of field`, `dramatic lighting` or `anamorphic`.

Those labels may describe an intended result, but authentic photographic appearance emerges from a coherent physical image-forming system.

The governing rule is:

> Cinematic appearance should emerge from a coherent physical and perceptual setup wherever the production route supports it. Camera, sensor/filmback, camera-to-subject distance, lens, aperture, focus, shutter, geometry, material response, lighting, exposure and movement are interdependent causes of the image, not isolated stylistic labels.

A second permanent rule is:

> Physics creates believability. Cinematography gives that physics meaning. The renderer executes only the parts of the physical/cinematic specification it can faithfully support.

## 2. Cinematography reasoning chain

Nexkosmo should reason from meaning toward image formation rather than from style words toward a generated picture.

Conceptually:

```text
Director intent
-> desired audience perception
-> spatial/blocking design
-> camera position and height
-> sensor / filmback
-> lens / focal length / optical model
-> aperture / T-stop
-> focus distance and focus behaviour
-> shutter / motion behaviour
-> lighting geometry and source properties
-> material/light interaction
-> exposure / dynamic range / colour pipeline
-> compatible renderer or hybrid route
-> resulting image
-> perceptual / continuity / technical validation
```

The Director remains authoritative over the intended meaning and may deliberately choose stylisation or physical departure when desired.

## 3. Physical coherence before decorative style

Nexkosmo should prefer physically coherent relationships before adding decorative cinematic treatment.

Examples of coherent relationships include:

- perspective agrees with camera position;
- field of view agrees with focal length and sensor/filmback;
- depth of field agrees with focal length, aperture, focus distance, subject distance and format;
- motion blur agrees with shutter and movement;
- light direction agrees with source placement;
- shadow softness agrees with source size and distance;
- illumination falloff agrees with physical source behaviour where simulated;
- reflections and highlights agree with material roughness, geometry and light positions;
- occlusion and parallax agree with scene geometry;
- exposure and highlight/shadow behaviour agree with the chosen imaging/colour model where supported.

A visually attractive result that contradicts required physical relationships must not be labelled physically accurate merely because it looks cinematic.

## 4. Camera is a physical imaging system

A camera definition is more than a brand name.

A canonical camera profile may include, where relevant:

- camera identity/profile version;
- sensor/filmback dimensions;
- capture resolution;
- aspect ratio / active image area;
- pixel aspect where relevant;
- shutter angle or exposure time;
- ISO/exposure index when part of the simulated or measured model;
- dynamic-range model where actually known;
- colour science / input transform where actually known;
- rolling/global shutter behaviour where relevant;
- camera position and orientation;
- camera height;
- camera movement path;
- stabilisation/rig behaviour where relevant;
- lens mount / compatible lens profile references.

Camera brand names MUST NOT be treated as proof of exact sensor or colour reproduction unless Nexkosmo has an authorised, measured or otherwise validated profile sufficient to support that claim.

## 5. Lens intelligence

Nexkosmo should know what lenses do, not merely know lens names or focal-length labels.

A canonical or renderer-facing Lens Profile may include, where relevant:

- lens identity and profile version;
- prime vs zoom;
- spherical vs anamorphic;
- focal length or zoom range;
- image-circle / format coverage;
- aperture range;
- T-stop / transmission where known;
- minimum focus distance;
- focus distance;
- entrance-pupil / nodal information where required for exact spatial work;
- focus breathing;
- geometric distortion;
- field curvature;
- vignetting;
- chromatic aberration;
- longitudinal/transverse aberration where measured;
- sharpness/MTF behaviour where measured/licensed/available;
- edge softness / falloff;
- contrast behaviour;
- flare / ghosting characteristics;
- coating behaviour where known;
- bokeh shape and character;
- aperture-blade geometry where known;
- cat-eye / off-axis bokeh behaviour;
- anamorphic squeeze ratio;
- anamorphic distortion and breathing;
- oval bokeh / streak flare characteristics where applicable;
- lens shading / transmission variation;
- measured calibration evidence and provenance.

The exact implementation may support a subset initially, but unsupported properties must remain explicit rather than being silently invented.

## 6. Lens + camera coupling

Focal length must never be interpreted without the camera format when field of view matters.

For example:

```text
35mm lens + Super 35 filmback
!=
35mm lens + larger-format filmback
```

The focal length remains 35mm, but the field of view differs because the active imaging area differs.

Likewise, if the camera is moved to restore similar framing after a lens/format change, perspective changes because camera position changed.

Therefore Nexkosmo must distinguish:

- focal length;
- field of view;
- sensor/filmback;
- camera-to-subject distance;
- framing;
- perspective.

These are related but not interchangeable concepts.

The permanent rule is:

> Lens choice is evaluated together with camera format and camera position. Framing similarity does not imply perspective equivalence.

## 7. Aperture, focus and depth of field

Nexkosmo should model depth of field as a consequence of the optical setup where supported, not as an independent blur effect.

Relevant factors include:

- focal length;
- aperture / f-number or T-stop as appropriate;
- focus distance;
- subject distance;
- foreground/background distances;
- sensor/filmback / circle-of-confusion assumptions;
- lens-specific focus behaviour;
- anamorphic/specialty optical behaviour where relevant.

An AI renderer that can only imitate shallow depth of field visually must not be treated as proving physically correct optical depth of field.

## 8. T-stop versus f-stop

Where production accuracy requires it, Nexkosmo should distinguish:

- **f-stop** — geometric aperture ratio;
- **T-stop** — measured/effective light transmission.

A renderer or virtual camera may support geometric aperture while not modelling real-lens transmission losses. The adapter/profile must state the level of fidelity rather than silently equating the two.

## 9. Shutter and motion

Motion rendering should relate camera/subject movement to shutter behaviour where the route supports it.

Relevant properties include:

- shutter angle;
- exposure time;
- frame rate;
- camera velocity;
- subject velocity;
- rolling/global shutter behaviour where relevant;
- motion-vector or temporal-sampling support.

A generated smear that looks like motion blur is not automatically evidence of physically coherent shutter behaviour.

## 10. Lighting as geometry and energy, not a style word

Lighting should be represented, where supported, as sources with physical/spatial properties rather than only labels such as `moody`, `soft` or `dramatic`.

Relevant properties may include:

- source type;
- source position and orientation;
- source size / emitting area;
- intensity / exposure contribution;
- distance to subject;
- beam/spread;
- colour temperature / spectrum where supported;
- modifiers/diffusion;
- flags, negative fill and blockers;
- practical-source relationships;
- environment/sky contribution;
- bounce/reflected illumination;
- temporal lighting changes.

Human-facing intent may still use terms like `soft`, `warm`, `isolated`, `ominous` or `natural`, but Brain should translate those into the strongest physically coherent setup available for the chosen route.

## 11. Materials and light transport

Photographic authenticity depends on how light interacts with actual scene structure and materials.

Where supported, relevant behaviour includes:

- diffuse response;
- specular response;
- roughness;
- Fresnel / IOR;
- metallic response;
- transmission/refraction;
- subsurface scattering for skin and other translucent materials;
- hair/fibre response;
- volume/scattering behaviour;
- normal/displacement/microstructure;
- reflection/refraction consistency with the environment.

A renderer may approximate some of these. The capability profile determines whether the result can be treated as physical evidence or only visual approximation.

## 12. Human perception is the creative objective

Physics alone does not make a Shot cinematic.

Brain/Producer should reason about how physical choices affect human perception and story meaning.

Examples:

```text
Intent: isolate Sarah emotionally
Possible strategy:
- greater camera distance
- longer focal length / narrower field of view
- controlled background separation
- negative space
- restrained camera movement
- lighting that separates Sarah without beautifying the whole frame
```

```text
Intent: make the audience feel trapped with Sarah
Possible strategy:
- physically closer camera
- wider lens
- stronger foreground/background perspective
- constrained frame
- environmental proximity
- lighting that keeps the surrounding space perceptually present
```

These are reasoning strategies, not mandatory formulas. The Director may choose another valid visual language.

## 13. Authenticity over generic beautification

Nexkosmo should not equate cinematic quality with maximum visual polish.

Authentic cinema may intentionally include:

- restrained or imperfect composition;
- deep rather than shallow focus;
- underexposure or low-key imagery;
- practical-source motivation;
- texture/grain/noise appropriate to the capture/finish pipeline;
- lens softness or aberration;
- imperfect camera movement;
- unglamorous skin/material response;
- negative space;
- long static shots;
- deliberate optical or exposure discomfort.

Brain should optimise for the Director's intended audience experience, not for an abstract `prettiest frame` objective.

## 14. Lens profile evidence classes

Nexkosmo must distinguish three levels of lens knowledge.

### Physical lens model

A mathematically/physically modelled generic lens with known parameters.

Example:

```text
50mm spherical lens
known filmback
known aperture
known focus distance
verified distortion model
```

### Measured real-lens profile

A profile based on measured/calibrated data for a specific lens or lens family, with provenance and licensing sufficient for the intended use.

This may support real characteristics such as distortion, vignetting, transmission, breathing, flare or aberration where actually measured.

### Creative approximation

A look inspired by a lens family or optical character without sufficient calibration to claim exact reproduction.

Examples:

```text
vintage-soft approximation
warm low-contrast spherical approximation
anamorphic-style flare approximation
```

A creative approximation must not be labelled as an exact reproduction of a real commercial lens.

## 15. Camera profile evidence classes

The same distinction applies to cameras.

Nexkosmo may know:

- physical/virtual filmback geometry;
- measured or licensed camera/sensor behaviour;
- creative approximation of a camera look.

An exact filmback and field of view do not prove exact sensor colour science, dynamic range, noise, highlight roll-off or shutter behaviour.

The UI/evidence system must not overclaim fidelity.

## 16. Renderer capability interaction

The physical cinematography specification exists independently of any renderer.

A renderer adapter must state which parts it can consume faithfully.

Examples:

### Offline physically based renderer

May support:

- exact geometry;
- exact camera transform;
- filmback;
- focal length;
- aperture/focus;
- physical light sources;
- material/light transport;
- depth/motion/normal passes.

### AI image/video renderer

May support only:

- textual lens/camera descriptions;
- reference images;
- pose/depth inputs;
- camera-motion conditioning;
- limited identity controls.

If so, `50mm` may be a conditioning hint rather than a physically defined camera.

The adapter must record that distinction.

## 17. Capability-aware optical fidelity

Renderer capability profiles should independently declare support for properties such as:

- physical camera transform;
- filmback/sensor dimensions;
- focal length;
- field of view;
- aperture;
- focus distance;
- optical depth of field;
- shutter/motion blur;
- lens distortion;
- vignetting;
- chromatic aberration;
- focus breathing;
- flare/ghosting;
- anamorphic squeeze/behaviour;
- measured lens profiles;
- physical light transport;
- spectral/colour pipeline support.

A single `supportsLens=true` flag is insufficient.

## 18. Route selection

When physical cinematography fidelity is required, Render Orchestration should choose a route that can preserve the required relationships.

Possible patterns include:

```text
Canonical 3D scene + physical camera/lens/light setup
-> Arnold / V-Ray / Blender / Unreal or another capable renderer
```

or:

```text
Physical 3D camera/blocking/depth reference
+ approved identity references
-> AI appearance/motion renderer
-> validation/compositing
```

or another hybrid route.

If an AI renderer cannot consume the physical specification directly, Brain should not discard the specification. It may derive compatible references while preserving the original physical truth.

## 19. Sarah example

Sarah is a useful identity and cinematography proof case.

Canonical state may resolve:

```text
Sarah identity: approved identity package
Sarah position: 1.4m from camera
background distance: 6.0m behind Sarah
camera height: 1.25m
filmback: defined
lens: 50mm spherical
aperture: T2.8
focus: Sarah near eye
shutter: defined for frame rate/motion intent
window key: camera-left, defined size/distance/intensity
negative fill: camera-right
practical lamp: background-right
exposure intent: protect window highlights while keeping Sarah lower
```

The appearance should emerge from the coherent setup where the renderer supports it.

If another route can only approximate those controls, the preview/result must carry the appropriate approximation evidence.

## 20. Director authority and intentional stylisation

Physics-first does not mean Nexkosmo forces photorealism.

The Director may intentionally choose:

- impossible optics;
- stylised lighting;
- exaggerated perspective;
- nonphysical materials;
- animation/anime/cartoon language;
- surreal motion;
- deliberate continuity or exposure breaks.

The system should preserve the distinction between:

```text
physically coherent result
intentional stylisation
renderer limitation / accidental inconsistency
```

Intentional stylisation is valid creative truth. Renderer limitation must not masquerade as intentional style unless the Director adopts it.

## 21. BUILD interaction

BUILD should expose camera/lens controls progressively rather than as a wall of technical parameters.

A normal Director may work with meaningful choices such as:

- wider / closer;
- longer / more isolated;
- more / less background focus;
- softer / harder light;
- warmer / cooler;
- handheld / locked / moving;
- choose camera/lens preset.

Advanced users may expose:

- sensor/filmback;
- exact focal length;
- exact camera distance/transform;
- aperture/T-stop;
- focus distance;
- shutter;
- measured lens profile;
- distortion/breathing/vignetting characteristics;
- lighting measurements;
- colour pipeline.

Both interfaces edit the same canonical cinematography state.

## 22. Validation

A physically significant preview/result may be validated at separate levels such as:

- geometry/perspective valid;
- camera/filmback valid;
- focal-length/FOV valid;
- optical-depth-of-field valid;
- lighting-geometry valid;
- material/light-transport valid;
- motion/shutter valid;
- lens-character measured/valid;
- camera/sensor-look measured/valid;
- creative-approximation only.

Validation labels are evidence, not a substitute for Director judgement.

## 23. Permanent rules

> Physics first, style second: establish coherent image-forming relationships before applying decorative cinematic treatment when realism is intended.

> Camera position determines perspective. Lens and filmback determine field of view. Framing alone does not define the optical experience.

> Nexkosmo knows lens behaviour, not just lens names.

> A lens profile may be physical, measured or creatively approximated; Nexkosmo must not confuse those evidence levels.

> Depth of field, motion blur, lighting, reflections and material response should arise from their physical causes whenever the selected renderer supports them.

> AI imitation of a lens or camera look is not automatically equivalent to a physically defined camera/lens system.

> Renderer limitations never erase the canonical physical cinematography specification.

> The Director decides what the audience should experience. Physics makes the chosen world believable; cinematography turns that physical truth into meaning.