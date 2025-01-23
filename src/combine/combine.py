from pathlib import Path
import pandas as pd
import src.utils.general as gen


def create_data_for_frontend():
    """
    Implementation of TemplateModelExtractor for creation of bill of materials.
    """
    main_directory = Path(__file__).parents[2]
    tm_directory = main_directory.joinpath('data/template_models')
    frontend_directory = main_directory.joinpath('data/frontend')

    template_model_list = []
    for temp_model in tm_directory.glob("*"):
        if '.gitkeep' not in temp_model.name:
            template_model_list.append(temp_model.name)

    bill_of_materials_to_combine = []
    impacts_to_combine = []
    prebuilt_scenarios_to_combine = []

    lists_for_combining = {
        'bill_of_materials_to_combine': bill_of_materials_to_combine,
        'impacts_to_combine': impacts_to_combine,
        'prebuilt_scenarios_to_combine': prebuilt_scenarios_to_combine
    }

    for template_model in template_model_list:
        directories_per_tm = {
            'bill_of_materials_to_combine': main_directory.joinpath(f'data/template_models/{template_model}/bom'),
            'impacts_to_combine': main_directory.joinpath(f'data/template_models/{template_model}/impacts'),
            'prebuilt_scenarios_to_combine': main_directory.joinpath(f'data/template_models/{template_model}/prebuilt_scenarios')
        }

        for list_for_dfs, directory in directories_per_tm.items():
            for file in directory.glob("*.csv"):
                temp_df = gen.read_csv(file)
                temp_df = temp_df.set_index('element_index')
                temp_df['template_model'] = template_model
                lists_for_combining.get(list_for_dfs).append(temp_df)

    combined_bom = pd.concat(bill_of_materials_to_combine)
    combined_impacts = pd.concat(impacts_to_combine)
    combined_prebuilt_scenarios = pd.concat(prebuilt_scenarios_to_combine)

    files_to_write = {
        'combined_bom': combined_bom,
        'combined_impacts': combined_impacts,
        'combined_prebuilt_scenarios': combined_prebuilt_scenarios
    }

    for name, df in files_to_write.items():
        gen.write_to_pickle(
            df=df,
            write_directory=frontend_directory,
            file_name=name
        )


if __name__ == '__main__':
    create_data_for_frontend()
