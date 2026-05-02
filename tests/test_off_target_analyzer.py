import pytest
from modules.off_target.tools.off_target_analyzer import OffTargetAnalyzer, analyze_off_targets

# Tests that the penalty dictionaries are populated accurately upon class initialization.
def test_initiate_populates_dictionaries():
    analyzer = OffTargetAnalyzer()
    analyzer.initiate()
    assert analyzer.mm_penalties[2] == 0.6
    assert analyzer.locus_penalties["essential coding gene"] == 0.0

# Tests that an empty candidate list raises a ValueError to prevent downstream pipeline crashes.
def test_empty_candidate_list_raises_error():
    analyzer = OffTargetAnalyzer()
    analyzer.initiate()
    with pytest.raises(ValueError, match="The candidate_gRNAs list cannot be empty."):
        analyzer.run([], "human", "SpCas9", "BRCA1", "HEK293", "knockout", "PX459")

# Tests that the safety calculation exactly matches the math outlined in the presentation slides.
def test_calculate_safety_score_slide_math():
    analyzer = OffTargetAnalyzer()
    analyzer.initiate()
    off_target_data = [{"mismatch_count": 2, "genomic_location": "intergenic"}]
    result = analyzer._calculate_safety_score(95.0, off_target_data)
    assert result == 57.0

# Tests an edge case where an essential gene hit acts as a fatal penalty to drop the score to zero.
def test_calculate_safety_score_fatal_penalty():
    analyzer = OffTargetAnalyzer()
    analyzer.initiate()
    off_target_data = [{"mismatch_count": 0, "genomic_location": "essential coding gene"}]
    result = analyzer._calculate_safety_score(100.0, off_target_data)
    assert result == 0.0

# Tests how the mathematical penalty stacks when a single guide has multiple off-target sites.
def test_calculate_safety_score_stacked_penalties():
    analyzer = OffTargetAnalyzer()
    analyzer.initiate()
    off_target_data = [
        {"mismatch_count": 1, "genomic_location": "promoter"},
        {"mismatch_count": 2, "genomic_location": "intron"}
    ]
    result = analyzer._calculate_safety_score(100.0, off_target_data)
    assert result == pytest.approx(3.99, 0.01)

# Tests that the optimal selection logic correctly sorts and returns the guide with the highest safety score.
def test_select_optimal_guide_by_safety():
    analyzer = OffTargetAnalyzer()
    candidates = [
        {"gRNA": "GUIDE_A", "baseline_score": 100.0, "safety_score": 30.0},
        {"gRNA": "GUIDE_B", "baseline_score": 90.0, "safety_score": 85.0}
    ]
    result = analyzer._select_optimal_guide(candidates)
    assert result["gRNA"] == "GUIDE_B"

# Tests an edge case where two guides have identical safety scores to ensure it falls back to the highest baseline score.
def test_select_optimal_guide_tiebreaker():
    analyzer = OffTargetAnalyzer()
    candidates = [
        {"gRNA": "GUIDE_A", "baseline_score": 90.0, "safety_score": 50.0},
        {"gRNA": "GUIDE_B", "baseline_score": 98.0, "safety_score": 50.0}
    ]
    result = analyzer._select_optimal_guide(candidates)
    assert result["gRNA"] == "GUIDE_B"

# Tests an edge case where passing an empty list to the selection helper raises a specific ValueError.
def test_select_optimal_guide_empty_error():
    analyzer = OffTargetAnalyzer()
    with pytest.raises(ValueError, match="No scored candidates available to select from."):
        analyzer._select_optimal_guide([])

# Tests the mock generator boundary condition where a guide shorter than 20 nucleotides produces no mock hits.
def test_mock_cas_offinder_short_length_edge_case():
    analyzer = OffTargetAnalyzer()
    short_guide = "ATGCATGCATGC"
    results = analyzer._run_cas_offinder(short_guide, "human")
    assert len(results) == 0

# Tests the mock generator character logic to ensure guides starting with G trigger severe penalties for the demo.
def test_mock_cas_offinder_g_start_penalties():
    analyzer = OffTargetAnalyzer()
    g_start_guide = "GAGTCCGCAGTCTTAGAGCT"
    results = analyzer._run_cas_offinder(g_start_guide, "human")
    assert len(results) == 2

# Tests the full MCP pipeline to guarantee all pass-through variables map correctly into the final JSON output.
def test_full_pipeline_passthrough_preservation():
    candidate_gRNAs = [{"gRNA": "CAGTCCGCAGTCTTAGAGCT", "score": 100.0}]
    result = analyze_off_targets(
        candidate_gRNAs=candidate_gRNAs,
        organism="human",
        cas_variant="SpCas9",
        target_gene="BRCA1",
        cell_type="HEK293",
        edit_type="knockout",
        kit_choice="PX459"
    )
    assert result["cas_variant"] == "SpCas9"
    assert result["kit_choice"] == "PX459"
    assert "guide_sequence" in result
    assert "off_target_risk_profile" in result

# Tests an edge case where a candidate dictionary is missing the score key to verify it safely defaults to 0.0.
def test_full_pipeline_missing_score_key():
    candidate_gRNAs = [{"gRNA": "CAGTCCGCAGTCTTAGAGCT"}]
    result = analyze_off_targets(
        candidate_gRNAs=candidate_gRNAs,
        organism="mouse",
        cas_variant="Cas12a",
        target_gene="PCSK9",
        cell_type="Hepa1-6",
        edit_type="knockin",
        kit_choice="pTarget"
    )
    assert result["guide_sequence"] == "CAGTCCGCAGTCTTAGAGCT"