# BioE134 Final Project: CRISPR Engineering Workflow Assistant - Off-Target Analyzer
**Author:** Derek Manahan

**Team Members:** Aubrey Pham, Yu-Shan Fu, Nathan Jimenez, Trinav Chaudhuri


## 1. Project Scope
This repository contains my individual contribution for our BioE 134 Final Project. Our team's big-picture goal was to build an end-to-end CRISPR experiment design assistant driven by Gemini via the Model Context Protocol (MCP). When a user describes a CRISPR experiment, our pipeline walks them through target selection, guide design, safety analysis, construction file building, delivery strategy, and validation planning.

My specific responsibility and scope is to implement an **Off-Target Analyzer**, which acts as the genomic safety checkpoint of the pipeline. It takes the ranked candidate guide-RNAs from Step 1 (Guide RNA Designer), and evaluates their potential unintended cleavage sites across the genome, and mathematically penalizes their baseline efficiency scores based on biological risk factors. The tool ultimately isolates the single safest gRNA and passes it, along with necessary metadata, downstream to Step 3 (Construction File Builder).

---

## 2. Functions Developed
To accomplish this, I developed a Python tool utilizing the Function Object Pattern (`initiate` and `run`). Inside this tool, I built four core helper functions that process the data deterministically:

* **`_run_cas_offinder(gRNA_list, organism)`**
  Acts as a simulator for the Cas-OFFinder algorithm. It dynamically generates realistic, deterministic mock off-target hits (including mismatches and locus types) based on the input guide's sequence length and starting characters to allow for reliable testing and LLM demonstration.
* **`_extract_off_target_data(cas_offinder_results)`**
  Parses the raw output from the mock Cas-OFFinder generator to neatly package the exact mismatch counts, genomic locations, and sequences into a structured list of dictionaries.
* **`_calculate_safety_score(baseline_score, off_target_data)`**
  The core biological logic module. It applies a mathematical penalty to the upstream baseline score. The multipliers are weighted by the number of mismatches (e.g., 1 mismatch is heavily penalized; 3 mismatches are lightly penalized) and the genomic locus (e.g., hitting an essential coding gene applies a fatal 0.0 multiplier, whereas an intron applies a minor 0.95 multiplier).
* **`_select_optimal_guide(scored_candidates)`**
  Sorts the heavily processed list of candidates by their new safety scores, handling edge-case tiebreakers, and isolates the single safest 20-nt guide sequence for the final output.

---

## 3. Key Accomplishments
* **Seamless Pipeline Integration:** Successfully engineered the tool to act as a data courier. It accepts required pass-through variables (like `cas_variant`, `kit_choice`, and `edit_type`) from the LLM prompt and guarantees they are packaged into the final JSON output so the next module in the pipeline has the exact inputs it expects.
* **Robust MCP Implementation:** Created a comprehensive `off_target_analyzer.json` C9 wrapper that correctly maps all 7 inputs and standardizes the tool for Gemini, alongside a `prompts.json` file that tests the tool across various biological domains (human cell lines, bacteria, and plant systems).
* **LLM Skill Injections:** Authored a comprehensive `SKILL.md` file that teaches Gemini the biological theory behind off-target mismatch penalties and locus dangers, allowing the AI to naturally and accurately explain *why* a specific score was heavily penalized to the end-user.
* **Rigorous Edge-Case Testing:** Designed a 12-test `pytest` suite that verifies the penalty math, checks tiebreaker sorting logic, validates the pass-through variable preservation, and catches edge cases like empty candidate lists or missing dictionary keys.