from pathlib import Path
import src.impact_calculator.ImpactCalculator as ic


def calculate_impacts():
    """
    Implementation of ImpactCalculator for creation of impacts.
    """
    main_directory = Path(__file__).parents[2]
    tm_directory = main_directory.joinpath('data/template_models')

    template_model_list = []
    for temp_model in tm_directory.glob("*"):
        if '.gitkeep' not in temp_model.name:
            template_model_list.append(temp_model.name)

    for template_model in template_model_list:
        bom_directory = main_directory.joinpath(f'data/template_models/{template_model}/bom')
        impact_directory = main_directory.joinpath(f'data/template_models/{template_model}/impacts')
        bom_file_path = \
            [bom_file for bom_file in bom_directory.glob('*') if '.gitkeep' not in bom_file.name]
        assert len(bom_file_path) == 1, 'There should only be one bill of materials \
in bill of materials directory'

        dict_of_impact_calculators = {
            'product': ic.ProductImpactCalculator(),
            'transportation': ic.TransportationImpactCalculator(),
            'replacement': ic.ReplacementImpactCalculator(),
            'end-of-life': ic.EndOfLifeImpactCalculator(),
            'module D': ic.ModuleDImpactCalculator(),
        }
        for lcs, impact_calculator in dict_of_impact_calculators.items():
            temp_calculator = impact_calculator
            temp_calculator.load_bill_of_materials(bom_file_path[0])
            temp_calculator.calculate_impacts()
            temp_calculator.write_impacts_to_csv(
                file_path=impact_directory,
                impacts_name=f'{template_model}_{lcs}_impacts'
            )


if __name__ == '__main__':
    calculate_impacts()
