# from pathlib import Path
from dataclasses import dataclass
import pandas as pd
import numpy as np
# import src.utils.general as gen


@dataclass
class PrebuiltScenarioBuilder:
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


@dataclass
class TransportationScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


@dataclass
class ConstructionScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods


@dataclass
class ReplacementScenarioBuilder(PrebuiltScenarioBuilder):
    """
    TMethods for creating replacement scenarios.
    See: https://docs.google.com/document/d/1U98-ywdp16ldmXZG7rqztwkpHnKCkLEVUq2V_0_gNNk/edit?usp=sharing
         https://docs.google.com/document/d/1d9ZtZbSrMXGaN7rMRNjzVAoSHPShybrjESpL6ZFL88A/edit?usp=sharing

    """

    def import_data(data_folder):
        """ Import replacement data: service life, and mappings to template model where necessary.
        """

        pass


    def map_service_life(model, service_life, mapper):
        """ Map service life from the replacement scenario to the model.
            Updates the model data with service life.

            Parameters
            ----------
            model : TemplateModel Obj.
                Model for which the replacements are applied.
            service_life : df.
                Table with columns 'id', 'material', 'service life'.
            mapper : df.
                Table mapping 'Material Name', 'Revit category' in template model to 'material', 'assembly' in the service_life table

            Returns
            -------
            TemplateModel Obj.
                Model with updated data on service life.  
        """


        material_to_service_life = pd.merge(mapper[['material', 'assembly', 'type']], service_life[['type', 'service_life']], 
                                            on='type', 
                                            how='left').drop(columns=['type'])
        model_with_service_life = pd.merge(model.model_material_data, material_to_service_life, 
                                         left_on=['Material Name', 'Revit category'], 
                                         right_on=['material', 'assembly'], 
                                         how='left').drop(columns=['material'])
        
        model.model_material_data = model_with_service_life

        return model


    def calculate_impacts(model, RSP=60):
        """ Calcualte the impacts, considering a reference study period (default 60 yrs).
            Service life entry of '60+' is matched to reference study period.
            Default reference study period is 60 years.

            Parameters
            ----------
            model : TemplateModel Obj.
                Model for which the replacements are applied.
            model_to_service_life : df.
                Model data with service life column.
            RSP : int.
                Reference study period in years.

            Returns
            -------
            df.
                Table of replacement (B4) impacts by TRACI categories (column headings) for each material in the model (row headings by element index)    
        """

        # no. of replacements
        service_life_in_str = model.model_material_data['service_life']
        service_life_in_str = service_life_in_str.replace('60+', RSP)
        service_life = pd.to_numeric(service_life_in_str)
        no_of_replacements = np.ceil(RSP / service_life) - 1

        # impacts per replacement
        a1_a3 = model.impact_data['a1-a3']
        a4    = model.impact_data['a4']
        c2_c4 = model.impact_data['c2-c4']
        d     = model.impact_data['d']

        # total impacts
        b4 = a1_a3.copy()
        b4['Life Cycle Stage'] = '[B4] Replacement'
        for impact_category in ['Acidification Potential Total (kgSO2eq)', 'Eutrophication Potential Total (kgNeq)', 'Global Warming Potential Total (kgCO2eq)', 'Ozone Depletion Potential Total (CFC-11eq)', 'Smog Formation Potential Total (kgO3eq)']:
            b4[impact_category] = (a1_a3[impact_category] + a4[impact_category] + c2_c4[impact_category] + d[impact_category]) * no_of_replacements

        return b4

    def set_results(model, result):
        """ Set calculated replacement (B4) impacts to the model data.
        """

        pass
        # TODO: Implement method


class RICS(PrebuiltScenarioBuilder):
    """
    Replacement scenario based on RICS data.
    See: https://docs.google.com/document/d/107xA9jqJ1mrnRmRRFBudW7x9DQP_elYQgowDAsCcYXA/edit

    """

    def import_data(data_folder):
        
        mapper_file = data_folder + '\RICS_mapper.csv'
        service_life_file = data_folder + '\RICS_service_life.csv'

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
    

@dataclass
class EndOfLifeScenarioBuilder(PrebuiltScenarioBuilder):
    """Methods for creating a prebuilt scenario"""
    # attributes

    # methods
