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
    lcs_map: dict = field(init=False)

    def __post_init__(self):
        self.impacts_map = {
            'Global Warming Potential_fossil': 'GWPf',
            'Global Warming Potential_biogenic': 'GWPb',
            'Global Warming Potential_luluc': 'GWP-LULUC',
            'Stored Biogenic Carbon': 'stored_carbon',
            'Acidification Potential': 'acp',
            'Eutrophication Potential': 'eup',
            'Smog Formation Potential': 'smg',
            'Ozone Depletion Potential': 'odp'
        }
        self.lcs_map = {
            'product': 'A1-A3: Product',
            'trans': 'A4: Transportation',
            'constr': 'A5: Construction',
            'repl': 'B2-B5: Replacement',
            'op': 'B6: Operational Energy',
            'eol': 'C2-C4: End-of-life'
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
            life_cycle_stage=self.lcs_map.get('product')
        )

        for impact_name, impact_df_name in self.impacts_map.items():
            self.impacts[impact_name] = \
                self.impacts[impact_df_name + '_mfg'] * self.impacts['Weight (kg)']
            self.impacts.drop(impact_df_name + '_mfg', axis=1, inplace=True)


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
        ).assign(
            life_cycle_stage=self.lcs_map.get('trans')
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

        temp_df = temp_df.drop(
            columns=[
                'Tally dist_truck',
                "Name_Tally Material",
            ]
        )
        self.impacts = temp_df


@dataclass
class ConstructionImpactCalculator(ImpactCalculator):
    """Calculation of construction impacts from WASTAGE ONLY. No construction activities.

    """
    def calculate_impacts(self):

        model_name = self.template_model_name
        main_directory = Path(__file__).parents[2]
        construction_impact_data_file = main_directory.joinpath(
            'references/background_data/a5_wastage.xlsx'
        )
        self.load_background_dataset(construction_impact_data_file)

        a1a3_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_product_impacts.csv'
        )
        a4_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_transportation_impacts.csv'
        )
        c1_c4_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_end-of-life_impacts.csv'
        )

        a1a3_impact_data = gen.read_csv(a1a3_impact_data_file).set_index('element_index')
        a4_impact_data = gen.read_csv(a4_impact_data_file).set_index('element_index')
        c1c4_impact_data = gen.read_csv(c1_c4_impact_data_file).set_index('element_index')

        temp_replacement_df = self.bill_of_materials.copy()
        temp_replacement_df = temp_replacement_df.set_index('Building Material_name')
        temp_replacement_df = temp_replacement_df.merge(
            self.background_dataset,
            left_index=True,
            right_on='Building Material_name',
            how='left',
        ).assign(
            life_cycle_stage=self.lcs_map.get('constr')
        ).set_index('element_index')

        a5_impacts = (
            a1a3_impact_data[list(self.impacts_map.keys())]
            + a4_impact_data[list(self.impacts_map.keys())]
            + c1c4_impact_data[list(self.impacts_map.keys())]
        ).mul(temp_replacement_df['wastage'], axis=0)
        self.impacts = pd.merge(
            left=temp_replacement_df,
            right=a5_impacts,
            left_index=True,
            right_index=True
        ).drop(
            columns=[
                'wastage',
            ]
        ).reset_index()


@dataclass
class ReplacementImpactCalculator(ImpactCalculator):
    """Calculation of replacement impacts from bill of materials. This is a placeholder.

    Attr:
        RSP (int): Reference Study Period
    """
    RSP: int = 60

    def calculate_impacts(self):

        model_name = self.template_model_name
        main_directory = Path(__file__).parents[2]
        replacement_impact_data_file = main_directory.joinpath(
            'references/background_data/b2-b5.xlsx'
        )
        self.load_background_dataset(replacement_impact_data_file)

        a1a3_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_product_impacts.csv'
        )
        a4_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_transportation_impacts.csv'
        )
        a5_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_construction_impacts.csv'
        )
        c1_c4_impact_data_file = main_directory.joinpath(
            f'data/template_models/{model_name}/impacts/{model_name}_end-of-life_impacts.csv'
        )

        a1a3_impact_data = gen.read_csv(a1a3_impact_data_file).set_index('element_index')
        a4_impact_data = gen.read_csv(a4_impact_data_file).set_index('element_index')
        a5_impact_data = gen.read_csv(a5_impact_data_file).set_index('element_index')
        c1c4_impact_data = gen.read_csv(c1_c4_impact_data_file).set_index('element_index')

        temp_replacement_df = self.bill_of_materials.copy()
        temp_replacement_df = temp_replacement_df.set_index('Assembly')
        temp_replacement_df = temp_replacement_df.merge(
            self.background_dataset,
            left_index=True,
            right_on='Assembly',
            how='left',
        ).assign(
            life_cycle_stage=self.lcs_map.get('repl')
        ).set_index('element_index')
        temp_replacement_df['RSP'] = self.RSP
        temp_replacement_df['number_of_replacements'] = (
            temp_replacement_df['RSP']
            // temp_replacement_df['service_lives']
        )
        # handle case where replacement year is 60, same as RSP, but 60 // 60 = 1
        temp_replacement_df.loc[
            temp_replacement_df['service_lives'] == self.RSP,
            'number_of_replacements'
        ] = 0

        b4_impacts = (
            a1a3_impact_data[list(self.impacts_map.keys())]
            + a4_impact_data[list(self.impacts_map.keys())]
            + a5_impact_data[list(self.impacts_map.keys())]
            + c1c4_impact_data[list(self.impacts_map.keys())]
        ).mul(temp_replacement_df['number_of_replacements'], axis=0)
        self.impacts = pd.merge(
            left=temp_replacement_df,
            right=b4_impacts,
            left_index=True,
            right_index=True
        ).drop(
            columns=[
                'service_lives',
                'RSP',
                'number_of_replacements'
            ]
        ).reset_index()


@dataclass
class OperationalImpactCalculator(ImpactCalculator):
    """Calculation of operational energy impacts for project."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials.iloc[:1].copy()
        self.impacts['Omiclass'] = '21-04 50 20'
        self.impacts['L1'] = 'Services'
        self.impacts['L2'] = 'Electrical'
        self.impacts['L3'] = 'Electrical Service and Distribution'
        self.impacts['Option'] = 'OP1'
        self.impacts['Assembly'] = 'Operational energy'
        self.impacts['Component'] = 'Operational energy'
        self.impacts['Building Material_name'] = 'NA'
        self.impacts['life_cycle_stage'] = self.lcs_map.get('op')
        self.impacts['Tally material'] = 'NA'
        self.impacts['Weight (kg)'] = 'NA'
        self.impacts['Data Source (Material Quantities)'] = 'TM'
        self.impacts['Acidification Potential'] = 20301
        self.impacts['Eutrophication Potential'] = 1281
        self.impacts['Smog Formation Potential'] = 245352
        self.impacts['Ozone Depletion Potential'] = 0.0000095
        self.impacts['Global Warming Potential_fossil'] = 6546607
        self.impacts['Global Warming Potential_biogenic'] = 0
        self.impacts['Global Warming Potential_luluc'] = 0
        self.impacts['Stored Biogenic Carbon'] = 0


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
            life_cycle_stage=self.lcs_map.get('eol')
        )

        for impact_name, impact_df_name in self.impacts_map.items():
            self.impacts[impact_name] = \
                self.impacts[impact_df_name + '_eol'] * self.impacts['Weight (kg)']
            self.impacts.drop(impact_df_name + '_eol', axis=1, inplace=True)


@dataclass
class ModuleDImpactCalculator(ImpactCalculator):
    """Calculation of Module D impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials


if __name__ == '__main__':
    pass
