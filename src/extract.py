from pathlib import Path
import src.utils.general as gen
from src.TemplateModelExtractor import TemplateModelExtractor


def create_bill_of_materials():
    """
    Implementation of TemplateModelExtractor for creation of bill of materials.
    """
    main_directory = Path(__file__).parents[1]
    config_path = main_directory.joinpath('references/extract_config.yml')

    config = gen.read_yaml(config_path)
    assert config is not None, 'The config dictionary could not be set'

    template_model_list = config.get('tme_models')
    assert template_model_list is not None, 'The list of template models could not be set'

    cols_to_drop_list = config.get('cols_to_drop')
    assert cols_to_drop_list is not None, 'The list for columns to drop could not be set'

    for template_model in template_model_list:
        tm_directory = main_directory.joinpath(f'data/template_models/{template_model}/raw')
        bom_directory = main_directory.joinpath(f'data/template_models/{template_model}/bom')
        Extractor = TemplateModelExtractor()
        Extractor.load_template_model(
            file_path=next(tm_directory.glob('*.csv'))
        )
        Extractor.create_bill_of_materials(
            cols_to_drop_list=cols_to_drop_list
        )
        Extractor.write_bill_of_materials(
            bom_directory,
            f'{template_model}_bom'
        )


if __name__ == '__main__':
    create_bill_of_materials()
