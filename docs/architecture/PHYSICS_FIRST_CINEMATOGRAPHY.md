# Physics-First Cinematography Contract

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD, READY, PRODUCTION, Brain, Continuity Engine, Render Orchestrator, Renderer Adapters, cinematography intelligence and future camera/lens systems  
**Related contracts:** `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`, `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`, `SHOT_COVERAGE_SUFFICIENCY.md`, `BUILD_PROGRESSIVE_DISCLOSURE_UI.md`, `CINEMATIC_SPATIAL_LAYERING_AND_RENDER_OUTPUT.md`

## 1. Purpose

Nexkosmo must not reduce cinematography to a collection of independent style labels such as `cinematic`, `35mm`, `shallow depth of field`, `dramatic lighting` or `anamorphic`.

Those labels may describe an intended result, but authentic photographic appearance emerges from a coherent physical image-forming system.

The governing rule is:

> Cinematic appearance should emerge from a coherent physical and perceptual setup wherever the production route supports it. Camera, camera-support/movement rig, sensor/filmback, camera-to-subject distance, lens, aperture, focus, shutter, geometry, material response, lighting, exposure and movement are interdependent causes of the image, not isolated stylistic labels.

A second permanent rule is:

> Physics creates believability. Cinematography gives that physics meaning. The renderer executes only the parts of the physical/cinematic specification it can faithfully support.

## 2. Cinematography reasoning chain

Nexkosmo should reason from meaning toward image formation rather than from style words toward a generated picture.

Conceptually:

```text
Director intent
-> desired audience perception
-> spatial/blocking design
-> camera support / movement rig
-> camera path / pivot / constraints / stabilisation
-> camera position and height
-> sensor / filmback
-> lens / focal length / optical model
-> optical filtration
-> aperture / T-stop
-> focus distance and focus behaviour
-> shutter / motion behaviour
-> white balance / tint / camera interpretation
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
- camera movement agrees with the selected support/rig where that rig materially defines the Shot;
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
- white balance;
- tint / green-magenta compensation where relevant;
- dynamic-range model where actually known;
- highlight response / roll-off where actually measured or validated;
- black-level / shadow response where actually measured or validated;
- sensor-noise behaviour where actually measured or validated;
- spectral sensitivity / colour-filter-array response where actually known;
- colour science / input transform where actually known;
- rolling/global shutter behaviour where relevant;
- rolling-shutter readout time / scan behaviour where actually known;
- camera position and orientation;
- camera height;
- camera movement path;
- camera support / movement-rig reference;
- stabilisation/rig behaviour where relevant;
- lens mount / compatible lens profile references.

Camera brand names MUST NOT be treated as proof of exact sensor or colour reproduction unless Nexkosmo has an authorised, measured or otherwise validated profile sufficient to support that claim.

### 4.1 Camera interpretation is part of image formation

The colour temperature of a light source and the camera's white-balance setting are different variables.

For example, a 3200K source viewed with a 3200K white balance is not interpreted the same way as the same source viewed with a 5600K white balance.

Where the route supports it, Nexkosmo should therefore preserve both:

```text
scene/source spectrum or colour temperature
+
camera white balance / tint / response
-> recorded colour relationship
```

A generic `warm` or `cool` label is not a substitute for this relationship when physical or camera-response fidelity is required.

### 4.2 Camera Support & Movement Rig State

Nexkosmo should represent how the camera is physically supported or moved as part of the Shot's cinematography state when that support materially affects movement, perspective, parallax, framing or audience perception.

A Camera Support / Movement Rig State may classify the platform as one or more of:

- locked/static camera;
- tripod / fluid head;
- monopod where useful;
- slider;
- dolly / track dolly;
- doorway dolly or floor dolly;
- pedestal / studio pedestal;
- jib;
- fixed-arm crane;
- telescopic crane / Technocrane-style system;
- handheld;
- shoulder rig;
- body-mounted stabilised rig / Steadicam-type system;
- motorized gimbal / stabiliser;
- drone / aerial platform;
- vehicle mount / process rig;
- cable cam;
- motion-control / robotic arm;
- body / head / chest / POV mount;
- remote head;
- virtual camera rig;
- another declared future support system.

The class name alone is not sufficient. Where relevant, the state should preserve physical or kinematic properties such as:

- camera-to-rig mount offset;
- pivot position;
- boom/arm length;
- telescoping range;
- rail/track/path geometry;
- constrained movement axes;
- pan range and speed;
- tilt range and speed;
- roll/bank behaviour;
- camera height range;
- altitude range for aerial systems;
- path start/end and intermediate key positions;
- velocity;
- acceleration/deceleration;
- easing;
- maximum speed / acceleration constraints where materially relevant;
- damping / inertia;
- stabilisation strength / response;
- operator-induced micro-motion where intentionally modelled;
- horizon-lock behaviour;
- target-tracking behaviour;
- repeatability / motion-control precision;
- parent platform motion such as a car, boat, actor or aircraft;
- environmental influence such as wind where intentionally modelled;
- collision/clearance constraints where the virtual/physical route supports them.

The permanent rule is:

> `Tripod`, `dolly`, `jib`, `crane`, `handheld`, `Steadicam`, `gimbal`, `drone` and similar terms are movement semantics, not decorative labels, when they materially define the Shot.

### 4.3 Support type changes the motion signature

Different support systems may reach similar start and end camera positions while producing different motion between them.

Examples:

```text
Tripod pan:
  position remains fixed
  orientation changes around the head/pivot

Dolly:
  camera translates through space
  perspective/parallax change continuously

Jib/crane:
  camera follows an arc or articulated/telescoping path
  height and distance may change together

Steadicam/body-stabilised rig:
  free operator translation
  stabilised but not perfectly inertial orientation
  human movement remains part of the motion signature

Motorized gimbal:
  free translation from operator/platform
  electronically stabilised orientation
  response/smoothing may differ from body-stabilised rigs

Handheld/shoulder:
  operator-driven translation and rotation
  deliberate or natural micro-motion, sway and acceleration

Drone:
  six-degree-of-freedom aerial translation/orientation
  altitude, yaw, bank, acceleration, wind/stabilisation behaviour may matter

Motion control/robot arm:
  repeatable programmed trajectory
  high path/pivot precision where supported
```

Nexkosmo must not assume these are equivalent simply because a generic transform curve can approximate their visible path.

### 4.4 Movement intent and rig choice

The Director may specify the movement directly (`slow push toward Sarah`) without naming a rig. Brain/Producer may then propose a compatible support system according to the required movement character, physical constraints and production route.

Conversely, the Director may explicitly request `tripod`, `jib`, `drone`, `Steadicam`, `gimbal`, `handheld`, `dolly` or another support class. In that case the support semantics become part of the Shot unless the Director changes them.

Examples of perceptual intent include:

- locked tripod for stillness, observation or tension;
- slow dolly for controlled spatial approach/withdrawal;
- jib/crane for vertical revelation or spatial expansion;
- Steadicam/gimbal for fluid movement through a space;
- handheld for embodied instability or immediacy;
- drone for scale, geography, height or continuous aerial movement;
- motion-control for exact repeatability or compositing/VFX requirements.

These associations are suggestions, not fixed artistic rules.

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

### 5.1 Optical filtration stack

Nexkosmo should represent physical filtration placed in the capture path separately from post-production look effects.

A filtration stack may include, where relevant:

- neutral-density filtration;
- variable ND where actually used/supported;
- infrared/IRND filtration;
- polariser and polariser orientation where meaningful;
- diffusion filters;
- mist/softening filters;
- diopters / close-focus optical attachments;
- colour-compensation or colour-effect filters;
- graduated filters;
- specialty optical filters;
- filter order when materially significant;
- measured transmission or colour shift where known.

A physical diffusion filter that changes light before image capture is not automatically equivalent to adding a diffusion effect after rendering.

The system must record whether the intended effect is:

```text
physical optical filtration
measured filter profile
creative approximation
post-production effect
```

and must not silently treat those evidence classes as interchangeable.

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

### 7.1 Focus is dynamic in footage

For moving footage, focus may be a time-varying camera parameter rather than one fixed distance.

A Focus Trajectory may include:

- focus target identity where applicable;
- start focus distance;
- end focus distance;
- intermediate key focus distances;
- start/end times or frames;
- rack-focus timing;
- interpolation/easing curve;
- focus-pull speed;
- overshoot/settle behaviour where intentionally modelled;
- whether focus follows a moving subject automatically or a defined pull path;
- lens breathing response during the pull where supported.

A renderer that can imitate a rack focus without preserving the required focus-distance/lens relationship must be labelled as an approximation for optical-fidelity purposes.

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
- support-rig motion signature;
- rolling/global shutter behaviour where relevant;
- rolling-shutter readout time where relevant;
- motion-vector or temporal-sampling support.

A generated smear that looks like motion blur is not automatically evidence of physically coherent shutter behaviour.

### 9.1 Time-varying lens and exposure state

Footage may intentionally change optical or exposure parameters during a Shot.

Where relevant, Nexkosmo should support versioned/time-keyed trajectories for:

- focal length / zoom position;
- focus distance;
- aperture / iris / T-stop;
- shutter angle or exposure time;
- ISO/EI when intentionally changed;
- ND/filter state when physically or virtually variable;
- white balance/tint when intentionally changed;
- camera-response mode where a route supports such changes.

A zoom is not merely a change in crop. A focus pull is not merely a blur transition. An iris ramp is not merely a brightness keyframe. Where physical fidelity is claimed, the renderer must honour the corresponding optical/exposure relationship.

Nexkosmo should preserve temporal continuity of exposure and colour through camera motion, subject motion, focus pulls, zooms and lighting changes unless the Director intentionally changes that continuity.

### 9.2 Camera movement is a trajectory with physical character

Where camera-motion fidelity matters, Nexkosmo should preserve more than position keyframes.

A Camera Movement Trajectory may include:

- support/rig reference;
- camera transform over time;
- parent-platform transform where applicable;
- pivot/arm/rail constraints;
- velocity profile;
- acceleration/deceleration profile;
- easing;
- pan/tilt/roll behaviour;
- stabilisation response;
- damping/inertia;
- intentional micro-motion;
- horizon behaviour;
- tracking/look-at target where used;
- spatial clearance/collision constraints where supported;
- repeatability tolerance where motion-control fidelity is required.

The same path rendered with different motion signatures may create a different audience experience and different physical relationships with parallax and motion blur.

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

### 10.1 Calibrated light measurement

Where the route supports calibrated lighting, Nexkosmo should preserve the measurement type and unit rather than storing an unexplained arbitrary intensity value.

Possible measurements may include, where applicable:

- lux / illuminance;
- lumens / luminous flux;
- candela / luminous intensity;
- nits / cd/m2 for emissive luminance;
- exposure values or meter readings;
- renderer-native physical power/radiometric units;
- spectral power data where available and useful.

Different renderer engines use different conventions. The Renderer Adapter must declare how canonical lighting measurements map into renderer-specific controls and whether that mapping is physically calibrated, constrained or approximate.

### 10.2 Exposure is a coupled physical relationship

Nexkosmo should not treat exposure as a standalone brightness slider when physical capture fidelity is required.

Conceptually:

```text
scene illumination / emitted radiance
+ material response
+ lens transmission / T-stop
+ optical filtration
+ shutter / exposure time
+ ISO / exposure index
+ sensor / camera response
+ white balance / colour interpretation
-> recorded exposure and colour response
```

This is a conceptual relationship, not a claim that one universal equation fully reproduces every real camera.

The important architectural rule is that changing one term may change the resulting image and must not be silently compensated by another term unless the Director or an authorised automatic-exposure rule intends that compensation.

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

```text
Intent: reveal scale around Sarah
Possible strategy:
- crane/jib/drone or another justified elevated movement route
- movement that changes height and spatial relationship rather than merely zooming out
- maintain coherent parallax and horizon behaviour
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

The same distinction applies to cameras and movement rigs.

Nexkosmo may know:

- physical/virtual filmback geometry;
- measured or licensed camera/sensor behaviour;
- physically/kinematically defined movement-rig behaviour;
- measured/calibrated movement-rig behaviour where available;
- creative approximation of a camera or movement look.

An exact filmback and field of view do not prove exact sensor colour science, dynamic range, noise, highlight roll-off, spectral sensitivity, white-balance behaviour or shutter/readout behaviour.

Likewise, a path that visually resembles a drone, Steadicam, jib or handheld Shot does not prove the corresponding movement-rig physics were preserved.

The UI/evidence system must not overclaim fidelity.

## 16. Renderer capability interaction

The physical cinematography specification exists independently of any renderer.

A renderer adapter must state which parts it can consume faithfully.

Examples:

### Offline physically based / 3D renderer

May support:

- exact geometry;
- exact camera transform;
- camera rig hierarchy/constraints;
- filmback;
- focal length;
- aperture/focus;
- physical light sources;
- material/light transport;
- depth/motion/normal passes.

### AI image/video renderer

May support only:

- textual lens/camera/rig descriptions;
- reference images;
- pose/depth inputs;
- camera-motion conditioning;
- limited identity controls.

If so, `50mm`, `drone shot`, `jib shot` or `Steadicam` may be conditioning hints rather than physically defined camera and rig states.

The adapter must record that distinction.

## 17. Capability-aware optical and movement fidelity

Renderer capability profiles should independently declare support for properties such as:

- physical camera transform;
- camera support / movement-rig semantics;
- rig pivot/arm/rail constraints;
- parent-platform motion;
- path/velocity/acceleration controls;
- stabilisation/damping/inertia controls;
- repeatable motion-control trajectories;
- handheld/operator micro-motion controls where relevant;
- aerial/drone altitude, banking, yaw and stabilisation controls where relevant;
- filmback/sensor dimensions;
- focal length;
- field of view;
- aperture;
- focus distance;
- focus trajectory / rack-focus control;
- optical depth of field;
- zoom trajectory / time-varying focal length;
- iris/aperture trajectory;
- shutter/motion blur;
- rolling-shutter/readout behaviour;
- white balance / tint controls;
- sensor/camera-response modelling;
- calibrated exposure / ISO-EI behaviour;
- optical filtration stack;
- measured filter profiles where available;
- lens distortion;
- vignetting;
- chromatic aberration;
- focus breathing, including during focus pulls;
- flare/ghosting;
- anamorphic squeeze/behaviour;
- measured lens profiles;
- calibrated/typed light units;
- physical light transport;
- temporal exposure/colour continuity;
- spectral/colour pipeline support.

A single `supportsLens=true`, `supportsCamera=true`, `supportsCameraMovement=true` or `supportsLighting=true` flag is insufficient.

## 18. Route selection

When physical cinematography fidelity is required, Render Orchestration should choose a route that can preserve the required relationships.

Possible patterns include:

```text
Canonical 3D scene + physical camera/lens/light setup + movement-rig state
-> Arnold / V-Ray / Blender / Unreal or another capable renderer
```

or:

```text
Physical 3D camera/blocking/depth/movement reference
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
camera support: tripod locked, slow pan only
camera height: 1.25m
filmback: defined
lens: 50mm spherical
aperture: T2.8
focus: Sarah near eye
focus trajectory: static unless a rack focus is intended
shutter: defined for frame rate/motion intent
ISO/EI: defined where the camera model uses it
white balance/tint: defined
filter stack: defined or none
window key: camera-left, defined size/distance/intensity/unit where supported
negative fill: camera-right
practical lamp: background-right
exposure intent: protect window highlights while keeping Sarah lower
```

If the Director changes the support to a slow jib rise, dolly push, handheld move, gimbal follow or drone move, Nexkosmo should preserve that support-specific movement state rather than merely attaching a new text label.

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
- surreal movement or impossible camera rigs;
- deliberate continuity or exposure breaks.

The system should preserve the distinction between:

```text
physically coherent result
intentional stylisation
renderer limitation / accidental inconsistency
```

Intentional stylisation is valid creative truth. Renderer limitation must not masquerade as intentional style unless the Director adopts it.

## 21. BUILD interaction

BUILD should expose camera/lens/rig controls progressively rather than as a wall of technical parameters.

A normal Director may work with meaningful choices such as:

- locked tripod;
- pan / tilt;
- dolly in / dolly out;
- jib/crane rise or descend;
- handheld;
- Steadicam / stabilised walk;
- gimbal follow;
- drone move;
- wider / closer;
- longer / more isolated;
- more / less background focus;
- rack focus from A to B;
- zoom in / zoom out;
- brighter / darker exposure intent;
- softer / harder light;
- warmer / cooler camera interpretation;
- choose camera/lens/filter/rig preset.

Advanced users may expose:

- camera support/rig class;
- pivot/mount/arm/rail geometry;
- path and transform trajectory;
- velocity/acceleration/easing;
- stabilisation/damping/inertia;
- operator micro-motion;
- horizon/target-tracking behaviour;
- sensor/filmback;
- exact focal length;
- exact camera distance/transform;
- aperture/T-stop;
- focus distance and focus trajectory;
- zoom/focal-length trajectory;
- iris/aperture trajectory;
- shutter;
- ISO/EI;
- white balance/tint;
- optical filter stack;
- measured lens/filter profile;
- distortion/breathing/vignetting characteristics;
- calibrated lighting measurements;
- sensor/camera-response profile;
- colour pipeline.

Both interfaces edit the same canonical cinematography state.

## 22. Validation

A physically significant preview/result may be validated at separate levels such as:

- geometry/perspective valid;
- camera/filmback valid;
- camera-support/movement-rig valid;
- path/pivot/constraint valid;
- movement-velocity/acceleration valid;
- stabilisation/motion-character valid;
- focal-length/FOV valid;
- optical-depth-of-field valid;
- focus-trajectory valid;
- zoom-trajectory valid;
- iris/exposure-trajectory valid;
- optical-filtration valid;
- white-balance/camera-interpretation valid;
- calibrated-lighting valid;
- lighting-geometry valid;
- material/light-transport valid;
- motion/shutter valid;
- rolling-shutter/readout valid;
- temporal exposure/colour-continuity valid;
- lens-character measured/valid;
- camera/sensor-look measured/valid;
- creative-approximation only.

Validation labels are evidence, not a substitute for Director judgement.

## 23. Permanent rules

> Physics first, style second: establish coherent image-forming relationships before applying decorative cinematic treatment when realism is intended.

> Camera position determines perspective. Lens and filmback determine field of view. Framing alone does not define the optical experience.

> Camera-support and movement-rig choice can determine the physical path, pivot, constraints, stabilisation and motion character of a Shot; it is part of cinematography when material.

> `Tripod`, `dolly`, `jib`, `crane`, `handheld`, `Steadicam`, `gimbal`, `drone`, `vehicle mount` and similar support terms are movement semantics, not decorative labels.

> Nexkosmo knows lens behaviour, not just lens names.

> A lens profile may be physical, measured or creatively approximated; Nexkosmo must not confuse those evidence levels.

> White balance, tint, filtration, focus, zoom, iris, shutter, lighting and sensor response are part of the image-forming system when they materially affect the intended Shot.

> Exposure is a coupled relationship between the scene, lens/filter transmission, shutter, aperture/T-stop, ISO/EI, sensor/camera response and colour interpretation; it is not merely a brightness label.

> Time-varying camera movement, focus, zoom, iris and exposure state must remain physically/temporally coherent where the selected route claims that fidelity.

> Physical filtration and post-production look effects are distinct evidence classes unless validated as equivalent for the intended purpose.

> Depth of field, motion blur, lighting, reflections and material response should arise from their physical causes whenever the selected renderer supports them.

> AI imitation of a lens, camera or camera-rig look is not automatically equivalent to a physically defined camera/lens/movement system.

> Renderer limitations never erase the canonical physical cinematography specification.

> The Director decides what the audience should experience. Physics makes the chosen world believable; cinematography turns that physical truth into meaning.