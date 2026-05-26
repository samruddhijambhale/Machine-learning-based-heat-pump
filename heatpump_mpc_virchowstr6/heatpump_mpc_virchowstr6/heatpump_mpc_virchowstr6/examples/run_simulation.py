"""
Main Simulation Script
======================
Runs MPC-controlled heat pump system for Virchowstr. 6

Usage: python examples/run_simulation.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from models import IntegratedSystem
from controllers import MPCController
from utils import DisturbanceGenerator, plot_simulation_results

def main():
    """Run 3-day MPC simulation"""

    print("="*70)
    print("HEAT PUMP MPC SIMULATION")
    print("Virchowstr. 6, Langenhagen")
    print("="*70)
    print()

    # Setup
    print("Initializing system...")
    system = IntegratedSystem()

    print(f"✓ Building: 2R2C model (NO SOLAR)")
    print(f"  - Floor area: {system.building.A_floor:.2f} m²")
    print(f"  - Heat load: 10.968 kW")
    print(f"  - Comfort: {system.building.T_comfort_min}-{system.building.T_comfort_max}°C")

    print(f"✓ Heat pump: iDM AERO ALM 4-12")
    print(f"  - Power: {system.heatpump.P_el_min}-{system.heatpump.P_el_max} kW")
    print(f"  - Backup heater: {system.heatpump.heater_power} kW")

    print(f"✓ Tank: 500L ({system.tank.T_min}-{system.tank.T_max}°C)")
    print(f"  - Storage: {system.tank.E_max:.2f} kWh")

    # MPC controller
    controller = MPCController(
        system, 
        horizon=16,    # 4 hours (why: covers price variations)
        delta_t=0.25,  # 15 min (why: balance speed/accuracy)
        w_switch=0.1   # Switching penalty (why: prevent cycling)
    )
    print(f"✓ MPC controller (NO RL)")
    print(f"  - Horizon: {controller.horizon} steps ({controller.horizon*controller.delta_t:.1f} hours)")
    print(f"  - Timestep: {controller.delta_t*60:.0f} minutes")

    # Disturbances
    distgen = DisturbanceGenerator()
    print(f"✓ Disturbances: Weather, internal gains, prices (NO SOLAR)")
    print()

    # Simulation parameters
    days = 3
    delta_t = 0.25  # hours
    num_steps = int(days * 24 / delta_t)

    print(f"Simulating {days} days ({num_steps} steps)...")
    print()

    # Generate disturbances (need extra for MPC horizon)
    disturbances = distgen.generate_all(0, num_steps + 16, delta_t)

    # Initialize
    state = system.get_initial_state()

    # Results storage
    results = {
        'time': [],
        'T_indoor': [],
        'T_wall': [],
        'T_tank': [],
        'SOC': [],
        'P_el': [],
        'cost': [],
        'COP': [],
        'Q_hp': [],
        'd_heat': [],
        'T_amb': [],
        'price': []
    }

    # Simulation loop
    for k in range(num_steps):
        # Current disturbances
        dist_k = {
            'T_amb': disturbances['T_amb'][k],
            'Q_internal': disturbances['Q_internal'][k],
            'T_amb_tank': 15.0  # Basement temperature
        }

        # Forecasts for MPC
        forecasts = {
            'price': disturbances['price'][k:k+16],
            'T_amb': disturbances['T_amb'][k:k+16],
            'Q_internal': disturbances['Q_internal'][k:k+16]
        }

        # MPC solves optimization
        P_el, solution = controller.solve(state, forecasts)

        # Simulate one step
        state, outputs = system.step(state, P_el, dist_k, delta_t)

        # Store results
        results['time'].append(k * delta_t)
        results['T_indoor'].append(outputs['T_indoor'])
        results['T_wall'].append(state[1])
        results['T_tank'].append(outputs['T_tank'])
        results['SOC'].append(outputs['SOC'])
        results['P_el'].append(P_el)
        results['cost'].append(P_el * disturbances['price'][k] * delta_t)
        results['COP'].append(outputs['COP'])
        results['Q_hp'].append(outputs['Q_hp'])
        results['d_heat'].append(outputs['d_heat'])
        results['T_amb'].append(dist_k['T_amb'])
        results['price'].append(disturbances['price'][k])

        # Daily summary
        if k % int(24/delta_t) == 0 and k > 0:
            day = k / (24/delta_t)
            cost_today = np.sum(results['cost'][-int(24/delta_t):])
            print(f"  Day {int(day)-1}: T_indoor={outputs['T_indoor']:.1f}°C, "
                  f"SOC={outputs['SOC']*100:.0f}%, Cost={cost_today:.2f}€")

    # Convert to arrays
    for key in results:
        results[key] = np.array(results[key])

    # Final summary
    print()
    print("="*70)
    print("SIMULATION RESULTS")
    print("="*70)
    total_elec = np.sum(results['P_el']) * delta_t
    total_cost = np.sum(results['cost'])
    avg_cop = np.mean(results['COP'])
    comfort_violations = np.sum(results['T_indoor'] < system.building.T_comfort_min)

    print(f"Total electricity: {total_elec:.2f} kWh")
    print(f"Total cost: {total_cost:.2f} €")
    print(f"Average COP: {avg_cop:.2f}")
    print(f"Comfort violations: {comfort_violations} steps ({comfort_violations/num_steps*100:.1f}%)")
    print(f"Min T_indoor: {np.min(results['T_indoor']):.1f}°C")
    print(f"Max T_indoor: {np.max(results['T_indoor']):.1f}°C")
    print()

    # Create results directory if needed
    os.makedirs('results', exist_ok=True)

    # Plot results
    print("Generating plots...")
    plot_simulation_results(results, days)

    print()
    print("="*70)
    print("SIMULATION COMPLETE ✓")
    print("="*70)
    print()
    print("Check results/simulation_results.png for detailed plots")

    return results

if __name__ == "__main__":
    results = main()
