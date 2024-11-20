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
        bom_df = gen.read_csv(bom_file_path)
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
    """Calculation of replacement impacts from bill of materials. This is a placeholder."""
    def calculate_impacts(self):
        self.impacts = self.bill_of_materials[
            self.bill_of_materials['Life Cycle Stage'] == "[B2-B5] Maintenance and Replacement"
        ]


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
