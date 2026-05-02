# CRISPR Off-Target Analyzer: Biological Theory & Scoring Logic

## 1. Module Purpose
The `Off-Target Analyzer` serves as a critical genomic safety checkpoint in the CRISPR design pipeline. While upstream tools identify guide RNAs (gRNAs) that are highly efficient at cutting the intended target, high efficiency is dangerous if the Cas enzyme also cuts elsewhere in the genome. This module ensures that the final recommended gRNA is not only active but genomically safe, preventing unintended collateral mutations.

## 2. Biological Theory: Mismatches
Cas nucleases (like SpCas9) use a 20-nucleotide gRNA to navigate the genome. However, the enzyme can sometimes tolerate imperfect binding, leading to off-target cleavage. The severity of this risk is determined by the **mismatch count**—the number of incorrect base pairings between the gRNA and the off-target DNA sequence.

This tool evaluates mismatches based on the following biological heuristic:
* **0 Mismatches (Multiplier: 0.0):** Fatal risk. The exact sequence exists perfectly elsewhere in the genome.
* **1 Mismatch (Multiplier: 0.1):** Severe risk. The Cas enzyme is highly likely to tolerate a single mismatch and induce a cut.
* **2 Mismatches (Multiplier: 0.6):** Moderate risk. Cleavage is possible depending on expression levels and time.
* **3 Mismatches (Multiplier: 0.9):** Low risk. Cas enzymes rarely cleave sequences with 3+ mismatches, but a minor penalty is applied for safety.

## 3. Biological Theory: Genomic Locus
If an off-target cut *does* occur, the phenotypic consequence depends entirely on where the cut happens. The tool applies spatial penalties based on the genomic location of the off-target site:
* **Essential Coding Gene (Multiplier: 0.0):** Fatal risk. Disrupting a known essential housekeeping gene or tumor suppressor can kill the cell or induce oncogenesis.
* **Exon (Multiplier: 0.4):** Heavy penalty. Frameshifts in standard protein-coding regions can knock out unintended proteins.
* **Promoter (Multiplier: 0.7):** Moderate penalty. Indels in regulatory regions can permanently upregulate or downregulate neighboring genes.
* **Intron (Multiplier: 0.95):** Light penalty. Introns are spliced out during mRNA maturation, so mutations here rarely affect the final protein.
* **Intergenic (Multiplier: 1.0):** No penalty. Mutations in "gene deserts" are generally well-tolerated by the cell.

## 4. The Mathematical Scoring Model
The tool synthesizes these biological realities into a single deterministic mathematical equation. It takes the baseline on-target efficiency score and aggressively penalizes it for every off-target site found by multiplying the score by the respective risk factors.

The mathematical penalty is calculated as:

$$\text{Safety Score} = \text{Baseline Score} \times \prod_{i=1}^{n} (\text{Mismatch Penalty}_i \times \text{Locus Penalty}_i)$$

**Example Calculation:**
If a guide enters the module with a baseline score of `95.0` and has a single off-target site located in a promoter (0.7) with 2 mismatches (0.6), the adjusted safety score is calculated as follows:

$$\text{Safety Score} = 95.0 \times (0.6 \times 0.7) = 39.9$$

By applying this model, a guide that starts with a perfect efficiency score but harbors dangerous off-target risks will be out-competed by a slightly less efficient, but vastly safer, alternative.