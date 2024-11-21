import sys
sys.path.append('C:/Users/kiun/pod_lca_data_analysis')

from pathlib import Path
# import pandas as pd
import src.utils.general as gen
import src.p_scenario_builder.PrebuiltScenarioBuilder as sb


def build_prebuilt_scenarios():
    """placeholder for implementation of prebuilt scenario"""
    # implement prebuilt scenario classes as appropriate
    main_directory = Path(__file__).parents[2]
    tm_directory = main_directory.joinpath('data/template_models')

    template_model_list = []
    for temp_model in tm_directory.glob("*"):
        if '.gitkeep' not in temp_model.name:
            template_model_list.append(temp_model.name)

    for template_model in template_model_list:
        bom_directory = main_directory.joinpath(f'data/template_models/{template_model}/bom')
        prebuilt_scenario_directory = main_directory.joinpath(f'data/template_models/{template_model}/prebuilt_scenarios')
        bom_file_path = \
            [bom_file for bom_file in bom_directory.glob('*') if '.gitkeep' not in bom_file.name]
        assert len(bom_file_path) == 1, 'There should only be one bill of materials \
in bill of materials directory'

        bom_df = gen.read_csv(bom_file_path[0])
        dict_of_scenario_builders = {
            'transportation': sb.TransportationScenarioBuilder(),
            'construction': sb.ConstructionScenarioBuilder(),
            'replacement': sb.ReplacementScenarioBuilder(),
            'end-of-life': sb.EndOfLifeScenarioBuilder()
        }
        for lcs, scenario_builder in dict_of_scenario_builders.items():
            temp_scenario_builder = scenario_builder
            temp_scenario_builder.build_scenarios(bom_df)
            temp_scenario_builder.write_scenarios_to_csv(
                file_path=prebuilt_scenario_directory,
                scenarios_name=f'{template_model}_{lcs}_prebuilt_scenarios'
            )


if __name__ == '__main__':
    build_prebuilt_scenarios()
