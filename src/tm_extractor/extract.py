from pathlib import Path
from src.tm_extractor.TemplateModelExtractor import TemplateModelExtractor


def create_bill_of_materials():
    """
    Implementation of TemplateModelExtractor for creation of bill of materials.
    """
    main_directory = Path(__file__).parents[2]
    tm_directory = main_directory.joinpath('data/template_models')
    raw_bom_path = main_directory.joinpath('data/raw/raw_boms.xlsx')

    template_model_list = []
    for temp_model in tm_directory.glob("*"):
        if '.gitkeep' not in temp_model.name:
            template_model_list.append(temp_model.name)

    for template_model in template_model_list:
        bom_directory = main_directory.joinpath(f'data/template_models/{template_model}/bom')

        Extractor = TemplateModelExtractor()
        Extractor.load_template_model(
            file_path=raw_bom_path
        )
        Extractor.create_bill_of_materials(
            template_model_name=template_model
        )
        Extractor.write_bill_of_materials(
            bom_directory,
            f'{template_model}_bom'
        )


if __name__ == '__main__':
    create_bill_of_materials()
