# BSIM3v3 Python Implementation

![BSIM3v3 Logo](https://img.shields.io/badge/BSIM3v3-MOSFET_Model-blue)
![Python](https://img.shields.io/badge/Python-3.13.5%2B-green)
[![License](https://img.shields.io/badge/License-Refer_to_LICENSE-red)]([LICENSE](https://mit-license.org/))

A Python implementation of the BSIM3v3 (Berkeley Short-channel IGFET Model) version 3.3 for MOSFET transistors. This model accurately calculates drain current (Ids) and other characteristics based on terminal voltages and physical parameters.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Model Overview](#model-overview)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

## Features

- Complete BSIM3v3.2 model implementation
- Accurate calculation of:
  - Threshold voltage with short-channel, narrow width, and DIBL effects
  - Mobility degradation effects
  - Velocity saturation
  - Channel length modulation
  - Subthreshold conduction
  - Temperature effects
  - Parasitic resistance effects
- Multiple operation regions:
  - Subthreshold (weak inversion)
  - Linear (triode)
  - Saturation
- Comprehensive documentation and examples

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Gueni/BSIM3v3-Python-Implementation.git
cd BSIM3v3-Python-Implementation
```
2. Install required dependencies:
```bash
pip install numpy matplotlib
```
## Usage

Basic usage example:
```bash
from src.BSIM3v3_2 import BSIM3v3_Model

# Initialize model (default 180nm NMOS parameters)
model = BSIM3v3_Model()

# Calculate drain current for given bias conditions
Vgs = 1.2  # Gate-source voltage [V]
Vds = 1.0  # Drain-source voltage [V]
Vbs = 0.0  # Bulk-source voltage [V]
T = 300    # Temperature [K]

Ids = model.compute(Vgs, Vds, Vbs, T)
print(f"Drain current: {Ids:.3e} A")
```
## Model Overview
The implementation follows the BSIM3v3.2 manual with these key components:

#### Threshold Voltage Calculation
Includes:

- Body effect

- Short-channel effects

- Narrow width effects

- DIBL effects

- Temperature effects

#### Mobility Model
Accounts for:

- Vertical field mobility degradation

- Temperature effects

- Body effect on mobility

#### Current Calculation
Handles all operation regions:

- Subthreshold (weak inversion)

- Linear (triode)

- Saturation (with channel length modulation)

#### Examples
The repository includes several demonstration scripts:
1. Threshold Voltage Analysis:
Shows Vth vs Vds characteristics and Id vs Vgs/Vds curves.
2. Comparison with Other Models:
Compares BSIM3v3 with other MOSFET models.
3. Custom Parameter Analysis:

## Documentation
- Full BSIM3v3.2 manual included in source/pdf/bsim3v3.2.pdf

- Model equations documented in src/Equations.py

- Parameter descriptions in src/vars.py

## Contributing

- Fork the repository

- Create a new branch (git checkout -b feature-branch)

- Commit your changes (git commit -am 'Add new feature')

- Push to the branch (git push origin feature-branch)

- Create a new Pull Request

## License

Refer to the LICENSE file for details.

## References

- BSIM3v3.2 Manual (included in source/pdf)

- Liu, W. (2001). MOSFET Models for SPICE Simulation: Including BSIM3v3 and BSIM4. Wiley.

- Tsividis, Y. (1999). Operation and Modeling of the MOS Transistor. Oxford University Press.
---

Developed by  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mohamed_Gueni-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/mgueni/)  
[![GitHub Repo](https://img.shields.io/badge/GitHub-BSIM3v3_Python_Implementation-blue?style=flat&logo=github)](https://github.com/Gueni/BSIM3v3-Python-Implementation)