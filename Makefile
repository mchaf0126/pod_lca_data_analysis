#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = pod_lca_data_analysis
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = pod_da_venv/Scripts/python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Create individual template model boms
boms:
	$(PYTHON_INTERPRETER) -m src.tm_extractor.extract

## Create individual template model impacts
impacts:
	$(PYTHON_INTERPRETER) -m src.impact_calculator.calc_impacts

## Create combined boms, and template models
combine:
	$(PYTHON_INTERPRETER) -m src.combine.combine

## Create combined boms, and template models
pb_scenarios:
	$(PYTHON_INTERPRETER) -m src.p_scenario_builder.build_prebuilt_scenarios

## Create all public dataset files
datasets:
	$(PYTHON_INTERPRETER) -m src.tm_extractor.extract
	$(PYTHON_INTERPRETER) -m src.impact_calculator.calc_impacts
	$(PYTHON_INTERPRETER) -m src.p_scenario_builder.build_prebuilt_scenarios
	$(PYTHON_INTERPRETER) -m src.combine.combine