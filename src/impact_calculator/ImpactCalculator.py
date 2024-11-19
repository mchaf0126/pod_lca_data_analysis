from dataclasses import dataclass, field
from abc import abstractmethod
from pathlib import Path
import pandas as pd
import src.utils.general as gen


@dataclass
class ImpactCalculator:
    """Abstract class for impact calculators."""
    bill_of_materials: pd.DataFrame = field(default=None)
    background_dataset: pd.DataFrame = field(default=None)
    impacts: pd.DataFrame = field(default=None)

    def load_bill_of_materials(self, file_path: Path) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        bom_df = gen.read_csv(file_path)
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
    """Calculation of product impacts from bill of materials."""
    def calculate_impacts(self):

        main_directory = Path(__file__).parents[2]
        product_impact_data_file = main_directory.joinpath('references/background_data/a1-a3.csv')
        self.load_background_dataset(product_impact_data_file)


        impacts_map = {'Global Warming Potential_fossil': 'GWPf_mfg',
                       'Global Warming Potential_biogenic': 'GWPb_mfg',
                       'Global Warming Potential_luluc': 'GWP-LULUC',
                       'Acidification Potential': 'acp_mfg',
                       'Eutrophication Potential': 'eup_mfg',
                       'Smog Formation Potential': 'smg_mfg',
                       'Ozone Depletion Potential': 'odp_mfg'}
        impact_lst = []
        for index, row in self.bill_of_materials.iterrows():
            element_index = row['element_index']
            material_name = row['Material Name']
            mass = row['Mass Total (kg)']
            new_entry = {'element_index': element_index}
            for key, value in impacts_map.items():
                try:
                    unit_impact = self.background_dataset[self.background_dataset['Name_generic'] == material_name].iloc[0][value]
                except IndexError as e:
                    print(f"{material_name} not in background dataset.")
                    break
                new_entry[key] = mass * unit_impact
            impact_lst.append(new_entry)
        
        impacts_tmp = pd.DataFrame(impact_lst, columns=['element_index'] + list(impacts_map.keys()))
        self.impacts = pd.merge(self.bill_of_materials, impacts_tmp, on='element_index', how='outer')

        return self.impacts


@dataclass
class TransportationImpactCalculator(ImpactCalculator):
    """Calculation of transportation impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials


@dataclass
class ReplacementImpactCalculator(ImpactCalculator):
    """Calculation of replacement impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials


@dataclass
class EndOfLifeImpactCalculator(ImpactCalculator):
    """Calculation of end-of-life impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials


@dataclass
class ModuleDImpactCalculator(ImpactCalculator):
    """Calculation of Module D impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials

if __name__ == '__main__':
    pass