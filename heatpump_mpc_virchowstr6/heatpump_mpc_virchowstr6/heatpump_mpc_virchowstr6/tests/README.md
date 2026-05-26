# Tests Directory

Unit tests for the MPC system.

To add tests, install pytest:
```bash
pip install pytest
```

Then create test files:
- `test_building.py` - Test 2R2C model
- `test_heatpump.py` - Test iDM AERO ALM 4-12
- `test_mpc.py` - Test MPC controller

Run tests with:
```bash
pytest tests/
```
