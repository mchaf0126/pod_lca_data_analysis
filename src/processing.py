from pathlib import Path
import src.utils.general as gen


def processing():
    """
    Processing of data for the scenario explorer
    """
    main_directory = Path(__file__).parents[1]
    tally_path = main_directory.joinpath('data/raw/tally_commercial_includeBC.csv')
    template_model_directory = main_directory.joinpath('data/processed')
    config_path = main_directory.joinpath('references/config.yml')

    config = gen.read_yaml(config_path)
    assert config is not None, 'The config dictionary could not be set'

    cols_to_drop_list = config.get('cols_to_drop')
    assert cols_to_drop_list is not None, 'The list for columns to drop could not be set'

    template_df = gen.read_csv(tally_path)

    template_df = template_df.drop(columns=cols_to_drop_list)

    template_df['Revit model'] = "Template_Model_1"

    template_df['element_index'] = None
    for row_index in template_df.iterrows():
        template_df.loc[row_index[0], 'element_index'] = f'Element_{row_index[0] // 5}'

    template_df = template_df.set_index('element_index')

    gen.write_to_csv(
        df=template_df,
        write_directory=template_model_directory,
        file_name='Template_Model_1'
    )


if __name__ == '__main__':
    processing()
