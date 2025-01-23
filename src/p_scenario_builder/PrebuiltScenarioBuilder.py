# from pathlib import Path
from dataclasses import dataclass
from pathlib import Path
import src.impact_calculator.ImpactCalculator as ic


@dataclass
class TransportationScenarioBuilder(ic.TransportationImpactCalculator):
    """Methods for creating a prebuilt scenario"""
    def calculate_impacts(self):
        # emission = mass of product * emission factor * distance * return factor
        # implements rail and truck 
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
        rail_emissions_name = 'Transport, train, diesel powered'
        truck_distance_column = 'R dist CA_truck'
        rail_distance_column = 'R dist CA dist_rail'

        trans_emissions = self.background_dataset.set_index('Product system name')
        truck_distances = self.background_distances[
            ['Name_Tally Material', truck_distance_column]
        ]
        rail_distances = self.background_distances[
            ['Name_Tally Material', rail_distance_column]
        ]
        # emission = mass of product * emission factor * distance * return factor
        temp_df = self.bill_of_materials.merge(
            truck_distances,
            left_on='Tally material',
            right_on='Name_Tally Material',
            how='left'
        ).merge(
            rail_distances,
            left_on='Tally material',
            right_on='Name_Tally Material',
            how='left'
        ).assign(
            life_cycle_stage=self.lcs_map.get('trans'),
            scenario='Regionally-Specific Distances'
        )

        for name, col_name in self.impacts_map.items():
            # emission = mass of product * emission factor * distance
            temp_df[f'{name}_truck'] = (
                (temp_df['Weight (kg)'] / 1000)
                * trans_emissions.loc[truck_emissions_name, col_name]
                * (temp_df[truck_distance_column] * mi_to_km_conversion)
            )

            # if distance is greater than 500 mi, then return factor = 1.5
            temp_df.loc[temp_df[truck_distance_column] > 500, f'{name}_truck'] = (
                1.5
                * (temp_df['Weight (kg)'] / 1000)
                * trans_emissions.loc[truck_emissions_name, col_name]
                * (temp_df[truck_distance_column] * mi_to_km_conversion)
            )

            # emission = mass of product * emission factor * distance
            temp_df[f'{name}_rail'] = (
                (temp_df['Weight (kg)'] / 1000)
                * trans_emissions.loc[rail_emissions_name, col_name]
                * (temp_df[rail_distance_column] * mi_to_km_conversion)
            )

            # if distance is greater than 500 mi, then return factor = 1.5
            temp_df.loc[temp_df[rail_distance_column] > 500, f'{name}_truck'] = (
                1.5
                * (temp_df['Weight (kg)'] / 1000)
                * trans_emissions.loc[rail_emissions_name, col_name]
                * (temp_df[rail_distance_column] * mi_to_km_conversion)
            )

            temp_df[name] = temp_df[f'{name}_truck'] + temp_df[f'{name}_rail']

        temp_df = temp_df.drop(
            columns=[
                'Name_Tally Material_x',
                'R dist CA_truck',
                'Name_Tally Material_y',
                'R dist CA dist_rail',
                'Global Warming Potential_fossil_truck',
                'Global Warming Potential_fossil_rail',
                'Global Warming Potential_biogenic_truck',
                'Global Warming Potential_biogenic_rail',
                'Global Warming Potential_luluc_truck',
                'Global Warming Potential_luluc_rail',
                'Acidification Potential_truck',
                'Acidification Potential_rail',
                'Eutrophication Potential_truck',
                'Eutrophication Potential_rail',
                'Smog Formation Potential_truck',
                'Smog Formation Potential_rail',
                'Ozone Depletion Potential_truck',
                'Ozone Depletion Potential_rail',
                'Ozone Depletion Potential',
            ]
        )
        self.impacts = temp_df


# @dataclass
# class ConstructionScenarioBuilder(PrebuiltScenarioBuilder):
#     """Methods for creating a prebuilt scenario"""
#     # attributes

#     # methods


# @dataclass
# class ReplacementScenarioBuilder(PrebuiltScenarioBuilder):
#     """Methods for creating a prebuilt scenario"""
#     # attributes

#     # methods


# @dataclass
# class EndOfLifeScenarioBuilder(PrebuiltScenarioBuilder):
#     """Methods for creating a prebuilt scenario"""
#     # attributes

#     # methods
