"""
Integrated System: Building + Heat Pump + Tank
==============================================
Why: Combines all components for MPC to optimize
"""
import numpy as np
from models.building_model import Building2R2C
from models.heatpump_model import iDM_AERO_ALM_4_12
from models.tank_model import HotWaterTank

class IntegratedSystem:
    """Complete heating system"""

    def __init__(self, building_params=None, hp_params=None, tank_params=None):
        self.building = Building2R2C(building_params)
        self.heatpump = iDM_AERO_ALM_4_12(hp_params)
        self.tank = HotWaterTank(tank_params)
        self.state_dim = 3  # [T_indoor, T_wall, T_tank]

    def get_initial_state(self):
        """Initial conditions [°C]"""
        return np.array([20.0, 18.0, 55.0])  # Comfortable start

    def step(self, state, P_el, disturbances, delta_t):
        """
        Simulate one timestep

        Flow: P_el -> HP -> Tank -> Building
        """
        T_indoor, T_wall, T_tank = state

        # Heat pump output
        Q_hp, COP = self.heatpump.heat_delivered(
            P_el, disturbances['T_amb'], T_tank
        )

        # Building demand (steady-state estimate)
        R_total = self.building.R_ie + self.building.R_ea
        d_heat = max((T_indoor - disturbances['T_amb']) / R_total, 0.0)

        # Tank dynamics
        T_amb_tank = disturbances.get('T_amb_tank', 15.0)
        T_tank_next = self.tank.dynamics(T_tank, Q_hp, d_heat, T_amb_tank, delta_t)

        # Heat to building (limited by tank energy)
        u_heat = min(d_heat, max((T_tank - self.tank.T_min) * self.tank.C_tank / delta_t, 0.0))

        # Building dynamics
        building_state = np.array([T_indoor, T_wall])
        next_building_state = self.building.dynamics(
            building_state, u_heat, 
            disturbances['T_amb'], disturbances['Q_internal'], 
            delta_t
        )

        next_state = np.array([
            next_building_state[0],
            next_building_state[1],
            T_tank_next
        ])

        outputs = {
            'COP': COP,
            'Q_hp': Q_hp,
            'u_heat': u_heat,
            'd_heat': d_heat,
            'comfort_violation': self.building.comfort_violation(next_state[0]),
            'T_indoor': next_state[0],
            'T_tank': next_state[2],
            'SOC': self.tank.temp_to_SOC(T_tank_next)
        }

        return next_state, outputs

    def get_constraints(self):
        """Get system constraints for MPC"""
        return {
            'P_el_min': self.heatpump.P_el_min,
            'P_el_max': self.heatpump.P_el_max,
            'T_indoor_min': self.building.T_comfort_min,
            'T_indoor_max': self.building.T_comfort_max,
            'T_tank_min': self.tank.T_min,
            'T_tank_max': self.tank.T_max
        }
