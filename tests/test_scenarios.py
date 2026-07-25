from retrofit_analysis.scenarios import generate_scenarios


def test_reference_scenario_count_and_order():
    scenarios = generate_scenarios()
    assert len(scenarios) == 18_421
    assert scenarios[0].as_list() == [
        "W0", "Wi0", "R0", "F0", "S0", "CC", "CC", "CC", "CC", "CC"
    ]
    assert scenarios[1].as_list() == [
        "W0", "Wi0", "R0", "F1", "S0", "CC", "CC", "CC", "Now", "CC"
    ]
    assert scenarios[9].as_list() == [
        "W0", "Wi0", "R0", "F2", "S0", "CC", "CC", "CC", "10_years", "CC"
    ]


def test_checkpoint_identifier_behavior():
    assert generate_scenarios()[1].checkpoint_identifiers() == [
        "W0_Wi0_R0_F1_S0",
        "W005_Wi005_R005_F1_S0",
        "W010_Wi010_R010_F1_S0",
        "W015_Wi015_R015_F1_S0",
        "W020_Wi020_R020_F1_S0",
        "W025_Wi025_R025_F1_S0",
    ]


def test_shading_never_precedes_window_upgrade():
    order = {"Now": 0, "5_years": 1, "10_years": 2, "15_years": 3, "20_years": 4, "25_years": 5}
    for scenario in generate_scenarios():
        if scenario.shading == "S1":
            assert scenario.window != "Wi0"
            assert order[scenario.shading_time] >= order[scenario.window_time]
