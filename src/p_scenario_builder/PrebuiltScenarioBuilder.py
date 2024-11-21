from pathlib import Path
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import src.utils.general as gen
from typing import List, Type

import src.impact_calculator.ImpactCalculator as ic

class ScenarioTrackerMixin(type):
    """ Tracker for all scenarios defined"""
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.scenarios = []
        for base in bases:
            if hasattr(base, "scenarios"):
                base.scenarios.append(cls)


class PrebuiltScenarioBuilder(metaclass=ScenarioTrackerMixin):
    """Methods for creating a prebuilt scenario"""
    # attributes
    def __init__(self) -> None:
        self.scenario_impacts = None
       
    def build_scenarios(self, bill_of_materials):
        pass

    def write_scenarios_to_csv(self, file_path: Path, scenarios_name: str) -> None:
        """_summary_

        Args:
            file_path (Path): _description_
        """
        # TODO: uncomment when ready
        # df_to_write = self.scenario_impacts
        # df_to_write = df_to_write.set_index('element_index')
        # gen.write_to_csv(
        #     df=df_to_write,
        #     write_directory=file_path,
        #     file_name=scenarios_name
        # )
        pass


class TransportationScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


class ConstructionScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


class ReplacementScenarioBuilder(PrebuiltScenarioBuilder):
    """
    Methods for creating replacement scenarios.
    See: https://docs.google.com/document/d/1U98-ywdp16ldmXZG7rqztwkpHnKCkLEVUq2V_0_gNNk/edit?usp=sharing
         https://docs.google.com/document/d/1d9ZtZbSrMXGaN7rMRNjzVAoSHPShybrjESpL6ZFL88A/edit?usp=sharing

    """

    def import_data(data_folder):
        """ Import replacement data: service life, and mappings to template model where necessary.
        """

        pass


    def map_service_life(bill_of_materials, service_life, mapper):
        """ Map service life from the replacement scenario to the model.
            Updates the model data with service life.

            Parameters
            ----------
            bill_of_materials : df.
                Bill of material for the model.
            service_life : df.
                Table with columns 'id', 'material', 'service life'.
            mapper : df.
                Table mapping 'Material Name', 'Revit category' in template model to 'material', 'assembly' in the service_life table

            Returns
            -------
            TemplateModel Obj.
                Model with updated data on service life.  
        """


        material_to_service_life = pd.merge(mapper[['material', 'assembly', 'type']], service_life[['type', 'Service Life']], 
                                            on='type', 
                                            how='left').drop(columns=['type'])
        BOM_with_service_life = pd.merge(bill_of_materials, material_to_service_life, 
                                         left_on=['Material Name', 'Revit category'], 
                                         right_on=['material', 'assembly'], 
                                         how='left').drop(columns=['material'])

        return BOM_with_service_life
    
    def build_scenarios(self, bill_of_materials):

        for replacement_scenario in self.scenarios:

            main_directory = Path(__file__).parents[2]
            background_data_folder = main_directory.joinpath('references/background_data')

            mapper, service_life = replacement_scenario.import_data(background_data_folder)
            bill_of_materials_updated = replacement_scenario.map_service_life(bill_of_materials, service_life, mapper)

            replacement_calculator = ic.ReplacementImpactCalculator()
            replacement_calculator.bill_of_materials = bill_of_materials_updated
            b4_impacts = replacement_calculator.calculate_impacts()
            #TODO: complete RICS mapping
            #TODO: label and write data
            #TODO: test ASHRAE mapper stuff

        #TODO: Return one df with all scenario data


class RICS(ReplacementScenarioBuilder):
    """
    Replacement scenario based on RICS data.
    See: https://docs.google.com/document/d/107xA9jqJ1mrnRmRRFBudW7x9DQP_elYQgowDAsCcYXA/edit

    """

    def import_data(data_folder):
        
        mapper_file = data_folder.joinpath('RICS_mapper.csv')
        service_life_file = data_folder.joinpath('RICS_service_life.csv')

        mapper = pd.read_csv(mapper_file)
        service_life = pd.read_csv(service_life_file)

        return mapper, service_life


class ASHRAE(PrebuiltScenarioBuilder):
    """
    Replacement scenario based on ASHRAE data.
    See: https://docs.google.com/document/d/107xA9jqJ1mrnRmRRFBudW7x9DQP_elYQgowDAsCcYXA/edit

    """

    def import_data(data_folder):
        """ Import replacement data: note that ASHRAE database maps directly to OmniClass level 3 (also in Model data).
        """

        service_life_file = data_folder + '\ASHRAE_service_life.csv'

        service_life = pd.read_csv(service_life_file)
        mapper = None 

        return mapper, service_life

    def map_service_life(model, service_life, _):
        """ Map service life from the replacement scenario to the model.
            Maps using OmniClass Level 3.
        """

        model_with_service_life = pd.merge(model.model_material_data.assign(**{'Omniclass L3':model.model_material_data['Omniclass L3'].str.lower()}), 
                                         service_life.assign(type=service_life['type'].str.lower()), 
                                         left_on='Omniclass L3', 
                                         right_on='type', 
                                         how='left').drop(columns=['type'])
        
        model.model_material_data = model_with_service_life

        return model
    

class EndOfLifeScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods
