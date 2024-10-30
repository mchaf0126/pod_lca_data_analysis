from pathlib import Path
from dataclasses import dataclass
import pandas as pd
import src.utils.general as gen


@dataclass
class TemplateModelExtractor():
    """Methods for extracting bill of materials from template model"""
    t_model_df: pd.DataFrame = None

    def load_template_model(self, file_path: Path) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        template_df = gen.read_csv(file_path)
        self.t_model_df = template_df

    def create_bill_of_materials(self, cols_to_drop_list: list) -> None:
        """_summary_

        Args:
            cols_to_drop_list (list): _description_
        """
        template_df = self.t_model_df

        template_df['Revit model'] = "Template_Model_1"

        template_df['element_index'] = None
        for row_index in template_df.iterrows():
            template_df.loc[row_index[0], 'element_index'] = f'Element_{row_index[0] // 5}'

        template_df = template_df.set_index('element_index')

        template_df = template_df.drop(columns=cols_to_drop_list)

        self.t_model_df = template_df

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
