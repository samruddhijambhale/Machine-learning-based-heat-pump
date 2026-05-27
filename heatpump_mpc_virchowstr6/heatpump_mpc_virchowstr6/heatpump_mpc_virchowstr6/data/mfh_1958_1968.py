'''
Multi-family house
Construction period 1949 - 1978
'''
# ------------------------------------------------------------
# State of construction
# Estimated TABULA-style German MFH archetype for 1968
# Solar gains are NOT used in this project
# ------------------------------------------------------------

# Geometry and material properties
mfh_1968_0_soc = {'H_ve': 72,             # [W/K]
                  'H_tr': 310,            # [W/K]
                  'H_tr_light': 58.0,     # [W/K]
                  'c_bldg': 35,           # [Wh/(m^2K)] Medium thermal mass estimate for 1960s MFH
                  'area_floor': 287.92,   # [m^2]
                  'height_room': 2.5,     # [m]
                  'name': 'mfh_1968_0_soc'}

# Heating system properties (for target room temperature of 20°C)
mfh_1968_0_soc['T_offset'] = 10     # [K]
mfh_1968_0_soc['T_amb_lim'] = 20    # [°C]
mfh_1968_0_soc['mdot_hp'] = 0.30

# Window properties
# Solar-related terms removed: g_value and c_shade are not used.
# Windows are kept only as geometry for transmission-related modeling.
w_east = {'area': 12.0, 'tilt': 90, 'azimuth': 90, 'c_frame': 0.3}
w_south = {'area': 18.0, 'tilt': 90, 'azimuth': 180, 'c_frame': 0.3}
w_west = {'area': 12.0, 'tilt': 90, 'azimuth': 270, 'c_frame': 0.3}
w_north = {'area': 9.0, 'tilt': 90, 'azimuth': 0, 'c_frame': 0.3}
windows = [w_east, w_south, w_west, w_north]
mfh_1968_0_soc['windows'] = windows

# Geolocation
mfh_1968_0_soc['position'] = {'lat': 52.44,
                              'long': 9.74,
                              'altitude': 55,
                              'timezone': 'Europe/Berlin'}



# ------------------------------------------------------------
# EnEV refurbishment
# Estimated TABULA-style German MFH archetype for 1968
# Solar gains are NOT used in this project
# ------------------------------------------------------------

# Geometry and material properties
mfh_1968_1_enev = {'H_ve': 62,             # [W/K]
                   'H_tr': 185,            # [W/K]
                   'H_tr_light': 36.0,     # [W/K]
                   'c_bldg': 35,           # [Wh/(m^2K)] Medium thermal mass estimate for 1960s MFH
                   'area_floor': 287.92,   # [m^2]
                   'height_room': 2.5,     # [m]
                   'name': 'mfh_1968_1_enev'}

# Heating system properties (for target room temperature of 20°C)
mfh_1968_1_enev['T_offset'] = -2     # [K]
mfh_1968_1_enev['T_amb_lim'] = 20    # [°C]
mfh_1968_1_enev['mdot_hp'] = 0.27

# Window properties
# Solar-related terms removed: g_value and c_shade are not used.
# Windows are kept only as geometry for transmission-related modeling.
w_east = {'area': 12.0, 'tilt': 90, 'azimuth': 90, 'c_frame': 0.3}
w_south = {'area': 18.0, 'tilt': 90, 'azimuth': 180, 'c_frame': 0.3}
w_west = {'area': 12.0, 'tilt': 90, 'azimuth': 270, 'c_frame': 0.3}
w_north = {'area': 9.0, 'tilt': 90, 'azimuth': 0, 'c_frame': 0.3}
windows = [w_east, w_south, w_west, w_north]
mfh_1968_1_enev['windows'] = windows

# Geolocation
mfh_1968_1_enev['position'] = {'lat': 52.44,
                               'long': 9.74,
                               'altitude': 55,
                               'timezone': 'Europe/Berlin'}



# ------------------------------------------------------------
# KfW refurbishment
# Estimated TABULA-style German MFH archetype for 1968
# Solar gains are NOT used in this project
# ------------------------------------------------------------

# Geometry and material properties
mfh_1968_2_kfw = {'H_ve': 54,             # [W/K]
                  'H_tr': 118,            # [W/K]
                  'H_tr_light': 24.0,     # [W/K]
                  'c_bldg': 35,           # [Wh/(m^2K)] Medium thermal mass estimate for 1960s MFH
                  'area_floor': 287.92,   # [m^2]
                  'height_room': 2.5,     # [m]
                  'name': 'mfh_1968_2_kfw'}

# Heating system properties (for target room temperature of 20°C)
mfh_1968_2_kfw['T_offset'] = -7     # [K]
mfh_1968_2_kfw['T_amb_lim'] = 20    # [°C]
mfh_1968_2_kfw['mdot_hp'] = 0.24

# Window properties
w_east = {'area': 12.0, 'tilt': 90, 'azimuth': 90, 'c_frame': 0.3}
w_south = {'area': 18.0, 'tilt': 90, 'azimuth': 180, 'c_frame': 0.3}
w_west = {'area': 12.0, 'tilt': 90, 'azimuth': 270, 'c_frame': 0.3}
w_north = {'area': 9.0, 'tilt': 90, 'azimuth': 0, 'c_frame': 0.3}
windows = [w_east, w_south, w_west, w_north]
mfh_1968_2_kfw['windows'] = windows

# Geolocation
mfh_1968_2_kfw['position'] = {'lat': 52.44,
                              'long': 9.74,
                              'altitude': 55,
                              'timezone': 'Europe/Berlin'}

