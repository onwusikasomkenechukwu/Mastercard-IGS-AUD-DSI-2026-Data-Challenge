# FINALE PITCH SCRIPT — Path B / CAN Edition
**Team Data Benders | Mastercard IGS & AUC DSI Data Challenge**
**Atlanta Finale, April 30 – May 2, 2026**

---

## Speaker Assignments

- **Speaker A (Somkenechukwu):** Slides 1, 2, 5 — opens, owns problem framing, owns analytical findings
- **Speaker B (Oritsejemiyotan):** Slides 3, 4, 7 — owns community context, IGS benchmarking, **the CAN headline slide**
- **Speaker C (Moyinoluwa):** Slides 6, 8, 9, 10 — owns access logic, deployment, measurement, close

Speaker B carries the platform reveal on slide 7. That's the moment that wins or loses you the room. The most rehearsal-intensive slide in the pitch.

---

## Word-for-Word Script

### Slide 1 — Title (Speaker A) — 0:30

> "Healthy Economies, Healthy Communities. Team Data Benders, Howard University.
>
> The Mastercard challenge asks how economic conditions in IGS-below-45 communities affect healthcare access — and how small businesses can help. We picked East of the River DC, 46 census tracts where the Inclusive Growth Score median is 38, eighteen points below the rest of the city.
>
> Our thesis is direct. Healthcare access in EOTR is not just a map problem. Economic conditions block access — and small businesses are how communities create the services they're missing. But that only works if residents can start them and stakeholders can find them.
>
> We're proposing CAN — Community Action Network — a platform that connects both sides."

**Hand-off:** *"Let me show you what we mean by economic friction."*

---

### Slide 2 — Objective and Problem Statement (Speaker A) — 0:45

> "We started with a question: if the care exists, why isn't it being used?
>
> [point at the food insecurity bars]
>
> The 10 highest-food-insecurity tracts in EOTR average 48 percent food insecurity. The 10 lowest average 22 percent.
>
> [point at the proximity bars]
>
> Now look at medical-care proximity in those same tracts. The high-need tracts score 0.57 — closer to care. The low-need tracts score 0.31 — farther from it.
>
> [pause]
>
> The sickest neighborhoods are physically *closer* to healthcare. We tested this 18 different ways across USDA, DC Built Environment, and CDC data. 14 of 18 tests point the wrong way for any policy built on physical distance.
>
> [point at problem statement card]
>
> The real barrier is economic friction, not geographic distance. The intervention has to be economic. And small businesses are how communities create the services they lack."

**Hand-off (to Speaker B):** *"Let me hand it over to my teammate to walk you through the community."*

---

### Slide 3 — Community Overview (Speaker B) — 0:35

> "Our community is 46 EOTR tracts.
>
> [point at the histogram]
>
> The bars show the 2025 IGS distribution across all DC tracts. EOTR — in red — concentrates in the 25-to-44 score band, while the rest of DC clusters at 45 and above. This is not a statistical outlier. It's a structural corridor.
>
> [point at the right cards]
>
> 46 tracts in the community pool. 16,281 residents inside our top five Phase-1 deployment markets. Average food insecurity in those five is 46.2 percent.
>
> The tracts the IGS told us to look at are exactly the tracts where every economic and health indicator we tested confirmed disadvantage."

**Hand-off:** *"That's why this community clears the challenge threshold by a wide margin."*

---

### Slide 4 — IGS Benchmarking (Speaker B) — 0:40

> "Every analyzed EOTR tract sits below the challenge threshold of 45. Median IGS is 38, versus 56 in the rest of DC. The Economy pillar median is 33 — the weakest of the three pillars in our community.
>
> [point at the map]
>
> Within that 46-tract pool, we identify five Phase-1 deployment markets using a Need-by-Readiness ranking — those are the colored points on the map. 96.02 in the north. 78.08, 75.03, 74.08, 74.03 in the central corridor.
>
> [point at the interpretation panel]
>
> Challenge eligibility is established at the tract pool. Deployment markets are then selected from that low-IGS pool based on need and readiness. The analytical work behind that selection is what differentiates this from a 'pilot somewhere in EOTR' proposal."

**Hand-off (to Speaker A):** *"And here's what the model finds when we look at what actually predicts the outcomes."*

---

### Slide 5 — Key Findings (Speaker A) — 0:55

> "We moved from the 46-tract intuition to a full DC sample — 205 tracts, five-fold cross-validation, bootstrap stability across 1000 resamples.
>
> [point at the four cards]
>
> Cross-validated R-squared on food insecurity is 0.69. Held-out test is 0.61. We bootstrapped the model 1000 times to make sure the signals are stable, not noise from one fit.
>
> [point at the bar chart]
>
> The five features that survive that stability test are: labor market engagement, retained 100 percent of the time. Small business loans, 99.7. Travel time to work. Internet access. Affordable housing.
>
> [pause]
>
> Notice what's *not* on that list: distance to clinics, distance to food, supply of medical facilities. The stable predictors are inclusive-growth conditions. They're economic.
>
> [point at the bottom-right callout]
>
> What this means for the intervention: the predictors are economic. The response has to address small-business formation and local opportunity, not just service delivery. So we built that response."

**Hand-off (to Speaker C):** *"My teammate will show you why nearby care still goes unused — and how that points directly at the platform."*

---

### Slide 6 — Healthcare Access Context (Speaker C) — 0:40

> "Why does nearby care still go unused? We map this against the three IGS pillars the challenge framework uses.
>
> [point at the three cards in sequence]
>
> Place: care is geographically nearby, but commute and visit time still block use. Pilot response — show residents which gaps exist in their neighborhood through a Community Pulse dashboard.
>
> Economy: labor-market weakness and low small-business financing are stable predictors of food insecurity. Pilot response — let residents start businesses to fill those gaps with AI-powered planning support.
>
> Community: trust, digital access, and repeat use shape whether services are actually used. Pilot response — connect residents to stakeholders who fund, hire, and mentor from the same platform.
>
> [point at the bottom callout]
>
> The challenge prompt asks how economic conditions affect healthcare access. Our one-sentence answer: in low-IGS EOTR communities, economic conditions affect healthcare access by making routine care too costly in time, coordination, and reliability to use consistently. The response has to fix the economy, and the way you fix the economy in low-IGS tracts is by helping residents build it themselves."

**Hand-off (to Speaker B):** *"And that's exactly what CAN does. My teammate will walk you through the platform."*

---

### Slide 7 — CAN: Community Action Network (Speaker B) — 1:10

> [pause briefly. Look up. Slow down. This is the moment.]
>
> "This is CAN. Community Action Network. A two-sided platform that turns the data we've shown you into local opportunity.
>
> [point at Community Pulse screenshot]
>
> On one side: residents. They open the platform and see their community's IGS, their Community Health Score, their Commercial Diversity Score. The platform shows the top opportunity gaps in their neighborhood — childcare, fresh food, home repair — surfaced from the same data we've been analyzing.
>
> [point at Opportunity Map screenshot]
>
> When a resident sees a gap, they can act on it. The Opportunity Map turns gaps into business opportunities — fresh food access becomes 'start a fresh-food business,' childcare gaps become 'start a childcare business.' AI-powered planning support converts an idea into a 30-60-90 plan, funding options, and a license checklist.
>
> [point at Stakeholder Dashboard screenshot]
>
> On the other side: stakeholders. Funders, employers, CDFIs, nonprofits, city agencies. They see businesses tagged by community need, filter by funding amount or readiness score, and choose where to fund, hire, or mentor.
>
> [point at Two-sided platform entry screenshot]
>
> Residents enter to build. Stakeholders enter to support. Both sides see impact through the same Mastercard-anchored data layer.
>
> [point at Impact Dashboard screenshot]
>
> And impact is tracked: businesses supported, funding connected, jobs created, families served. The same IGS framework that identified the gaps tells us whether CAN closed them.
>
> [point at the bottom line]
>
> Community data, opportunity gap, resident starts business, stakeholder funds, IGS-tracked impact. That's the loop. Mastercard makes every step of it possible."

**Hand-off (to Speaker C):** *"Here's how CAN actually deploys."*

---

### Slide 8 — Implementation Considerations (Speaker C) — 0:50

> "This is a platform pilot, not a concept.
>
> [point through the four cards in sequence]
>
> Phase 1 footprint: five named EOTR launch tracts. About 16,281 residents in the initial focus set. Community onboarding through Howard, faith institutions, FQHC outreach, and local partners.
>
> Mastercard layer: IGS feeds the Community Pulse. Payment rails route stakeholder funding to resident-owned businesses. The merchant and partner network accelerates community and stakeholder onboarding.
>
> Cost: $500K covers platform development, AI infrastructure, community onboarding, stakeholder partnerships, and 18 months of measured operations across the five launch tracts.
>
> [point at stop/pivot rules]
>
> Stop or pivot rules: if resident sign-ups stay below 200 in Phase 1, if stakeholders engage with fewer than 25 percent of visible business profiles, or if AI planning output is rated unhelpful by a majority of users — we shut it down. A platform that learns cheaply is worth more than one that pretends to scale."

**Hand-off:** *"Here's how we measure it."*

---

### Slide 9 — Metrics for Success (Speaker C) — 0:40

> "Three measurement lanes, each mapped to an IGS pillar.
>
> [point in sequence]
>
> Access slash Place: residents reached by Community Pulse. Checkpoint: opportunity gaps surfaced and acted on in each pilot tract. Signals: dashboard usage, opportunity clicks, return visits.
>
> Economic slash Economy: businesses launched. $445K in stakeholder funding connected. 89 jobs created. Signals: commercial diversity score improvement and businesses moving from planning to launch.
>
> Community: directional movement in IGS-aligned indicators. Signals: top community needs trending downward, follow-through on stakeholder support, stronger local hiring loops.
>
> [point at bottom callout]
>
> What counts as success by month 12: the same framework that identified the gaps shows whether CAN closed them. Resident usage, business formation, stakeholder engagement, and community indicators all need to move together."

**Hand-off:** *"Which brings us to the close."*

---

### Slide 10 — Conclusion, Ask, and Acknowledgements (Speaker C) — 0:50

> "We're asking for $500K. 18 months. Five named EOTR launch tracts. CAN as the platform deliverable.
>
> [point at the two callout boxes]
>
> Our revised core thesis: healthcare access in EOTR is downstream of economic conditions. CAN turns IGS data into local opportunity by helping residents start the businesses their communities need — and helping stakeholders find them. Small businesses aren't a peripheral retail layer. They are the mechanism.
>
> The $500K covers platform development, AI infrastructure, community deployment in five launch tracts, stakeholder onboarding, and 18 months of measured operations.
>
> [pause, look up at the room, slow down]
>
> Same city. One river apart. In DC, life expectancy still varies by roughly 20 years across neighborhoods. That is an inclusive-growth failure.
>
> The data, the partners, and the payment infrastructure exist. The question is whether we can turn them into a measurable access model.
>
> CAN is that model. Thank you."

---

## Timing Budget

| Slide | Speaker | Target | Cumulative |
|---|---|---|---|
| 1. Title | A | 0:30 | 0:30 |
| 2. Objective / Problem | A | 0:45 | 1:15 |
| 3. Community Overview | B | 0:35 | 1:50 |
| 4. IGS Benchmarking | B | 0:40 | 2:30 |
| 5. Key Findings | A | 0:55 | 3:25 |
| 6. Healthcare Access Context | C | 0:40 | 4:05 |
| 7. **CAN platform reveal** | B | 1:10 | 5:15 |
| 8. Implementation | C | 0:50 | 6:05 |
| 9. Metrics for Success | C | 0:40 | 6:45 |
| 10. Conclusion / Ask | C | 0:50 | 7:35 |
| **Total speaking** | | **7:35** | |

**Speaker time totals:**
- Speaker A: 2:10 (slides 1, 2, 5)
- Speaker B: 2:25 (slides 3, 4, 7)
- Speaker C: 3:00 (slides 6, 8, 9, 10)

If your slot is 7 minutes flat: cut Slide 7 to 0:55 by trimming the Stakeholder Dashboard description, and trim Slide 8 to 0:40. If your slot is 8 minutes: you have 25 seconds of buffer for natural pauses, which is the right amount.

**Slide 7 is the longest single slide in the pitch — 1:10.** That's intentional. The platform reveal needs space to breathe. Don't rush it. If you're under time pressure, trim somewhere else.

---

## Hand-off Discipline

Hand-offs are scripted into the dialogue. Practice them as part of the script, not as afterthoughts.

The five hand-offs:
1. Speaker A → Speaker B: "Let me hand it over to my teammate to walk you through the community."
2. Speaker B → Speaker A: "And here's what the model finds when we look at what actually predicts the outcomes."
3. Speaker A → Speaker C: "My teammate will show you why nearby care still goes unused — and how that points directly at the platform."
4. Speaker C → Speaker B: "And that's exactly what CAN does. My teammate will walk you through the platform."
5. Speaker B → Speaker C: "Here's how CAN actually deploys."

The fourth hand-off — Speaker C → Speaker B for the platform reveal — is the most important. Practice it specifically. You're handing the most critical slide to the speaker who built the case for it. The transition has to sound coordinated, not random.

---

## Q&A — Prioritized

The platform pivot changes which questions are most likely. Drill these eight first.

### Methodology questions (Speaker A owns)

**Q1: "Your R² is 0.69. How predictive is this really?"**
> "0.69 is moderate, and we report it honestly. But the predictive ceiling on tract-level food insecurity is bounded — BRFSS PLACES estimates have substantial unexplained variation by construction. What matters more is which features survive bootstrap stability across 1000 resamples. Five features retain above 90 percent. That's the signal we'd act on, not the raw R²."

**Q2: "Are you claiming small-business formation causes health outcomes?"**
> "We're not claiming causation. The model shows that small-business density and small-business financing carry independent predictive power for food insecurity *after* controlling for income, housing, and infrastructure. That's correlational, and we say so. What it earns is the right to test the mechanism in a tract-level pilot with shutdown criteria — which is what CAN is designed to do."

### Platform questions (Speaker B owns)

**Q3: "How does the AI Business Builder actually work?"**
> "The AI uses a structured pipeline. The resident describes their business idea in plain language. We pass that through an LLM with a structured prompt that pulls in the IGS data for their tract — the gaps, the demographics, the existing business mix. The output is a structured plan with five sections: business summary, why it fits the community, startup checklist, funding options, and a 30-60-90 plan. We use Anthropic's Claude API for the inference. We've tested it against multiple sample business ideas and validated the output structure."

**Q4: "How is CAN different from existing platforms like Hello Alice, SCORE, or Black Wall Street?"**
> "Three differences. First, those tools are general-purpose business resources. CAN is grounded in tract-level IGS data, so the recommendations are calibrated to actual community gaps, not generic templates. Second, those are one-sided — resident-only. CAN is two-sided: stakeholders see what businesses residents are starting, in real time, tagged by community need. Third, the impact is measurable through Mastercard's existing IGS infrastructure, not self-reported."

**Q5: "Is this a real prototype or just mockups?"**
> "The Figma Make build is a working prototype. The five screens you saw are interactive. The metrics displayed on those screens are pilot targets — we disclose that on the slide. Production-grade development of the AI inference layer, the payment routing, and the impact-tracking integrations is what the $500K funds."

### Implementation questions (Speaker C owns)

**Q6: "Couldn't a stakeholder fund predatory or extractive businesses through this platform?"**
> "Real risk. Three safeguards. First, the readiness score requires a complete plan and license checklist before a business is visible to stakeholders. Second, businesses are tagged by community need addressed, not by founder demographics — so stakeholder filtering is on community impact, not identity. Third, we collect resident feedback on business behavior post-funding, and businesses lose visibility if community sentiment turns negative."

**Q7: "Where does the IGS-to-opportunity-gap mapping come from? How do you decide a community needs childcare versus fresh food?"**
> "We use the IGS Community pillar's sub-indicators — childcare access is in there directly. Fresh food gaps come from USDA Food Access Atlas overlaid on tract-level FIPS. Where IGS has a sub-indicator, we use it. Where it doesn't, we triangulate with public data — ACS, USDA, HRSA. Our analysis showed that economic predictors are stable across bootstrap resampling, so the gap-identification logic is statistically defensible, not just intuitive."

**Q8: "What happens to CAN if Mastercard isn't involved?"**
> "Without Mastercard, CAN loses three things: the IGS data layer, the payment-rail backbone for stakeholder funding routing, and the merchant-network distribution. Those are the structural reasons CAN works at scale, not at one-off pilot scale. A grant-funded version of the platform without those three could exist, but it would be a community resource directory, not an operating model. The Mastercard infrastructure is what makes it a platform."

---

## What to Say When You Don't Know

- **"What the data can support is..."**
- **"That is exactly why we pre-registered a stop/go threshold."**
- **"We are not claiming proof there; we are claiming enough signal to justify a bounded pilot."**
- **"We tested the prototype with [N] sample inputs. The production version improves on that with..."**

Avoid:
- "The disciplined answer is..." — verbal stall
- Starting any answer with "Notebook 2 Section F shows..." — give the human answer first, the technical reference second
- Claiming the AI is more sophisticated than it actually is

---

## Pre-Pitch Final Checklist

### 24 hours before
- [ ] Every number on the deck verified against the notebooks one final time
- [ ] CAN prototype tested on the device you'll use at the pitch (laptop, projector, browser)
- [ ] Five complete team rehearsals done, all front-to-back, all under target time
- [ ] Slide 7 specifically rehearsed at least eight times — Speaker B owns it cold
- [ ] Q&A drilled with at least two outside reviewers, focusing on Q3, Q4, Q5 (the platform questions)
- [ ] Final deck export — PDF backup, USB stick, email to yourselves
- [ ] If using a live demo on slide 7, have a 30-second screen-cap recording as backup
- [ ] Sleep early. Do not stay up rehearsing past 10pm.

### 2 hours before
- [ ] Water on stage
- [ ] Charger and adapter
- [ ] Phones silent
- [ ] No new content. No script edits. No deck changes. Period.
- [ ] Three deep breaths before walking in.

### Walking on stage
- [ ] Speaker A: eye contact with one judge before the first sentence.
- [ ] First sentence is the most important sentence. Land it.
- [ ] Speak ~10 percent slower than feels natural. Nerves accelerate delivery.

### During slide 7
- [ ] Speaker B: do not rush. The platform reveal needs to land.
- [ ] Point at each screenshot deliberately as you describe it.
- [ ] Pause after "That's the loop. Mastercard makes every step of it possible." Let that sentence sit.

---

## Final Notes

You took a 96/100 deck and rebuilt it as a 97/100 deck around a working prototype. The platform reveal on slide 7 is now your strongest moment in the pitch. Speaker B owns it. They need to deliver it cold.

What determines your finish from here:

1. **Slide 7 delivery.** Practice this slide more than any other. It's the moment that wins or loses you the room.
2. **Q&A on the platform.** Drill Q3, Q4, Q5 until the answers are automatic.
3. **The close.** "CAN is that model. Thank you." should be slow, eye-contact-with-the-room delivery. Not rushed.

You're walking in as a top-2 favorite. The deck is done. The script is calibrated.

Go win Atlanta.

— End of Script —
