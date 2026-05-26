"""
Disturbance Generation - NO SOLAR GAINS
========================================
Why NO SOLAR: <5% impact for standard German residential building
Includes: Weather, Internal gains, Electricity prices
"""
import numpy as np

class DisturbanceGenerator:
    """Generate weather, prices (NO SOLAR)"""

    def __init__(self, location='Langenhagen'):
        self.location = location

    def generate_ambient_temperature(self, start_time, num_steps, delta_t):
        """
        Winter ambient temperature [°C]
        Pattern: Sinusoidal daily (coldest at 6am, warmest at 2pm)
        """
        hours = start_time + np.arange(num_steps) * delta_t
        T_avg = 5.0  # Winter average
        T_amplitude = 4.0  # Daily swing ±4°C
        T_amb = T_avg + T_amplitude * np.sin(2 * np.pi * hours / 24.0 - np.pi/2)
        T_amb += np.random.normal(0, 0.5, num_steps)  # Add noise
        return T_amb

    def generate_internal_gains(self, start_time, num_steps, delta_t):
        """
        Internal heat gains [kW]
        Sources: Occupants (~70W/person) + Appliances (~300W/apt)
        Pattern: Higher in morning/evening (occupancy)
        """
        hours = start_time + np.arange(num_steps) * delta_t
        hour_of_day = hours % 24

        Q_base = 1.5  # Base load (always on appliances)
        Q_internal = np.ones(num_steps) * Q_base

        # Morning peak (6-9am): Cooking, showering
        morning = (hour_of_day >= 6) & (hour_of_day < 9)
        Q_internal[morning] += 1.0

        # Evening peak (5-11pm): Cooking, occupancy
        evening = (hour_of_day >= 17) & (hour_of_day < 23)
        Q_internal[evening] += 1.5

        return Q_internal

    def generate_electricity_price(self, start_time, num_steps, delta_t):
        """
        Tibber-like dynamic pricing [€/kWh]
        Based on your Tibber-pries.jpg patterns
        """
        hours = start_time + np.arange(num_steps) * delta_t
        hour_of_day = hours % 24

        base_price = 0.1717  # Average German electricity price
        price = np.ones(num_steps) * base_price

        # Morning peak (6-9am): High demand
        morning_peak = (hour_of_day >= 6) & (hour_of_day < 9)
        price[morning_peak] += 0.05

        # Evening peak (5-9pm): Highest demand
        evening_peak = (hour_of_day >= 17) & (hour_of_day < 21)
        price[evening_peak] += 0.07

        # Midday (11am-3pm): Some solar, lower prices
        midday = (hour_of_day >= 11) & (hour_of_day < 15)
        price[midday] -= 0.02

        # Night off-peak (10pm-6am): Lowest prices
        night_offpeak = (hour_of_day >= 22) | (hour_of_day < 6)
        price[night_offpeak] -= 0.04

        # Add small random variation
        price += np.random.normal(0, 0.005, num_steps)
        price = np.clip(price, 0.10, 0.30)

        return price

    def generate_all(self, start_time, num_steps, delta_t):
        """Generate all disturbances (NO SOLAR)"""
        return {
            'T_amb': self.generate_ambient_temperature(start_time, num_steps, delta_t),
            'Q_internal': self.generate_internal_gains(start_time, num_steps, delta_t),
            'price': self.generate_electricity_price(start_time, num_steps, delta_t)
        }
