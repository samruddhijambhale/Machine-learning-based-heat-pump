"""Plotting utilities for simulation results"""
import matplotlib.pyplot as plt
import numpy as np

def plot_simulation_results(results, days, filename='results/simulation_results.png'):
    """Create 5-panel results plot"""
    fig, axes = plt.subplots(5, 1, figsize=(14, 12))

    # 1. Temperatures
    axes[0].plot(results['time'], results['T_indoor'], label='Indoor', linewidth=2, color='#e74c3c')
    axes[0].plot(results['time'], results['T_wall'], label='Wall', linewidth=1.5, color='#3498db', alpha=0.7)
    axes[0].plot(results['time'], results['T_amb'], label='Ambient', alpha=0.5, color='gray')
    axes[0].axhline(20, color='red', linestyle='--', alpha=0.5, label='Comfort min')
    axes[0].set_ylabel('Temperature [°C]', fontsize=11)
    axes[0].legend(loc='upper right', fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title('Building Temperatures (2R2C - NO SOLAR)', fontsize=12, fontweight='bold')

    # 2. Tank & SOC
    ax1 = axes[1]
    ax1.plot(results['time'], results['T_tank'], label='Tank temp', color='#e67e22', linewidth=2)
    ax1.axhline(45, color='blue', linestyle='--', alpha=0.3)
    ax1.axhline(65, color='red', linestyle='--', alpha=0.3)
    ax1.set_ylabel('Tank Temp [°C]', fontsize=11, color='#e67e22')
    ax1.tick_params(axis='y', labelcolor='#e67e22')

    ax1b = ax1.twinx()
    ax1b.fill_between(results['time'], 0, results['SOC']*100, alpha=0.3, color='#27ae60')
    ax1b.set_ylabel('SOC [%]', fontsize=11, color='#27ae60')
    ax1b.tick_params(axis='y', labelcolor='#27ae60')
    ax1b.set_ylim([0, 100])

    ax1.grid(True, alpha=0.3)
    ax1.set_title('Hot Water Tank Storage (500L)', fontsize=12, fontweight='bold')

    # 3. Power & Price
    ax2 = axes[2]
    ax2.fill_between(results['time'], 0, results['P_el'], alpha=0.4, color='#9b59b6')
    ax2.plot(results['time'], results['P_el'], color='#9b59b6', linewidth=1.5, label='HP power')
    ax2.set_ylabel('Power [kW]', fontsize=11, color='#9b59b6')
    ax2.tick_params(axis='y', labelcolor='#9b59b6')

    ax2b = ax2.twinx()
    ax2b.plot(results['time'], results['price']*100, color='#c0392b', alpha=0.7, linewidth=2, label='Price')
    ax2b.set_ylabel('Price [ct/kWh]', fontsize=11, color='#c0392b')
    ax2b.tick_params(axis='y', labelcolor='#c0392b')

    ax2.grid(True, alpha=0.3)
    ax2.set_title('Heat Pump & Tibber Pricing', fontsize=12, fontweight='bold')

    # 4. COP & Heat
    ax3 = axes[3]
    ax3.plot(results['time'], results['COP'], label='COP', linewidth=2, color='#16a085')
    ax3.set_ylabel('COP', fontsize=11, color='#16a085')
    ax3.tick_params(axis='y', labelcolor='#16a085')
    ax3.axhline(np.mean(results['COP']), color='#16a085', linestyle='--', alpha=0.5)

    ax3b = ax3.twinx()
    ax3b.plot(results['time'], results['Q_hp'], label='HP output', color='#e74c3c', alpha=0.7, linewidth=1.5)
    ax3b.plot(results['time'], results['d_heat'], label='Demand', color='#3498db', alpha=0.7, linewidth=1.5, linestyle='--')
    ax3b.set_ylabel('Heat [kW]', fontsize=11)

    ax3.grid(True, alpha=0.3)
    ax3.set_title('Heat Pump Efficiency (iDM AERO ALM 4-12)', fontsize=12, fontweight='bold')

    # 5. Cumulative cost
    cumulative_cost = np.cumsum(results['cost'])
    axes[4].plot(results['time'], cumulative_cost, linewidth=2.5, color='#27ae60')
    axes[4].fill_between(results['time'], 0, cumulative_cost, alpha=0.3, color='#27ae60')
    axes[4].set_ylabel('Cumulative Cost [€]', fontsize=11)
    axes[4].set_xlabel('Time [hours]', fontsize=11)
    axes[4].grid(True, alpha=0.3)
    axes[4].set_title(f'Total Cost: {cumulative_cost[-1]:.2f} €', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved to '{filename}'")
    plt.close()
