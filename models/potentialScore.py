
import numpy as np

class PotentialScoreCalculator:
    """
    Calculator for environmental and socioeconomic potential scores.
    Normalizes various environmental indicators and combines them into a weighted score.
    """
    
    BOUNDS = {
        "so2": (0, 300),
        "no2": (0, 300),
        "co": (0, 10),
        "o3": (0, 300),
        "pm25": (0, 500),
        "aqi": (0, 500),
        "precipitation": (0, 500),
        "ndvi": (0, 1),
        "sentinel": (0, 1),
        "poverty_index": (0, 1),
    }
    
    
    WEIGHTS = {
        "air_pollution": 0.30,
        "emissions": 0.25,
        "environment": 0.20,
        "poverty": 0.25
    }
    
    @staticmethod
    def normalize(val, min_val, max_val):
        """Normalize a value between 0 and 1 based on min and max bounds"""
        return np.clip((val - min_val) / (max_val - min_val), 0, 1)
    
    def normalize_parameter(self, param_name, value):
        """Normalize a specific parameter using its predefined bounds"""
        min_val, max_val = self.BOUNDS[param_name]
        return self.normalize(value, min_val, max_val)
    
    def calculate_score(self, params):
        """
        Calculate the potential score based on environmental and socioeconomic parameters.
        
        Args:
            params: dict containing the following keys:
                - pm25: Particulate matter 2.5 concentration
                - aqi: Air Quality Index
                - so2: Sulfur dioxide concentration
                - no2: Nitrogen dioxide concentration
                - co: Carbon monoxide concentration
                - o3: Ozone concentration
                - ndvi: Normalized Difference Vegetation Index
                - sentinel: Soil moisture from Sentinel satellite
                - poverty_index: Socioeconomic poverty index
                
        Returns:
            float: Combined potential score (0-100)
        """
        # Normalize all input parameters
        norm_params = {
            key: self.normalize_parameter(key, params[key]) 
            for key in params if key in self.BOUNDS
        }
        
        
        component_scores = {
            "air_pollution": 0.05 * (0.5 * norm_params["pm25"] + 0.5 * norm_params["aqi"]),
            "emissions": 0.05 * (0.25 * norm_params["so2"] + 0.25 * norm_params["no2"] +
                                0.25 * norm_params["co"] + 0.25 * norm_params["o3"]),
            "environment": 0.4 * (0.5 * (1 - norm_params["ndvi"]) + 0.5 * (1 - norm_params["sentinel"])),
            "poverty": 0.5 * norm_params["poverty_index"]
        }

        
        final_score = sum(self.WEIGHTS[component] * score 
                         for component, score in component_scores.items())
        
        return round(final_score * 100 * 4, 2)
    
    @classmethod
    def generate_potential_score(cls, pm25, aqi, so2, no2, co, o3, ndvi, sentinel, poverty_index):
        """
        Legacy method for calculating potential score with individual parameters.
        Uses the same algorithm as calculate_score but with positional arguments.
        This is a class method so it can be called without instantiating the class.
        """
        params = {
            "pm25": pm25,
            "aqi": aqi,
            "so2": so2,
            "no2": no2,
            "co": co,
            "o3": o3,
            "ndvi": ndvi,
            "sentinel": sentinel,
            "poverty_index": poverty_index
        }
        calculator = cls()
        return calculator.calculate_score(params)
