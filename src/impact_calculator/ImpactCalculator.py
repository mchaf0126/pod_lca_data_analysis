"""Definition of classes for calculation of environmental impacts."""
from dataclasses import dataclass, field
from abc import abstractmethod
from pathlib import Path
import pandas as pd
import src.utils.general as gen


@dataclass
class ImpactCalculator:
    """Abstract class for impact calculators."""
    template_model_name: str
    bill_of_materials: pd.DataFrame = field(default=None)
    background_dataset: pd.DataFrame = field(default=None)
    impacts: pd.DataFrame = field(default=None)
    impacts_map: dict = field(init=False)

    def __post_init__(self):
        self.impacts_map = {
            'Global Warming Potential_fossil': 'GWPf',
            'Global Warming Potential_biogenic': 'GWPb',
            'Global Warming Potential_luluc': 'GWP-LULUC',
            'Acidification Potential': 'acp',
            'Eutrophication Potential': 'eup',
            'Smog Formation Potential': 'smg',
            'Ozone Depletion Potential': 'odp'
        }

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
        background_df = gen.read_excel(file_path)
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
        product_impact_data_file = main_directory.joinpath('references/background_data/a1-a3.xlsx')
        self.load_background_dataset(product_impact_data_file)

        self.impacts = pd.merge(
            self.bill_of_materials,
            self.background_dataset[['Name_Tally Material'] + [impact_cat + '_mfg' for impact_cat in self.impacts_map.values()]],
            left_on='Tally material',
            right_on='Name_Tally Material',
            how='left'
        ).drop(
            "Name_Tally Material",
            axis=1
        ).assign(
            life_cycle_stage="Product: A1-A3"
        )

        for impact_name, impact_df_name in self.impacts_map.items():
            self.impacts[impact_name] = \
                self.impacts[impact_df_name + '_mfg'] * self.impacts['Weight (kg)']
            self.impacts.drop(impact_df_name + '_mfg', axis=1, inplace=True)

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

        main_directory = Path(__file__).parents[2]
        EOL_impact_data_file = main_directory.joinpath('references/background_data/c2-c4.xlsx')
        self.load_background_dataset(EOL_impact_data_file)

        self.impacts = pd.merge(
            self.bill_of_materials,
            self.background_dataset[['Name_Tally Material'] + [impact_cat + '_eol' for impact_cat in self.impacts_map.values()]],
            left_on='Tally material',
            right_on='Name_Tally Materialc',
            how='left'
        ).drop(
            "Name_Tally Material",
            axis=1
        )

        for impact_name, impact_df_name in self.impacts_map.items():
            self.impacts[impact_name] = \
                self.impacts[impact_df_name + '_eol'] * self.impacts['Weight (kg)']
            self.impacts.drop(impact_df_name + '_eol', axis=1, inplace=True)

        return self.impacts


@dataclass
class ModuleDImpactCalculator(ImpactCalculator):
    """Calculation of Module D impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials


if __name__ == '__main__':
    pass
