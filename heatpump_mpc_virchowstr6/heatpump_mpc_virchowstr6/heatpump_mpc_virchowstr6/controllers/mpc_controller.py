"""
Model Predictive Controller - NO Reinforcement Learning
========================================================
Why MPC: Predictive, handles constraints, optimization-based
Why NO RL: Known physics, deterministic, faster deployment
"""
import numpy as np
try:
    import casadi as ca
    CASADI_AVAILABLE = True
except ImportError:
    CASADI_AVAILABLE = False
    print("ERROR: Install CasADi with: pip install casadi")

class MPCController:
    """MPC for heat pump optimization (pure optimization, NO RL)"""

    def __init__(self, system, horizon=16, delta_t=0.25, w_switch=0.1):
        """
        Args:
            horizon: 16 steps = 4 hours (why: covers price variations)
            delta_t: 0.25 hours = 15 min (why: balance speed/accuracy)
            w_switch: 0.1 (why: prevent excessive on/off cycling)
        """
        if not CASADI_AVAILABLE:
            raise ImportError("CasADi required")

        self.system = system
        self.horizon = horizon
        self.delta_t = delta_t
        self.w_switch = w_switch
        self.constraints = system.get_constraints()
        self._build_optimizer()
        self.P_el_prev = 0.0

    def _build_optimizer(self):
        """Build CasADi NLP (Nonlinear Program)"""
        H = self.horizon

        # Decision variables: electrical power over horizon
        self.P_el = ca.MX.sym('P_el', H)

        # Parameters (known inputs at solve time)
        self.state_0 = ca.MX.sym('state_0', 3)
        self.price_forecast = ca.MX.sym('price', H)
        self.T_amb_forecast = ca.MX.sym('T_amb', H)
        self.Q_int_forecast = ca.MX.sym('Q_int', H)
        self.P_el_prev_param = ca.MX.sym('P_el_prev', 1)

        cost = 0.0
        g = []  # Constraints
        lbg = []  # Lower bounds
        ubg = []  # Upper bounds

        state = self.state_0

        # Predict over horizon
        for k in range(H):
            T_indoor = state[0]
            T_wall = state[1]
            T_tank = state[2]

            # COP model (embedded in MPC)
            COP = self.system.heatpump.COP_a +                   self.system.heatpump.COP_b * self.T_amb_forecast[k] -                   self.system.heatpump.COP_c * (T_tank - self.system.heatpump.T_ref)
            COP = ca.fmax(ca.fmin(COP, self.system.heatpump.COP_max), 
                         self.system.heatpump.COP_min)

            Q_hp = COP * self.P_el[k]

            # Building demand
            R_total = self.system.building.R_ie + self.system.building.R_ea
            d_heat = ca.fmax((T_indoor - self.T_amb_forecast[k]) / R_total, 0.0)

            # Tank dynamics
            Q_loss = self.system.tank.k_loss * ca.fmax(T_tank - 15.0, 0.0)
            E_tank = self.system.tank.C_tank * (T_tank - self.system.tank.T_min)
            E_tank_next = E_tank + (Q_hp - d_heat - Q_loss) * self.delta_t
            T_tank_next = self.system.tank.T_min + E_tank_next / self.system.tank.C_tank

            # Heat to building
            u_heat = ca.fmin(d_heat, ca.fmax(E_tank / self.delta_t, 0.0))

            # Building dynamics (2R2C, NO SOLAR)
            Q_ie = (T_indoor - T_wall) / self.system.building.R_ie
            Q_ea = (T_wall - self.T_amb_forecast[k]) / self.system.building.R_ea

            dT_indoor = (u_heat + self.Q_int_forecast[k] - Q_ie) / self.system.building.C_i
            dT_wall = (Q_ie - Q_ea) / self.system.building.C_e

            T_indoor_next = T_indoor + dT_indoor * self.delta_t
            T_wall_next = T_wall + dT_wall * self.delta_t

            state = ca.vertcat(T_indoor_next, T_wall_next, T_tank_next)

            # COST FUNCTION
            # 1. Electricity cost (main objective)
            cost += self.price_forecast[k] * self.P_el[k] * self.delta_t

            # 2. Switching penalty (prevent on/off cycling)
            if k == 0:
                cost += self.w_switch * (self.P_el[k] - self.P_el_prev_param)**2
            else:
                cost += self.w_switch * (self.P_el[k] - self.P_el[k-1])**2

            # CONSTRAINTS
            # Power limits
            g.append(self.P_el[k])
            lbg.append(self.constraints['P_el_min'])
            ubg.append(self.constraints['P_el_max'])

            # Comfort constraint (CRITICAL)
            g.append(T_indoor_next)
            lbg.append(self.constraints['T_indoor_min'])
            ubg.append(self.constraints['T_indoor_max'])

            # Tank temperature limits
            g.append(T_tank_next)
            lbg.append(self.constraints['T_tank_min'])
            ubg.append(self.constraints['T_tank_max'])

        g = ca.vertcat(*g)

        # Create NLP
        nlp = {
            'x': self.P_el,
            'f': cost,
            'g': g,
            'p': ca.vertcat(self.state_0, self.price_forecast, 
                           self.T_amb_forecast, self.Q_int_forecast,
                           self.P_el_prev_param)
        }

        # Solver options
        opts = {
            'ipopt.print_level': 0,  # Suppress solver output
            'print_time': 0,
            'ipopt.max_iter': 100
        }

        self.solver = ca.nlpsol('solver', 'ipopt', nlp, opts)
        self.lbg = lbg
        self.ubg = ubg

    def solve(self, state, forecasts):
        """
        Solve MPC optimization

        Returns: P_el_optimal (for next 15 min), solution dict
        """
        H = self.horizon

        price = forecasts['price'][:H]
        T_amb = forecasts['T_amb'][:H]
        Q_internal = forecasts.get('Q_internal', np.ones(H) * 2.0)[:H]

        p = np.concatenate([state, price, T_amb, Q_internal, [self.P_el_prev]])

        try:
            sol = self.solver(x0=np.zeros(H), p=p, lbg=self.lbg, ubg=self.ubg)
            P_el_plan = np.array(sol['x']).flatten()
            P_el_optimal = float(P_el_plan[0])
            self.P_el_prev = P_el_optimal

            solution = {
                'success': True,
                'P_el_plan': P_el_plan,
                'cost': float(sol['f'])
            }
        except Exception as e:
            print(f"MPC solver failed: {e}")
            P_el_optimal = 1.0
            solution = {'success': False, 'error': str(e)}

        return P_el_optimal, solution
