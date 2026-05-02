class OffTargetAnalyzer:
    """
    Description:
        Serves as a genomic safety checkpoint by mathematically evaluating the off-target 
        risk of candidate gRNAs and isolating the safest sequence for construct building.

    Input:
        candidate_gRNAs (list): List of dicts from Step 1, e.g., [{"gRNA": "ATGC...", "score": 95.0}]
        organism (str): Target organism genome to scan.
        cas_variant (str): Pass-through variable for downstream construction.
        target_gene (str): Pass-through variable.
        cell_type (str): Pass-through variable.
        edit_type (str): Pass-through variable.
        kit_choice (str): Pass-through variable.

    Output:
        dict: A structured JSON containing the optimal guide_sequence, its risk profile, 
              and all necessary pass-through metadata for the Construction File Builder.

    Tests:
        - Case:
            Input: candidate_gRNAs=[{"gRNA": "GAGTCCGCAGTCTTAGAGCT", "score": 95.0}], organism="human", cas_variant="SpCas9", target_gene="BRCA1", cell_type="HEK293", edit_type="knockout", kit_choice="PX459"
            Expected Output: {"guide_sequence": "GAGTCCGCAGTCTTAGAGCT"}
            Description: Standard pass-through and risk calculation.
    """

    def initiate(self) -> None:
        self.mm_penalties = {0: 0.0, 1: 0.1, 2: 0.6, 3: 0.9}
        
        self.locus_penalties = {
            "essential coding gene": 0.0, 
            "exon": 0.4, 
            "promoter": 0.7, 
            "intron": 0.95, 
            "intergenic": 1.0
        }

    def run(self, candidate_gRNAs: list, organism: str, cas_variant: str, target_gene: str, cell_type: str, edit_type: str, kit_choice: str) -> dict:
        
        if not candidate_gRNAs:
            raise ValueError("The candidate_gRNAs list cannot be empty.")

        scored_candidates = []

        for candidate in candidate_gRNAs:
            gRNA_seq = candidate.get("gRNA", "")
            baseline_score = candidate.get("score", 0.0)

            raw_results = self._run_cas_offinder(gRNA_seq, organism)
            
            off_target_data = self._extract_off_target_data(raw_results)
            
            safety_score = self._calculate_safety_score(baseline_score, off_target_data)

            scored_candidates.append({
                "gRNA": gRNA_seq,
                "baseline_score": baseline_score,
                "safety_score": safety_score,
                "off_target_data": off_target_data
            })

        optimal_guide = self._select_optimal_guide(scored_candidates)

        mismatch_dist = {"0MM": 0, "1MM": 0, "2MM": 0, "3MM": 0}
        for site in optimal_guide["off_target_data"]:
            mm_key = f"{site['mismatch_count']}MM"
            if mm_key in mismatch_dist:
                mismatch_dist[mm_key] += 1

        return {
            "cas_variant": cas_variant,
            "target_gene": target_gene,
            "organism": organism,
            "cell_type": cell_type,
            "guide_sequence": optimal_guide["gRNA"],
            "edit_type": edit_type,
            "kit_choice": kit_choice,
            "off_target_risk_profile": {
                "total_off_targets": len(optimal_guide["off_target_data"]),
                "mismatch_distribution": mismatch_dist
            }
        }

    def _run_cas_offinder(self, gRNA: str, organism: str) -> list:
        mock_hits = []
        if len(gRNA) >= 20:
            mock_hits.append({
                "sequence": gRNA[:-2] + "AA",
                "mismatches": 2,
                "locus_type": "promoter"
            })
            
            if gRNA.startswith("A") or gRNA.startswith("G"):
                mock_hits.append({
                    "sequence": gRNA[:-1] + "C",
                    "mismatches": 1,
                    "locus_type": "intron"
                })
        return mock_hits

    def _extract_off_target_data(self, cas_offinder_results: list) -> list:
        parsed_data = []
        for res in cas_offinder_results:
            parsed_data.append({
                "sequence": res["sequence"],
                "mismatch_count": res["mismatches"],
                "genomic_location": res["locus_type"]
            })
        return parsed_data

    def _calculate_safety_score(self, baseline_score: float, off_target_data: list) -> float:
        current_score = baseline_score

        for site in off_target_data:
            mm_count = site["mismatch_count"]
            locus = site["genomic_location"]

            mm_multiplier = self.mm_penalties.get(mm_count, 1.0)
            locus_multiplier = self.locus_penalties.get(locus, 1.0)

            current_score = current_score * mm_multiplier * locus_multiplier

        return max(0.0, round(current_score, 2))

    def _select_optimal_guide(self, scored_candidates: list) -> dict:
        if not scored_candidates:
            raise ValueError("No scored candidates available to select from.")
            
        sorted_guides = sorted(
            scored_candidates, 
            key=lambda x: (x["safety_score"], x["baseline_score"]), 
            reverse=True
        )
        return sorted_guides[0]

_instance = OffTargetAnalyzer()
_instance.initiate()
analyze_off_targets = _instance.run