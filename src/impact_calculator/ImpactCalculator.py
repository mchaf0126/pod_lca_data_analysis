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
    """Calculation of transportation impacts from bill of materials."""
    background_distances: pd.DataFrame = field(default=None)

    def load_background_distances(self, file_path: Path) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        background_df = gen.read_excel(file_path)
        self.background_distances = background_df

    def calculate_impacts(self):
        # emission = mass of product * emission factor * distance * return factor
        # currently only does truck transport, but this can be fixed in the future.
        # It is a straightforward calc, it just requires a lot of complicated
        # combinations that are not worth the time for current 0's.
        main_directory = Path(__file__).parents[2]
        transporation_emissions_file = main_directory.joinpath(
            'references/background_data/a4_emissions.xlsx'
        )
        transportation_distances_file = main_directory.joinpath(
            'references/background_data/a4_distances.xlsx'
        )

        self.load_background_dataset(transporation_emissions_file)
        self.load_background_distances(transportation_distances_file)
        mi_to_km_conversion = 1.60934

        truck_emissions_name = 'Transport, combination truck, average fuel mix'
        truck_distance_column = 'Tally dist_truck'

        trans_emissions = self.background_dataset.set_index('Product system name')
        trans_distances = self.background_distances[
            ['Name_Tally Material', truck_distance_column]
        ]
        # emission = mass of product * emission factor * distance * return factor
        temp_df = self.bill_of_materials.merge(
            trans_distances,
            left_on='Tally material',
            right_on='Name_Tally Material',
            how='left'
        ).drop(
            "Name_Tally Material",
            axis=1
        ).assign(
            life_cycle_stage="Transportation: A4"
        )

        for name, col_name in self.impacts_map.items():
            # emission = mass of product * emission factor * distance
            temp_df[name] = (
                (temp_df['Weight (kg)'] / 1000)
                * trans_emissions.loc[truck_emissions_name, col_name]
                * (temp_df[truck_distance_column] * mi_to_km_conversion)
            )

            # if distance is greater than 500 mi, then return factor = 1.5
            temp_df.loc[temp_df[truck_distance_column] > 500, name] = (
                1.5
                * (temp_df['Weight (kg)'] / 1000)
                * trans_emissions.loc[truck_emissions_name, col_name]
                * (temp_df[truck_distance_column] * mi_to_km_conversion)
            )

        self.impacts = temp_df


@dataclass
class ReplacementImpactCalculator(ImpactCalculator):
    """Calculation of replacement impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials


@dataclass
class EndOfLifeImpactCalculator(ImpactCalculator):
    """Calculation of end-of-life impacts from bill of materials."""
    def calculate_impacts(self):

        main_directory = Path(__file__).parents[2]
        eol_impact_data_file = main_directory.joinpath('references/background_data/c2-c4.xlsx')
        self.load_background_dataset(eol_impact_data_file)

        self.impacts = pd.merge(
            self.bill_of_materials,
            self.background_dataset[['Name_Tally Material'] + [impact_cat + '_eol' for impact_cat in self.impacts_map.values()]],
            left_on='Tally material',
            right_on='Name_Tally Material',
            how='left'
        ).drop(
            "Name_Tally Material",
            axis=1
        ).assign(
            life_cycle_stage="End-of-life: C2-C4"
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
