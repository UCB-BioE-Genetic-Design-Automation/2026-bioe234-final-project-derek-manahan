import pytest
from modules.seq_basics.tools.off_target_analyzer import analyze_off_targets

def test_analyze_off_targets_basic_flow():
    mock_candidates = [{"gRNA": "GAGTCCGCAGTCTTAGAGCT", "score": 95}]
    
    result = analyze_off_targets(
        candidate_gRNAs=mock_candidates,
        organism="human",
        cas_variant="SpCas9",
        target_gene="BRCA1",
        edit_type="knockout",
        kit_choice="PX459",
        cell_type="HEK293"
    )
    
    # Assert the outputs map correctly
    assert result["guide_sequence"] is not None
    assert result["cas_variant"] == "SpCas9"
    assert result["cell_type"] == "HEK293" 
    assert "off_target_risk_profile" in result

def test_empty_gRNA_list():
    # Simulate Step 1 failing to find any valid PAM sites
    result = analyze_off_targets(
        candidate_gRNAs=[], 
        organism="human",
        cas_variant="SpCas9",
        target_gene="BRCA1",
        edit_type="knockout",
        kit_choice="PX459",
        cell_type="HEK293"
    )
    
    # Even with an empty list, it should still format the pass-through variables safely
    assert result["organism"] == "human"
    assert result["target_gene"] == "BRCA1"

def test_missing_required_arguments():
    # We purposefully leave out the `cell_type` argument here
    with pytest.raises(TypeError):
        analyze_off_targets(
            candidate_gRNAs=[{"gRNA": "GAGTCCGCAGTCTTAGAGCT", "score": 95}],
            organism="human",
            cas_variant="SpCas9",
            target_gene="BRCA1",
            edit_type="knockout",
            kit_choice="PX459"
        )