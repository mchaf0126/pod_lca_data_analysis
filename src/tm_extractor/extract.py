from pathlib import Path
import src.utils.general as gen
from src.tm_extractor.TemplateModelExtractor import TemplateModelExtractor


def create_bill_of_materials():
    """
    Implementation of TemplateModelExtractor for creation of bill of materials.
    """
    main_directory = Path(__file__).parents[2]
    config_path = main_directory.joinpath('references/extract_config.yml')

    config = gen.read_yaml(config_path)
    assert config is not None, 'The config dictionary could not be set'

    cols_to_drop_list = config.get('cols_to_drop')
    assert cols_to_drop_list is not None, 'The list for columns to drop could not be set'

    tm_directory = main_directory.joinpath('data/template_models')

    template_model_list = []
    for temp_model in tm_directory.glob("*"):
        if '.gitkeep' not in temp_model.name:
            template_model_list.append(temp_model.name)

    for template_model in template_model_list:
        raw_directory = main_directory.joinpath(f'data/template_models/{template_model}/raw')
        bom_directory = main_directory.joinpath(f'data/template_models/{template_model}/bom')

        raw_file_path = \
            [raw_file for raw_file in raw_directory.glob('*') if '.gitkeep' not in raw_file.name]
        assert len(raw_file_path) == 1, 'There should only be one raw file in raw file directory'

        Extractor = TemplateModelExtractor()
        Extractor.load_template_model(
            file_path=raw_file_path[0]
        )
        Extractor.create_bill_of_materials(
            cols_to_drop_list=cols_to_drop_list,
            template_model_name=template_model
        )
        Extractor.write_bill_of_materials(
            bom_directory,
            f'{template_model}_bom'
        )


if __name__ == '__main__':
    create_bill_of_materials()
