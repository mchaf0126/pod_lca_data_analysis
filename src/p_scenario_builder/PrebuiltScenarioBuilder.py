from pathlib import Path
from dataclasses import dataclass
import pandas as pd
# import src.utils.general as gen


@dataclass
class PrebuiltScenarioBuilder:
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


@dataclass
class TransportationScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    
    def __init__(self, module_folder_path, templatemodel_path):
        self.module_folder_path = module_folder_path
        self.templatemodel_path = templatemodel_path
        self.dfs = {}
        self.tem_df = None
        self.final_df = None

    def load_data(self):
        # Load CSV files in module folder and store them as dataframes in self.dfs dictionary
        for file in sorted(os.listdir(self.module_folder_path)):
            if file.endswith(".csv"):
                file_path = os.path.join(self.module_folder_path, file)
                df = pd.read_csv(file_path)
                df_name = os.path.splitext(file)[0]
                self.dfs[df_name] = df
        # Load the template model CSV file
        self.tem_df = pd.read_csv(self.templatemodel_path)

    def prepare_data(self):
        # Prepare data for merging and calculations
        trans_mass = self.tem_df[self.tem_df['Life Cycle Stage'] == '[A1-A3] Product']
        trans_mass = trans_mass[['element_index', 'Material Group', 'Mass Total (kg)']]
        dfs_keys = list(self.dfs.keys())

        # Unpack required dataframes in alphabetical order based on file names
        self.distances, self.mode_scenario, self.modes, self.scenarios, self.stg_code, self.trans_mode = (
            self.dfs[dfs_keys[i]] for i in range(len(dfs_keys))
        )

        # Merge dataframes to prepare for calculations
        self.mass = trans_mass.merge(self.stg_code, how='right', left_on='Material Group', right_on='material_id').drop(columns='material_id')
        self.mode_scenario_df = self.mode_scenario.merge(self.modes, left_on='mode_id', right_on='id', suffixes=(None, '_mode')).merge(
            self.scenarios, left_on='scenario_id', right_on='id', suffixes=(None, '_scenario')
        )
        self.mode_scenario_df = self.mode_scenario_df[['id', 'name', 'name_scenario']].rename(
            columns={'name': 'mode_name', 'name_scenario': 'scenario_name'}
        )

        self.trans_mode_df = self.trans_mode.merge(self.mode_scenario_df, left_on='mode_scenario_id', right_on='id', suffixes=(None, '_mode_scenario'))
        self.trans_mode_df = self.trans_mode_df[['mode_scenario_id', 'return_trip_factor', 'gwp', 'mode_name', 'scenario_name']]

        self.mass_distance = self.mass.merge(self.distances, how='left', on='stg_code')
        self.final_df = self.mass_distance.merge(self.trans_mode_df, on='mode_scenario_id').drop(columns=['id', 'mode_scenario_id', 'reference'])

    def calculate_transportation_impact(self):
        # Perform calculation to obtain the total transportation impact (total_a4)
        self.final_df = self.final_df.assign(
            total_a4=self.final_df['Mass Total (kg)'] * self.final_df['distance'] * self.final_df['gwp'] * self.final_df['return_trip_factor']
        )
        return self.final_df

    def run(self):
        self.load_data()
        self.prepare_data()
        return self.calculate_transportation_impact()


@dataclass
class ConstructionScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


@dataclass
class ReplacementScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


@dataclass
class EndOfLifeScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods
