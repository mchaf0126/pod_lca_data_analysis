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
        impact_directory = tm_directory.joinpath(f'{template_model}/impacts')
        dict_of_impact_calculators = {
            'product': ic.ProductImpactCalculator(template_model),
            'transportation': ic.TransportationImpactCalculator(template_model),
            'replacement': ic.ReplacementImpactCalculator(template_model),
            'operational': ic.OperationalImpactCalculator(template_model),
            'end-of-life': ic.EndOfLifeImpactCalculator(template_model),
            # 'module D': ic.ModuleDImpactCalculator(template_model),
        }

        for lcs, impact_calculator in dict_of_impact_calculators.items():
            temp_calculator = impact_calculator
            temp_calculator.load_bill_of_materials()
            temp_calculator.calculate_impacts()
            temp_calculator.write_impacts_to_csv(
                file_path=impact_directory,
                impacts_name=f'{template_model}_{lcs}_impacts'
            )


if __name__ == '__main__':
    calculate_impacts()
