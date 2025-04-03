from enum import Enum
import os, json, yaml
import geopandas as gpd
from geopandas.geodataframe import GeoDataFrame
import osmnx as ox

REGION_DICT_PATH = "region_dictionary.json"
REGION_CONUS = "conus"

class RegionType(Enum):
    COUNTRY = 0
    URBAN_AREA = 1
    COUNTY = 2
    PROVINCE = 3
    CUSTOM = 4

class Controller():
    
    def __init__(self, config_path = 'config.yaml'):
        self.config = self._load_config(config_path)
        self.region = str(self.config.get("region"))

        if not self.region:
            raise ValueError("The configuration must include a 'region' key.")

        self.gdf = None
        self._init_region()

    def _load_config(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file '{path=}' does not exist.")

        with open(path, 'r') as file:
            return yaml.safe_load(file)
        
    def _init_region(self):
        if os.path.exists(self.region) and self.region.endswith('.shp'):
            region_data = self.load_shapefile(self.region)
            self.gdf = region_data
        else:
            region_data = self.load_by_name(self.region)
            self.gdf = region_data

        return region_data

    @staticmethod
    def load_shapefile(shapefile_path):
        try:
            return gpd.read_file(shapefile_path)
        except Exception as exception:
            raise RuntimeError(f"Could not load shapefile: {exception=}")
        
    @staticmethod
    def load_conus():
        with open(REGION_DICT_PATH, 'r') as f:
            region_dict = json.load(f)

        region_data = Controller.load_shapefile(region_dict[RegionType.PROVINCE])

        us_states = region_data[region_data['adm0_a3'] == 'USA']

        non_conus = ['Alaska', 'Hawaii', 'Puerto Rico', 'Guam', 'American Samoa',
                    'Northern Mariana Islands', 'United States Virgin Islands']

        # Filter out non-CONUS
        conus = us_states[~us_states['name'].isin(non_conus)]
        
        return conus

    @staticmethod
    def load_by_name(name, region_type = RegionType.CUSTOM):
        if (not region_type == RegionType.CUSTOM):
            with open(REGION_DICT_PATH, 'r') as f:
                region_dict = json.load(f)

            try:
                shapefile_path = region_dict[region_type]
                region_data = Controller.load_shapefile(shapefile_path)

                selected = region_data[str(region_data['name']).strip().lower() == 
                                    name.strip().lower()]

                if (selected.empty):
                    raise ValueError(
                        f"Region name {name=} could not be found based on region type")

                return selected
            except:
                raise ValueError(f"Region name '{name=}' shapefile not found.")
        else:
            try: 
                return ox.geocode_to_gdf(name)
            except:
                raise ValueError(f"Region name '{name=}' not recognized or shapefile not found.")
    
    def get_region_data(self):
        return self.gdf
    
    def set_region_data(self, region_data: GeoDataFrame):
        self.gdf = region_data


                
