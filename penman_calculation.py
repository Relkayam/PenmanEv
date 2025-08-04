"""
----------------------------------------------------------------------
Project: Penman Evaporation Calculator
Filename: penman_calculation
Author: Roy Elkayam
Created: 2025-04-08
Description: Calculates daily potential evaporation using the Penman equation based on meteorological data.
following: Valiantzas, J.D. (2006). Simplified versions for the Penman evaporation equation using routine weather data.
    Journal of Hydrology, 331(3-4), 690-702.
----------------------------------------------------------------------
"""

import math
import numpy as np
from datetime import datetime
import pandas as pd
from datetime import datetime


class PenmanEvaporation:
    """
    Implementation of simplified Penman equations for evaporation calculation from meteorological data.
    Based on: Valiantzas, J.D. (2006). Simplified versions for the Penman evaporation equation using routine weather data.
    Journal of Hydrology, 331(3-4), 690-702.
    """

    def __init__(self, latitude_deg, elevation=0, albedo=0.08):
        """
        Initialize the Penman evaporation calculator.

        Args:
            latitude_deg (float): Latitude of the location in decimal degrees
            elevation (float): Elevation above sea level in meters (default 0)
            albedo (float): Surface albedo (0.08 for open water, 0.23-0.25 for grass)
        """
        self.latitude_rad = math.radians(latitude_deg)
        self.elevation = elevation
        self.albedo = albedo

    def calculate_daily_evaporation(self, datetime_obj, t_mean, rh_mean, rs, u=None,
                                    wind_function='penman1948'):
        """
        Calculate daily potential evaporation using simplified Penman equation.

        Args:
            datetime_obj (datetime.date or str): Date of calculation (for solar geometry)
            t_mean (float): Mean air temperature (°C)
            t_max (float): Maximum air temperature (°C)
            t_min (float): Minimum air temperature (°C)
            rh_mean (float): Mean relative humidity (%)
            rs (float): Solar radiation (MJ/m²/day)
            u (float, optional): Wind speed at 2m height (m/s)
            wind_function (str): Wind function to use ('penman1948', 'penman1956', 'linacre1993')

        Returns:
            float: Potential evaporation (mm/day)
        """
        # Calculate extraterrestrial radiation and daylight hours
        ra, N = self._calculate_ra_and_N(datetime_obj)

        if u is not None:
            # Use simplified Penman equation with wind data (Eq. 32 in paper)
            # Determine wind function coefficients
            if wind_function == 'penman1948':
                a_u, b_u = 1, 0.536
            elif wind_function == 'penman1956':
                a_u, b_u = 0.5, 0.536
            elif wind_function == 'linacre1993':
                a_u, b_u = 0, 0.54
            else:
                raise ValueError("Invalid wind function specified")

            # Simplified Penman equation with wind data (Eq. 32)
            term1 = 0.051 * (1 - self.albedo) * rs * math.sqrt(t_mean + 9.5)
            term2 = 2.4 * (rs / ra) ** 2
            term3 = 0.052 * (t_mean + 20) * (1 - rh_mean / 100) * (a_u - 0.38 + b_u * u)

            # Add elevation correction if needed (Eq. 36)
            elevation_correction = 0.00012 * self.elevation
            e_pen = term1 - term2 + term3 + elevation_correction
        else:
            # Use simplified Penman equation without wind data (Eq. 33)
            term1 = 0.047 * rs * math.sqrt(t_mean + 9.5)
            term2 = 2.4 * (rs / ra) ** 2
            term3 = 0.09 * (t_mean + 20) * (1 - rh_mean / 100)

            # Add elevation correction if needed (Eq. 36)
            elevation_correction = 0.00012 * self.elevation
            e_pen = term1 - term2 + term3 + elevation_correction

        return max(0, e_pen)  # Evaporation can't be negative

    def _calculate_ra_and_N(self, date):
        """
        Calculate extraterrestrial radiation (Ra) and daylight hours (N) using simplified equations.
        Eqs. 34 and 35 in the paper.

        Args:
            date (datetime.date or str): Date for calculation

        Returns:
            tuple: (Ra in MJ/m²/day, N in hours)
        """
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()

        month = date.month
        phi = self.latitude_rad

        # Calculate daylight hours N (Eq. 34)
        N = 4 * phi * math.sin(0.53 * month - 1.65) + 12

        # Calculate extraterrestrial radiation Ra (Eq. 35)
        if abs(phi) > 23.5 * math.pi / 180:  # Temperate zone
            Ra = 3 * N * math.sin(0.131 * N - 0.95 * phi)
        else:  # Tropical zone
            Ra = 118 * N ** 2 * math.sin(0.131 * N - 0.2 * phi)

        return Ra, N


