from enum import Enum
import os, json, yaml
import geopandas as gpd
from geopandas.geodataframe import GeoDataFrame
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Loading config at: {config_path}")
        
        self.config = self._load_config(config_path)

        if ('region_name' in self.config):
            self.region = str(self.config.get("region_name"))
        else:
            raise ValueError("The configuration must include a 'region' key.")

        if ('region_type' in self.config):
            self.region_type = int(self.config.get('region_type'))
        else:
            self.region_type = RegionType.CUSTOM

        logger.info(f"Loading region: {self.region}")

        self.gdf = None
        self._init_region()

    def _load_config(self, path):
        logger.info(f"_load_config")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file '{path}' does not exist.")

        with open(path, 'r') as file:
            return yaml.safe_load(file)
        
    def _init_region(self):
        logger.info(f"_init_region")

        if os.path.exists(self.region) and self.region.endswith('.shp'):
            region_data = self.load_shapefile(self.region)
            self.gdf = region_data
        elif self.region.strip().lower() == 'conus':
            region_data = self.load_conus()
            self.gdf = region_data
        else:
            region_data = self.load_by_name(self.region, self.region_type)
            self.gdf = region_data

        return region_data

    @staticmethod
    def load_shapefile(shapefile_path):
        logger.info(f"load_shapefile")

        try:
            return gpd.read_file(shapefile_path)
        except Exception as exception:
            raise RuntimeError(f"Could not load shapefile: {exception=}")
        
    @staticmethod
    def load_conus():
        logger.info(f"load_conus")

        if not os.path.exists(REGION_DICT_PATH):
            raise FileNotFoundError(f"Missing region dictionary at {REGION_DICT_PATH}")

        with open(REGION_DICT_PATH, 'r') as f:
            region_dict = json.load(f)

        region_data = Controller.load_shapefile(region_dict[RegionType.PROVINCE.value])

        us_states = region_data[region_data['adm0_a3'] == 'USA']

        non_conus = ['Alaska', 'Hawaii', 'Puerto Rico', 'Guam', 'American Samoa',
                    'Northern Mariana Islands', 'United States Virgin Islands']

        # Filter out non-CONUS
        conus = us_states[~us_states['name'].isin(non_conus)]
        
        return conus
    
    @staticmethod
    def check_shapedf(shape_df):

        logger.info(f"checking dataframe for name: {shape_df.columns}")

        shape_df.columns = map(str.lower, shape_df.columns)
        if ('name' in shape_df.columns):
            return True
        else:
            return False

    @staticmethod
    def load_by_name(name, region_type = RegionType.CUSTOM):
        logger.info(f"load_by_name: {name}")

        if (not region_type == RegionType.CUSTOM):
            with open(REGION_DICT_PATH, 'r') as f:
                region_dict = json.load(f)

            try:
                shapefile_path = region_dict[region_type]
                region_data = Controller.load_shapefile(shapefile_path)

                if (Controller.check_shapedf(region_data)):
                    region_data['name_clean'] = region_data['name'].str.strip().str.lower()
                    name_clean = name.strip().lower()
                    selected = region_data[region_data['name_clean'] == name_clean]

                    if (selected.empty):
                        raise ValueError(
                            f"Region name {name} could not be found based on region type")

                    return selected
                else:
                    raise ValueError(f"Region name '{name}' shapefile not found.")
            except:
                raise ValueError(f"Region name '{name}' shapefile not found.")
        else:
            try: 
                import osmnx as ox
                return ox.geocode_to_gdf(name)
            except ImportError as e:
                logger.error(f"Need to install OSMNX to use this functionality")
                raise e 
            except Exception as e:
                raise ValueError(f"Region name '{name=}' not recognized or shapefile not found.")
    
    def get_region_data(self):
        logger.info(f"get_region_data")

        return self.gdf
    
    def set_region_data(self, region_data: GeoDataFrame):
        logger.info(f"set_region_data")

        self.gdf = region_data


                
