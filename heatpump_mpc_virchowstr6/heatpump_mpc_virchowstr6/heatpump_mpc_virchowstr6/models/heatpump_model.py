"""
Heat Pump Model - iDM AERO ALM 4-12
====================================
YOUR actual installed heat pump at Virchowstr. 6
Specs: 4-12 kW, COP@A7/W35=5.48, 6 kW backup heater
"""
import numpy as np

class iDM_AERO_ALM_4_12:
    """iDM AERO ALM 4-12 air-source heat pump model"""

    def __init__(self, params=None):
        if params is None:
            params = self.get_default_params()

        # Power limits [kW]
        self.P_el_max = params['P_el_max']  # Inverter limit
        self.P_el_min = params['P_el_min']  # Min before cycling

        # COP limits
        self.COP_min = params['COP_min']
        self.COP_max = params['COP_max']

        # COP model: COP = a + b*T_amb - c*(T_flow-T_ref)
        self.COP_a = params['COP_a']
        self.COP_b = params['COP_b']
        self.COP_c = params['COP_c']
        self.T_ref = params['T_ref']

        self.heater_power = params.get('heater_power', 6.0)

    @staticmethod
    def get_default_params():
        """iDM AERO ALM 4-12 parameters (from datasheet)"""
        return {
            'P_el_max': 3.5,    # Max electrical [kW]
            'P_el_min': 0.8,    # Min electrical [kW]
            'COP_min': 2.0,     # Worst case
            'COP_max': 5.5,     # Best case
            'COP_a': 4.0,       # Base COP (calibrated)
            'COP_b': 0.04,      # Ambient coefficient
            'COP_c': 0.018,     # Flow temp coefficient
            'T_ref': 55.0,      # Reference temp [°C]
            'heater_power': 6.0 # Backup heater [kW]
        }

    def compute_COP(self, T_amb, T_flow):
        """Compute COP from temperatures"""
        COP_raw = self.COP_a + self.COP_b * T_amb - self.COP_c * (T_flow - self.T_ref)
        return np.clip(COP_raw, self.COP_min, self.COP_max)

    def heat_delivered(self, P_el, T_amb, T_flow):
        """
        Returns: Q_thermal [kW], COP
        Formula: Q = COP × P_el
        """
        P_el_clipped = np.clip(P_el, self.P_el_min, self.P_el_max)
        COP = self.compute_COP(T_amb, T_flow)
        Q_in = COP * P_el_clipped
        return Q_in, COP

    def get_max_heating_capacity(self, T_amb, T_flow):
        """Max thermal output at conditions [kW]"""
        COP = self.compute_COP(T_amb, T_flow)
        return COP * self.P_el_max

    def heater_required(self, Q_demand, T_amb, T_flow):
        """Check if 6 kW backup heater needed [kW]"""
        Q_hp_max = self.get_max_heating_capacity(T_amb, T_flow)
        if Q_demand > Q_hp_max:
            return min(Q_demand - Q_hp_max, self.heater_power)
        return 0.0
