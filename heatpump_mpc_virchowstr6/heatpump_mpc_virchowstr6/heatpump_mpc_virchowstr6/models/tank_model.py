"""
Hot Water Storage Tank - 500L
==============================
Why: Thermal storage for load shifting (charge at night, use during day)
"""
import numpy as np

class HotWaterTank:
    """500L thermal storage tank"""

    def __init__(self, params=None):
        if params is None:
            params = self.get_default_params()

        self.V = params['V']          # Volume [m³]
        self.T_min = params['T_min']  # Min temp [°C]
        self.T_max = params['T_max']  # Max temp [°C]
        self.k_loss = params['k_loss']  # Heat loss coeff [kW/K]

        # Thermal capacitance [kWh/K]
        rho = 1000  # Water density [kg/m³]
        cp = 4.186  # Specific heat [kJ/(kg·K)]
        self.C_tank = (rho * self.V * cp) / 3600  # Convert to kWh/K

        # Max storage energy [kWh]
        self.E_max = self.C_tank * (self.T_max - self.T_min)

    @staticmethod
    def get_default_params():
        return {
            'V': 0.5,        # 500 liters
            'T_min': 45.0,   # Min operating temp
            'T_max': 65.0,   # Max operating temp
            'k_loss': 0.15   # Heat loss coefficient
        }

    def dynamics(self, T_tank, Q_in, Q_out, T_amb_tank, delta_t):
        """
        Tank energy balance
        dE/dt = Q_in - Q_out - Q_loss
        E = C_tank × (T_tank - T_min)
        """
        E_tank = self.C_tank * (T_tank - self.T_min)
        Q_loss = self.k_loss * max(T_tank - T_amb_tank, 0.0)
        E_tank_next = E_tank + (Q_in - Q_out - Q_loss) * delta_t
        E_tank_next = np.clip(E_tank_next, 0, self.E_max)
        T_tank_next = self.T_min + E_tank_next / self.C_tank
        return T_tank_next

    def temp_to_SOC(self, T_tank):
        """Convert temperature to State of Charge [0-1]"""
        return (T_tank - self.T_min) / (self.T_max - self.T_min)
