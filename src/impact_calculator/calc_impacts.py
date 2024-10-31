from pathlib import Path
import src.utils.general as gen
import src.impact_calculator.ImpactCalculator as ic


def calculate_impacts():
    """
    Implementation of ImpactCalculator for creation of impacts.
    """
    main_directory = Path(__file__).parents[2]
    config_path = main_directory.joinpath('references/impact_config.yml')

    config = gen.read_yaml(config_path)
    assert config is not None, 'The config dictionary could not be set'

    template_model_list = config.get('tme_models')
    assert template_model_list is not None, 'The list of template models could not be set'

    for template_model in template_model_list:
        bom_directory = main_directory.joinpath(f'data/template_models/{template_model}/bom')
        impact_directory = main_directory.joinpath(f'data/template_models/{template_model}/impacts')
        dict_of_impact_calculators = {
            'product': ic.ProductImpactCalculator(),
            'transportation': ic.TransportationImpactCalculator(),
            'replacement': ic.ReplacementImpactCalculator(),
            'end-of-life': ic.EndOfLifeImpactCalculator(),
            'module D': ic.ModuleDImpactCalculator(),
        }
        for lcs, impact_calculator in dict_of_impact_calculators.items():
            temp_calculator = impact_calculator
            temp_calculator.load_bill_of_materials(next(bom_directory.glob('*.csv')))
            temp_calculator.calculate_impacts()
            temp_calculator.write_impacts_to_csv(
                file_path=impact_directory,
                impacts_name=f'{template_model}_{lcs}_impacts'
            )


if __name__ == '__main__':
    calculate_impacts()
