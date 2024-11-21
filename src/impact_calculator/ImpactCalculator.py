from dataclasses import dataclass, field
from abc import abstractmethod
from pathlib import Path
import numpy as np
import pandas as pd
import src.utils.general as gen


@dataclass
class ImpactCalculator:
    """Abstract class for impact calculators."""
    template_model_name: str
    bill_of_materials: pd.DataFrame = field(default=None)
    background_dataset: pd.DataFrame = field(default=None)
    impacts: pd.DataFrame = field(default=None)

    def load_bill_of_materials(self) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        # find bom directory
        main_directory = Path(__file__).parents[2]
        bom_directory = main_directory.joinpath(
            f'data/template_models/{self.template_model_name}/bom'
        )

        # find file path, assuming only one BOM in each template model folder
        bom_file_path = \
            [bom_file for bom_file in bom_directory.glob('*') if '.gitkeep' not in bom_file.name]
        assert len(bom_file_path) == 1, 'There should only be one bill of materials \
in bill of materials directory'
        # read bom file
        bom_df = gen.read_csv(bom_file_path[0])
        self.bill_of_materials = bom_df

    def load_background_dataset(self, file_path: Path) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        background_df = gen.read_csv(file_path)
        self.background_dataset = background_df

    @abstractmethod
    def calculate_impacts(self):
        """Abstract method for calculating impacts."""

    def write_impacts_to_csv(self, file_path: Path, impacts_name: str) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        df_to_write = self.impacts
        df_to_write = df_to_write.set_index('element_index')
        gen.write_to_csv(
            df=df_to_write,
            write_directory=file_path,
            file_name=impacts_name
        )


@dataclass
class ProductImpactCalculator(ImpactCalculator):
    """Calculation of product impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials[
            self.bill_of_materials['Life Cycle Stage'] == "[A1-A3] Product"
        ]


@dataclass
class TransportationImpactCalculator(ImpactCalculator):
    """Calculation of transportation impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials[
            self.bill_of_materials['Life Cycle Stage'] == "[A4] Transportation"
        ]


@dataclass
class ReplacementImpactCalculator(ImpactCalculator):
    """Calculation of replacement impacts from bill of materials. This is a placeholder.

    Attr:
        RSP (int): Reference Study Period
    """
    RSP: int = 60

    def calculate_impacts(self):

        #TODO: test once all other impact calculators are merged

        model_name = self.bill_of_materials['Revit model'].unique()[0]

        main_directory = Path(__file__).parents[2]
        a1a3_impact_data_file = main_directory.joinpath(f'data/template_models/{model_name}/impacts/{model_name}_product_impacts.csv')
        a4_impact_data_file = main_directory.joinpath(f'data/template_models/{model_name}/impacts/{model_name}_transportation_impacts.csv')
        a5_impact_data_file = main_directory.joinpath(f'data/template_models/{model_name}/impacts/{model_name}_construction_impacts.csv')
        c1_c4_impact_data_file = main_directory.joinpath(f'data/template_models/{model_name}/impacts/{model_name}_end-of-life_impacts.csv')
        d_impact_data_file = main_directory.joinpath(f'data/template_models/{model_name}/impacts/{model_name}_module D_impacts.csv')

        a1a3_impact_data = gen.read_csv(a1a3_impact_data_file)
        a4_impact_data = gen.read_csv(a4_impact_data_file)
        # a5_impact_data = gen.read_csv(a5_impact_data_file)
        c1c4_impact_data = gen.read_csv(c1_c4_impact_data_file)
        d_impact_data = gen.read_csv(d_impact_data_file)

        impacts_categories= ['Global Warming Potential_fossil', 
                             'Global Warming Potential_biogenic', 
                             'Global Warming Potential_luluc', 
                             'Acidification Potential',
                             'Eutrophication Potential',
                             'Smog Formation Potential'
                             'Ozone Depletion Potential']
        impact_lst = []
        for index, row in self.bill_of_materials.iterrows():
            element_index = row['element_index']
            material_name = row['Material Name']
            service_life = row['Service Life']        
            no_of_replacements = np.ceil(self.RSP / service_life) - 1
            if no_of_replacements == 0:
                new_entry = {'element_index': element_index} | {key: 0.0 for key in impacts_categories}
            else:
                new_entry = {'Material Name': material_name, 'element_index': element_index}
                for impact_category in impacts_categories:
                    new_entry[impact_category] = (a1a3_impact_data[a1a3_impact_data['element_index'] == element_index].iloc[0][impact_category] + 
                                        a4_impact_data[a4_impact_data['element_index'] == element_index].iloc[0][impact_category] + 
                                        # a5_impact_data[a5_impact_data['element_index'] == element_index].iloc[0][impact_category] +
                                        c1c4_impact_data[c1c4_impact_data['element_index'] == element_index].iloc[0][impact_category] +
                                        d_impact_data[d_impact_data['element_index'] == element_index].iloc[0][impact_category]) * no_of_replacements          

            impact_lst.append(new_entry)

        impacts_tmp = pd.DataFrame(impact_lst, columns=['element_index'] + impacts_categories)
        self.impacts = pd.merge(self.bill_of_materials, impacts_tmp, on='element_index', how='outer')

        return self.impacts
    

@dataclass
class EndOfLifeImpactCalculator(ImpactCalculator):
    """Calculation of end-of-life impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):



        self.impacts = self.bill_of_materials[
            self.bill_of_materials['Life Cycle Stage'] == "[C2-C4] End of Life"
        ]


@dataclass
class ModuleDImpactCalculator(ImpactCalculator):
    """Calculation of Module D impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials[
            self.bill_of_materials['Life Cycle Stage'] == "[D] Module D"
        ]
