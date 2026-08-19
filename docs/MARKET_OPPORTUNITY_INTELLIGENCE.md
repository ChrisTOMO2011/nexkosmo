# Market & Opportunity Intelligence

## Status

This document defines an enduring Nexkosmo product-intelligence responsibility. It is an architectural direction and product contract, not a claim that the capability is implemented in the current increment.

## Purpose

Nexkosmo should continuously identify unmet creator needs and capability gaps from permitted public market signals while preserving evidence, uncertainty, creator agency, and human control over consequential roadmap decisions.

The system exists to answer:

> What do creators need that Nexkosmo cannot currently do, how strong is the evidence for that need, and what is the best responsible response?

## Core Principle: Visible Feedback Is Not Market Size

A public review, feature request, forum post, or comment is evidence of a need. It is not a population count.

Many creators who experience the same problem will never provide feedback. Others may leave a product, create a workaround, search for an alternative, or tolerate the friction silently. Therefore Nexkosmo MUST NOT present observed request counts as statements such as `X users want this` or otherwise treat visible feedback volume as total demand.

Raw counts MAY be retained as internal evidence when provenance and deduplication are preserved, but product decisions MUST use a broader Demand Confidence assessment.

## Permitted Signal Classes

Subject to source terms, applicable law, and platform policy, evidence may include:

- competitor reviews and public product feedback;
- public forums and communities;
- public feature-request boards;
- recurring workflow complaints and workarounds;
- search and engagement signals available through legitimate channels;
- Nexkosmo feature-page interest;
- opt-in and waitlist behaviour;
- prototype and experiment usage;
- retention and repeated use;
- willingness-to-pay evidence; and
- other legitimate behavioural evidence relevant to the underlying creator need.

Market intelligence MUST focus on aggregate product needs and opportunity signals. It MUST NOT become a system for harvesting personal contact information for unsolicited outreach.

## Semantic Need Clustering

The Brain should recognise differently worded observations that express the same underlying need.

For example, the following may belong to one `integrated_3d_creation` need cluster:

- `I wish this had a 3D modeller.`
- `Why can't I edit the mesh?`
- `I have to leave the application and use Blender.`
- `I want to make my own props inside the movie tool.`

Clustering MUST preserve links back to the original evidence. Repeated, copied, syndicated, or otherwise non-independent signals should be deduplicated or discounted. Independent evidence across different sources, competitors, time periods, and creator contexts should increase confidence more than repetition from one source.

## Demand Confidence

Demand Confidence is an evidence assessment, not a claimed percentage of the market.

It should consider, where available:

1. Explicit feedback — direct requests, complaints, and praise.
2. Recurrence — whether the same underlying need appears repeatedly.
3. Independence — whether evidence comes from independent sources and contexts.
4. Workflow friction — repeated workarounds, abandonment, switching, or unnecessary tool changes.
5. Behavioural interest — legitimate search, click, feature-page, opt-in, or waitlist signals.
6. Prototype behaviour — whether creators actually use the proposed capability.
7. Retention/value — whether the capability improves continued use or meaningful outcomes.
8. Willingness to pay — evidence that the capability creates sufficient value to support sustainable delivery.
9. Trend — whether evidence is strengthening, stable, or weakening over time.
10. Evidence quality — provenance, reliability, recency, independence, and uncertainty.

The UI SHOULD prefer qualitative or calibrated confidence states such as `Low`, `Emerging`, `Moderate`, `High`, or `Strongly Validated` unless a numerical score has a documented statistical meaning.

## Silent Demand

Nexkosmo should explicitly account for silent demand: creators may need or want a capability without publicly requesting it.

Silent demand is an inference and MUST remain labelled as uncertain. It MUST NOT be converted into an invented user count.

The Brain may infer possible silent demand from legitimate behavioural evidence such as recurring workflow friction, tool switching, abandonment, feature discovery behaviour, prototype use, or similarity to validated needs. Important inferences should be tested through real behaviour before being promoted to strong product conclusions.

## Capability Gap

When the Brain identifies a useful need that Nexkosmo cannot currently satisfy, it should create a Capability Gap candidate rather than automatically creating a feature.

A Capability Gap assessment should include:

- underlying creator need;
- source provenance and evidence summary;
- Demand Confidence and uncertainty;
- current Nexkosmo capability coverage;
- creator value and increase in human agency;
- strategic and architectural fit;
- technical feasibility;
- implementation and operational cost;
- security, privacy, rights, and governance implications;
- expected differentiation;
- dependencies and opportunity cost; and
- measurable validation criteria.

## Response Options

A Capability Gap is not synonymous with `build`.

The Brain and Steward should compare at least these responses:

- **Build** — own the capability because it is strategically important and belongs in Nexkosmo's architecture.
- **Integrate** — use an external technology while Nexkosmo owns the workflow, intelligence, policy, and user experience.
- **Partner** — obtain the capability through a strategic provider or ecosystem relationship.
- **Prototype / Research** — learn before committing to production architecture.
- **Defer** — preserve the evidence but wait for stronger timing, resources, or validation.
- **Reject** — do not pursue when evidence, fit, value, safety, or opportunity cost is inadequate.

## Lifecycle

Strong opportunities should progress through controlled gates:

`Discover -> Cluster -> Validate -> Capability Gap -> Architecture/Feasibility Study -> Steward Review -> Human Approval -> Prototype/Experiment -> Behavioural Validation -> Production Promotion`

No observed competitor request should bypass these gates merely because it is popular or frequently repeated.

## Intelligence Responsibilities

### Developmental Intelligence

Discovers signals, clusters needs, identifies capability gaps, investigates alternatives, proposes experiments, and learns from successes and failures.

### Steward Worker

Evaluates whether pursuing an opportunity is a worthwhile use of Nexkosmo's time, compute, engineering effort, capital, and attention. It considers creator value, human agency, evidence, duplication, strategic priority, cost, and expected benefit.

### Human Authority

Significant product, roadmap, spending, partnership, or market actions require explicit human approval. The system may recommend and prepare work; it does not silently redefine Nexkosmo's product direction.

### Operational Intelligence

Operational Intelligence may rely on a new capability only after that capability has passed its required validation and has been deliberately promoted into production.

## Learning Loop

Product Intelligence should update confidence from experiment outcomes and real usage.

A promising review cluster that produces weak behavioural interest should lose confidence. A need supported by independent feedback, strong prototype adoption, sustained use, and meaningful creator outcomes should gain confidence.

The system should learn from both positive and negative evidence and retain the reasoning behind confidence changes.

## Provenance and Explainability

Every material opportunity recommendation should preserve:

- original source references where permitted;
- collection time and source class;
- semantic-cluster membership;
- deduplication/independence treatment;
- evidence-quality assessment;
- inference versus observation distinction;
- confidence history;
- experiments performed;
- outcomes; and
- decision/provenance history.

The Brain should be able to explain why an opportunity was raised, what evidence supports it, what remains uncertain, and why a particular response was recommended.

## Example

A competitor review says, `I wish this software had a 3D modeller.` That is one observation.

The Brain discovers semantically related evidence across other permitted sources, including complaints about leaving filmmaking tools to edit meshes or create props. Nexkosmo does not currently satisfy the underlying need.

The correct result is not `hundreds of users want a 3D modeller`.

The correct result is a Capability Gap such as:

- Need: integrated 3D creation and editing;
- Demand Confidence: High;
- Evidence Quality: Strong;
- Independent Evidence: Multiple sources and contexts;
- Silent Demand: Plausible, uncertain;
- Nexkosmo Coverage: Incomplete;
- Strategic Fit: High;
- Recommended Response: Prototype an integrated approach and validate real creator behaviour before production commitment.

## Permanent Rule

> Never equate visible feedback with market size. Treat feedback as evidence, infer broader demand cautiously from multiple independent signals, and validate important opportunities through real behaviour.
