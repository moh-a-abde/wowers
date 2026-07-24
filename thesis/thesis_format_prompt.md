# Master's Thesis Generation Prompt — "Business Case + Technical Proof-of-Concept" Format

> **How to use this file:** Fill in every `{{PLACEHOLDER}}` in Section 0, then paste this entire document
> into the AI as a single prompt. Everything after Section 0 is instruction to the model, not to you.
> Do not delete the rule sections — they are what makes the output match the reference format.

---

## 0. Project Variables (fill these in before running)

| Variable | Your value |
|---|---|
| `{{COMPANY_NAME}}` | *(the proposed venture, e.g. "AeroSun Analytics")* |
| `{{THESIS_TITLE}}` | *(pattern: "`{{COMPANY_NAME}}`: A Proof-of-Concept `{{ARTIFACT_TYPE}}` for `{{CAPABILITY}}`")* |
| `{{AUTHORS}}` | *(one per line, ALL CAPS, no titles)* |
| `{{UNIVERSITY}}` | |
| `{{SCHOOL_OR_COLLEGE}}` | *(e.g. "School of Engineering")* |
| `{{DEGREE}}` | *(e.g. "Master of Science")* |
| `{{MONTH_YEAR}}` | *(e.g. "August 2025")* |
| `{{ADVISOR}}` | |
| `{{SECONDARY_FACULTY}}` | *(business/other advisors thanked in Acknowledgements)* |
| `{{INDUSTRY_CONTACTS}}` | *(name, title, company — real-world practitioners thanked)* |
| `{{PROBLEM_DOMAIN}}` | *(the industry whose pain is being solved, e.g. "utility-scale solar maintenance")* |
| `{{CORE_TECHNOLOGY}}` | *(the accelerating/enabling tech, e.g. "FPGA-accelerated CNN inference")* |
| `{{DATA_SOURCE_HARDWARE}}` | *(the COTS device supplying input, e.g. "DJI Mini 3 Pro drone")* |
| `{{TARGET_METRICS}}` | *(3–5 headline numbers the thesis will prove, e.g. throughput, power, accuracy)* |
| `{{TOTAL_LENGTH}}` | *(target 18,000–24,000 words body text, excluding references and appendices)* |

---

## 1. Role and Task

You are writing a complete Master of Science thesis in `{{SCHOOL_OR_COLLEGE}}`. The thesis has a
**dual mandate**: it argues that a proposed company is a viable business, and it documents a
working technical proof-of-concept that de-risks the hardest part of that company's technology.
Both halves must be present, and the technical half must be roughly three times the length of the
business half.

Write the full document in Markdown. Do not summarize, do not outline, do not offer to write
sections later. Produce the finished thesis in one pass.

---

## 2. Mandatory Document Skeleton

Reproduce this front matter and chapter structure exactly. Chapter numbering is flat-decimal
(`4.4.8`), never Roman, never lettered.

```
Title page
Certification page
Abstract
Acknowledgements
Table of Contents
List of Figures
List of Tables

1 Introduction
  1.1 Thesis Statement
  1.2 Thesis Outline

2 Background and Prior Work
  2.1 {{Domain}} and Common {{Failure Modes}}
  2.2 Current {{Practice}} and {{Detection}} Techniques
  2.3 {{Enabling Technology, plain-language primer}}
  2.4 {{Acceleration / optimization of that technology}}

3 Business Model
  3.1 The Problem
  3.2 The Solution
  3.3 The Target Market
  3.4 Competition
  3.5 Pricing Model
  3.6 Marketing and Distribution
  3.7 Market Potential
  3.8 Future Vision and Project Timeline

4 Design Details
  4.1 System Overview
  4.2 {{Input Acquisition Subsystem}}
    4.2.1 {{Hardware and vendor SDK interface}}
    4.2.2 {{Companion application}}
  4.3 {{Data Transport Subsystem}}
    4.3.1 {{Protocol selection and rationale}}
    4.3.2 {{Second-hop protocol}}
    4.3.3 {{Auxiliary service}}
    4.3.4 {{Development / emulation tooling}}
  4.4 {{Core Compute Design}}
    4.4.1 through 4.4.9 — one subsection per toolchain stage, ending with a
          "{{X}} Design Build Process Summary" that carries a single flowchart figure
  4.5 {{Custom Hardware Schematic Design}}
    4.5.1 {{Main device and peripherals}}
    4.5.2 {{Power delivery}}
    4.5.3 Expected Power Consumption and Battery Life
    4.5.4 {{Compliance / robustness considerations}}
  4.6 {{Custom Hardware Physical Design}}
    4.6.1 Mechanical and Thermal Considerations
    4.6.2 {{Layout}} Overview
    4.6.3 {{Power routing}}
    4.6.4 {{Signal integrity constraints}}
    4.6.5 {{Programming and Memories}}
    4.6.6 Hardware Test Plan
    4.6.7 Hardware Cost

5 Experiments and Results
  5.1.1 Best Case and Expected System Performance
  5.1.2 through 5.1.6 — one subsection per subsystem, in the same order they
        appeared in Chapter 4, ending with System Integration Tests
  5.1.7 {{Resource Utilization / scaling headroom}}
  5.1.8 {{Simulation results}}

6 Conclusions and Future Work

References

Appendix A: {{Bill of materials, detailed tables}}
Appendix B: {{Raw measurement captures}}
Appendix C: {{Simulation output figures}}
```

**Quirk to preserve:** Chapter 5's subsections start at `5.1.1`, not `5.1`. There is no `5.1`
heading. This is inherited from the reference document and is intentional.

---

## 3. Front Matter Templates

### 3.1 Title page

```
{{THESIS_TITLE}}

A THESIS
SUBMITTED TO THE FACULTY OF THE GRADUATE SCHOOL
OF {{UNIVERSITY}}
BY

{{AUTHOR 1, ALL CAPS}}
{{AUTHOR 2, ALL CAPS}}

IN PARTIAL FULFILLMENT OF THE REQUIREMENTS
FOR THE DEGREE OF {{DEGREE}}

{{MONTH_YEAR}}
```

### 3.2 Certification page

```
{{UNIVERSITY}}

This is to certify that I have examined this copy of Master's thesis by

{{Author 1}}
{{Author 2}}

and have found it is complete and satisfactory in all respects,
and that any and all revisions required by the final
examining committee have been made.

______________________
Name of Faculty Advisor(s)

_____________________________________
Signature of Faculty Advisor(s)

_____________________________________
Date

GRADUATE PROGRAM
{{SCHOOL_OR_COLLEGE}}
```

### 3.3 Abstract — exactly five paragraphs, 350–450 words total

1. **Opportunity and pain.** Open with the macro opportunity, then narrow to the specific
   inefficiency. Quantify the loss in dollars or energy at global or national scale. Close by
   naming the promising-but-currently-manual approach that fails to capture the value.
2. **The proposal.** One sentence naming the company and what it solves. One sentence stating
   what the technical research aims to demonstrate, with the phrase "that can be built on later
   in the development of a minimum viable product (MVP)".
3. **What was built.** Two or three sentences tracing the dataflow end to end, in order.
4. **What was measured.** Report the headline numbers from `{{TARGET_METRICS}}` with full
   measured precision — do not round. Note simulation status separately from measured status.
5. **What it enables.** State that the work forms a knowledge base and development system, then
   name the three specific improvements that would carry it to customer value.

### 3.4 Acknowledgements — four short paragraphs

Advisor first ("valuable guidance, feedback, and encouragement"). Business-side faculty second
("business advice and perspective, which helped shape the direction and real-world applicability").
Industry practitioners third, by name and title and company, for domain insight. A one-line
catch-all thanks last.

### 3.5 Table of Contents, List of Figures, List of Tables

Render as dot-leader lines with page numbers. Every figure and table in the body must appear
here, numbered sequentially across the whole document (figures and tables number independently,
and appendix figures continue the same sequence rather than restarting).

---

## 4. Voice, Tense, and Sentence Mechanics

These rules are what make the output read as an engineering thesis rather than as a blog post or
a marketing deck. Follow all of them.

**Person and tense**
- Use "we" for authorial decisions and results: *we designed*, *we proved*, *we propose*,
  *we recorded*.
- Use passive or impersonal voice for process description: *the routing was done with matched
  40 Ω traces*, *a voltage monitoring circuit was added*, *this test would pass if…*.
- Use present tense for how the system works, past tense for what was done and measured.
- Never use second person. Never address the reader.

**Signposting**
Every major section ends with a forward-pointing sentence, and many begin by naming what follows.
Use these constructions liberally — they are a signature of the format:
- "…will now be discussed."
- "These common faults will now be discussed in more detail."
- "For a full breakdown of the real-world tests and corresponding throughput see section 5.1.3."
- "The rationale behind the final choice will now be discussed."
- "A more detailed look at … will now be discussed."

**Figure and table references**
- Every figure and table is named in prose *before* it appears: "…can be seen in Figure 14",
  "The full list … can be seen in Table 5", "Figure 5 below depicts the described model
  architecture."
- Tables are captioned *above* the table. Figures are captioned *below* the figure.
- Caption style: `Table 6: System hardware cost` / `Figure 23: Simulated DC IR drop test for
  1.8 V rail` — sentence case, no terminal period.

**Numbers and units**
- Always a space between value and unit: `1.7368 W`, `6.25 MHz`, `512 MB`, `40 Ω`, `±10 ps`.
- Report measurements at the precision they were taken. `18.22 FPS`, `1.7368 W`, `82.62%`,
  `44.31 ms`, `0.4117 MB/s`. Do not clean these to round numbers.
- Express derived estimates with their assumption inline: *"assuming a 90% conversion efficiency"*,
  *"assuming the voltage ramp rate is linear"*, *"assuming a worst environmental operating
  temperature of 40°C"*.
- Show the arithmetic when a reader would otherwise have to trust you:
  *"3.3 V / 1.5 ms = 2200 V/s"*.

**Specificity**
Name every part, tool, version, and vendor. Never write "a microcontroller" when you mean
`ESP32-S3-WROOM-1-N16R8`. Never write "simulation software" when you mean `Ansys SIwave`.
Include tool versions when they mattered (`Vivado 2022.2`, `Ubuntu 18.04`, `WSL 2.0`,
`PYNQ-Z2 v3.1 SD card image`). Include exact machine specs when a build was resource-constrained.

**Word choice**
- Plain verbs over formal ones: *make* not *fabricate*, *end* not *terminate*, *start* not
  *commence*, *find out* not *ascertain*, *try* not *endeavor*, *see* not *perceive*, *get* not
  *acquire*, *say* not *articulate*, *look into* not *investigate*, *change* not *modify*,
  *convince* not *persuade*, *live* not *reside*, *get back* not *retrieve*.
- Replace "very + adjective" with a single stronger word (*deafening*, *ancient*, *rapid*,
  *massive*, *obvious*, *brief*, *sluggish*).
- Do not use rhetorical questions, exclamation points, em-dash asides, or bulleted fragments
  in body prose. Bullets appear only for enumerated build outputs, pricing tiers, and
  specification lists.

---

## 5. Chapter-by-Chapter Content Rules

### Chapter 1 — Introduction (900–1,200 words)
Open with the macro trend and a hard capacity or market number. Explain why the current approach
does not scale, naming the physical constraint (area, height, access, frequency). Propose the
company in a paragraph that starts "We propose the creation of a company, `{{COMPANY_NAME}}`, to…".
Describe the end-state automated workflow in one paragraph, step by step. Then state plainly that
the required development is vast, and split it into technical development and logistical
development, listing what each contains. Close: "This work will discuss the business model of
`{{COMPANY_NAME}}` with additional focus on the first steps in its technical development."

**1.1 Thesis Statement** — one paragraph, ~120 words. State the proposition, the scope of the
business discussion, and what the proof-of-concept develops.

**1.2 Thesis Outline** — one paragraph walking chapter by chapter in order, each with a clause
describing its content.

### Chapter 2 — Background and Prior Work (2,000–2,800 words)
- **2.1** — enumerate the failure modes as a numbered set in the opening ("there are six common
  faults…"), then give each one its own paragraph in the same order. Every fault paragraph must
  end with a quantified efficiency or performance impact and a bracketed citation. Include a
  rule-of-thumb figure where the field has one.
- **2.2** — describe current practice honestly, including what practitioners already do well.
  Name which failure modes current methods catch and which they miss.
- **2.3** — a from-first-principles primer on the enabling technology, written for a reader in an
  adjacent discipline. Scope it explicitly ("this paper discusses only the prediction, or
  inference, of these models, not the training"). Build up layer by layer or stage by stage.
  End by explaining *why* the standard hardware is inefficient — this sets up 2.4.
- **2.4** — the acceleration argument, supported by 8–12 bracketed citations to prior work.
  Compare at least three named prior implementations by a common metric (parameter count,
  resource utilization, throughput). This is where the literature review density peaks.

### Chapter 3 — Business Model (2,000–2,500 words)
Each subsection is 150–400 words. Non-negotiable content:
- **3.1** — restate the problem with a global or national dollar figure and a unit-level figure.
  Enumerate three named complications.
- **3.2** — the service, in one paragraph. Include the optional partner/ecosystem play.
- **3.3** — pick one **real, named** installation or customer as the archetype. Give its size,
  output, and the specific feature that makes it hard to serve conventionally.
- **3.4** — name real competitors. Concede what they do well. Identify the specific gap.
- **3.5** — three price tiers as a bulleted list with dollar figures. Then a single sentence
  showing the derivation: *"This pricing was calculated as X% of the value of the `{{benefit}}`
  regained from a Y% improvement at a Z-scale installation."*
- **3.6** — three named stages, in order, with the goal of each.
- **3.7** — TAM arithmetic shown explicitly, then narrowed to a serviceable regional market, then
  narrowed again to a realistic share (~10%). Three numbers, each derived from the last.
- **3.8** — growth outlook with a named upcoming project, then the milestone sequence, then the
  argument for which milestone is the true core value and therefore gets built first.

### Chapter 4 — Design Details (9,000–12,000 words — the bulk of the thesis)
- **4.1** carries the system block diagram (Figure 1) and walks the dataflow in order. It must
  end with an honesty paragraph: *"For this work, although a full solution has been implemented,
  it does not strictly follow the proposed design and functions as proof of concept. The notable
  differences in design are …"*
- Every subsystem section follows the same internal shape:
  1. What this part is responsible for.
  2. The options considered — name at least three.
  3. Why the chosen option won, in terms of the stated requirements.
  4. How it was implemented, in enough detail to rebuild it.
  5. Known limitations, deferred to future work by name.
- State requirements as explicit lists before selecting: *"There are four main requirements of
  data transfer between X and Y. The transfer must be …"*
- Include at least one state machine figure with named states and labeled transitions, described
  state by state in prose.
- Include at least one build-process flowchart summarizing a multi-tool pipeline, with each tool
  as a labeled swim lane.
- Document environment struggles as findings, not complaints. Give the exact configuration that
  finally worked and the exact one that failed.
- Power/resource budgets go in a table with one row per consumer plus TOTAL rows per rail or
  category.
- Cost analysis states what was excluded from the total and why.

### Chapter 5 — Experiments and Results (3,500–4,500 words)
- **5.1.1 must come first** and must establish theoretical/ideal performance *before* any
  measurement is presented. Produce two parallel tables: **Ideal system transfer performance**
  and **Expected system transfer performance**, with identical column headers, differing only in
  the assumptions applied. Columns follow the dataflow left to right and end in a Total column.
- Each following subsection: setup (name the exact hardware and instruments used), method,
  result table, then a discrepancy paragraph.
- **The discrepancy paragraph is mandatory wherever measured ≠ expected.** It must (a) state the
  gap numerically, (b) identify the mechanism, (c) say whether the gap is acceptable for the
  current scope, and (d) name the specific change that would close it. Example shape:
  *"These measurements are quite a bit slower than the expected transfer time of 3.78 ms. The
  source of this extra delay is … Albeit slower, the measured speed was deemed enough for … To
  increase the overall bandwidth, … would drastically improve performance."*
- Report results that undercut your own assumptions as readily as results that support them.
  If a tool failed to produce usable output, say so and list the specific reasons it failed.
- The integration test must use realistic stimulus and say why that stimulus is representative.
- Include an energy-per-operation column where two implementations are compared, not just
  time and power separately.

### Chapter 6 — Conclusions and Future Work (700–1,000 words)
Paragraph 1: what was designed and tested, and which MVP requirements it fulfills.
Paragraph 2: the demonstration, restating the headline metrics at full precision.
Paragraph 3: one sentence naming the three future-work themes.
Then one paragraph per theme, each explaining what specifically to change and why it matters.
Final paragraph: position the work as the first step toward customer value for the company.

---

## 6. Citation and Reference Format

- In-text: bracketed numerals in citation order of first appearance — `[1]`, `[2]`, `[10], [12],
  [13], and [14]`. Cite every quantitative claim taken from outside the work.
- Reference list: IEEE-adjacent, in numerical order.
  - Journal/conference: `A. Author, B. Author and C. Author, "Title in sentence case," Publisher
    or Venue, vol. X, no. Y, pp. Z-Z, YEAR.`
  - Web: `Organization, "Page title," DD Month YYYY. [Online]. Available: URL. [Accessed DD Month
    YYYY].`
- Target 40–50 references. Mix of peer-reviewed papers, vendor datasheets, tool documentation,
  government/agency statistics, competitor websites, and at least one community forum post or
  GitHub repository where that is genuinely where the solution came from.
- Cite datasheets for every hardware limit you claim.

---

## 7. Tables and Figures — Required Inventory

Produce a minimum of **20 figures** and **20 tables**. The following must exist:

**Figures**
1. System block diagram (Chapter 4.1)
2. Application/software flow diagram
3. User interface screenshot description
4. Protocol state machine
5. Core design architecture diagram
6. Integrated block design (top level)
7. Simplified block diagram of the same, for readability
8. Operation flowchart split into two labeled lanes
9. Full build-process flowchart with per-tool swim lanes
10. Custom hardware block diagram
11–13. Schematic excerpts for input selection, power conversion, and protection
14. Vendor tool estimate summary
15–16. Physical assembly renders, front and back
17–18. Measurement captures for two competing implementations
19–20. Simulation results, one per analysis type
+ appendix figures continuing the same numbering

**Tables**
1. Pin/interface assignment
2. Power consumption per consumer with TOTAL rows
3. Thermal performance per component (power, thermal characteristic, resulting temp, max temp)
4. Design limit vs. designed value per rail
5. Memory inventory (device, section, type, size)
6. Cost breakdown with a Total row
7. Ideal system performance
8. Expected system performance
9. Measured transfer rates
10. Cross-platform performance comparison
11. Integration test results including energy per operation
12. Resource utilization (used / available / % utilization)
13. Reference platform support matrix
14. Scale comparison by parameter count
15. Resource comparison between the used platform and the next tier up
16–17. Worst-case simulated values
18–20. Appendix bills of materials and detailed matching tables

Tables use plain Markdown pipe syntax. Keep column headers short and in title case.

---

## 8. Intellectual Honesty Requirements

The reference document's credibility comes from these habits. Reproduce all of them:

1. **State the gap between proposal and implementation early**, in the system overview, not buried
   in conclusions.
2. **Use a stand-in where the real thing was out of scope**, and say so plainly — e.g. a pretrained
   public-dataset model standing in for the domain model, with the reason given ("the model itself
   is not central to the interest of this paper").
3. **Report the compromise conditions** under which a test was run (reduced clock rate, single-bit
   instead of quad, jumper wires instead of PCB) and what the compromise cost in performance.
4. **Report failures with mechanisms**: list the specific reasons a tool or method did not work.
5. **Separate simulated from measured** everywhere. Never let a simulated number sit unlabeled
   next to a measured one.
6. **Flag out-of-spec results even when nothing was done about them** — e.g. a decoupling network
   that shows unacceptable impedance at the operating bandwidth, with the fix deferred and named.
7. **Attribute borrowed code and designs** to their forum post, tutorial, or repository.
8. **Never claim customer validation that did not happen.** Business projections are labeled as
   estimates and assumptions.

---

## 9. Output Instructions

- Output Markdown only. Use `#` for chapter titles, `##` for `X.Y`, `###` for `X.Y.Z`.
- Where a figure would appear, insert a placeholder block:
  `> **[FIGURE N]** — {{one-sentence description of what the figure must show}}`
  followed immediately by the italic caption line. This gives a designer a build list.
- Write the entire document. Do not truncate, do not write "…continues similarly", do not stop
  to ask whether to proceed.
- Total body length: `{{TOTAL_LENGTH}}`.
- No meta-commentary, no notes to the reader, no explanation of your own process anywhere in the
  output.
