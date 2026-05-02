# CRISPR Off-Target Analyzer — Skill Guidance for Gemini

## What this module does
This module acts as a genomic safety checkpoint in a multi-step CRISPR design pipeline. It takes a list of candidate guide RNAs (gRNAs) that have already been scored for on-target efficiency, and evaluates them for potential off-target cleavage risks across a specified organism's genome. It mathematically penalizes guides that bind to dangerous genomic locations (like promoters or essential genes) and isolates the single safest gRNA to pass downstream to the Construction File Builder.

## Available resources
| Resource name | Description |
|---------------|-------------|
| `dynamic` | This tool does not rely on static local `.gb` files. It dynamically accepts an `organism` string (e.g., "human", "E. coli", "mouse") to configure the off-target scanning parameters. |

## Tools and when to use them

### `analyze_off_targets`
Call this tool when the user provides a list of candidate gRNAs and asks to evaluate their safety, scan for off-target effects, or determine which guide is the safest to use.
- **Trigger phrases:** "Run an off-target safety scan," "Evaluate this list of guides," "Check these candidates for off-target effects," "Which of these guides is the safest?"
- **Parameter notes:** - `candidate_gRNAs`: Must be a list of dictionaries containing the guide sequence and its baseline score.
  - Pass-through variables (`cas_variant`, `target_gene`, `cell_type`, `edit_type`, `kit_choice`): You must extract these from the user's prompt and pass them into the tool exactly as provided. Do not omit them, as they are strictly required for the next step of the user's pipeline.
- **Output notes:** The tool returns a single JSON object containing the optimal, safest `guide_sequence`, its detailed `off_target_risk_profile`, and all the pass-through variables.

## Interpreting results
When explaining the final result to the user, use the `off_target_risk_profile` to justify why the guide was chosen. You need to understand the backend math to explain this properly:
- **Baseline vs. Safety Score:** The tool starts with the guide's original efficiency score and mathematically subtracts points based on off-target risk.
- **Mismatch Penalties:** A perfect match (0 mismatches) at an off-target site is highly dangerous. 1 mismatch is severely penalized (0.1 multiplier), 2 mismatches are moderately penalized (0.6 multiplier), and 3 mismatches receive a light penalty (0.9 multiplier).
- **Genomic Location Penalties:** Where the off-target cut happens matters. Hitting an "essential coding gene" applies a 0.0 multiplier, acting as a fatal penalty that immediately disqualifies the guide. Promoters (0.7) and exons (0.4) are also heavily penalized compared to introns (0.95) or intergenic regions (1.0).
- **Communication Style:** Do not just list the math. Explain the biological reality. For example, "Guide B was selected because Guide A was heavily penalized for a high-risk 2-mismatch off-target site located in a promoter region."