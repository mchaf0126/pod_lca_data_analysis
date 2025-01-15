from pathlib import Path
from dataclasses import dataclass
import pandas as pd
import src.utils.general as gen


@dataclass
class TemplateModelExtractor:
    """Methods for extracting bill of materials from template model"""
    all_str_bom: pd.DataFrame = None
    all_enc_o_bom: pd.DataFrame = None
    all_enc_t_bom: pd.DataFrame = None
    all_enc_r_bom: pd.DataFrame = None
    t_model_df: pd.DataFrame = None

    def load_template_model(self, file_path: Path) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        self.all_str_bom = pd.read_excel(file_path, sheet_name='Structure')
        self.all_enc_o_bom = pd.read_excel(file_path, sheet_name='Enclosure - Opaque')
        self.all_enc_t_bom = pd.read_excel(file_path, sheet_name='Enclosure - Translucent')
        self.all_enc_r_bom = pd.read_excel(file_path, sheet_name='Enclosure - Roofing')

    def create_bill_of_materials(self, template_model_name: str) -> None:
        """_summary_

        Args:
            cols_to_drop_list (list): _description_
        """
        template_model_name_split = template_model_name.split('_')

        str_bom_option_name = template_model_name_split[0]
        enc_o_option_name = template_model_name_split[1]
        enc_t_option_name = template_model_name_split[2]
        enc_r_option_name = template_model_name_split[3]

        str_bom_option = self.all_str_bom[self.all_str_bom['Option'] == str_bom_option_name]
        enc_o_bom_option = self.all_enc_o_bom[self.all_enc_o_bom['Option'] == enc_o_option_name]
        enc_t_bom_option = self.all_enc_t_bom[self.all_enc_t_bom['Option'] == enc_t_option_name]
        enc_r_bom_option = self.all_enc_r_bom[self.all_enc_r_bom['Option'] == enc_r_option_name]

        template_model_bom = pd.concat(
            [
                str_bom_option,
                enc_o_bom_option,
                enc_t_bom_option,
                enc_r_bom_option
            ]
        )

        template_model_bom['element_index'] = None
        template_model_bom.reset_index(inplace=True)
        for row_index in template_model_bom.iterrows():
            template_model_bom.loc[row_index[0], 'element_index'] = f'Element_{row_index[0]}'

        template_model_bom = template_model_bom.set_index('element_index')

        self.t_model_df = template_model_bom

    def write_bill_of_materials(self, file_path: Path, bill_of_materials_name: str) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        df_to_write = self.t_model_df
        gen.write_to_csv(
            df=df_to_write,
            write_directory=file_path,
            file_name=bill_of_materials_name
        )
