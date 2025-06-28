#!/usr/bin/env python
# coding=utf-8
import numpy as np
import matplotlib.pyplot as plt

class Simplified_BSIM3_Model:
    """Simplified MOSFET model with constant values replacing complex calculations"""
    
    def __init__(self):
        # Realistic parameters for power MOSFET
        self.Vth = 3.0       # Threshold voltage (V) - Higher for power devices
        self.mu = 0.015      # Mobility (m²/V·s) - Lower due to high doping
        self.Cox = 5e-3      # Oxide capacitance (F/m²) - Thicker gate oxide
        self.W = 1e-2        # Channel width (m) - Much wider for high current
        self.L = 1e-6        # Channel length (m) - Short but not minimum
        self.lambda_ch = 0.05 # Channel length modulation - Lower for power devices
        self.Vsat = 1e5      # Saturation velocity (m/s) - Higher for power devices
        self.Vbi = 0.8       # Built-in potential (V)
        self.Phi_s = 0.9     # Surface potential (V)
        self.Xdep = 2e-6     # Depletion width (m) - Wider for high voltage
        self.Ab = 1.2        # Bulk charge effect coefficient
        self.Rds_on = 0.1    # On-resistance (Ω) - Key parameter for power MOSFETs
        self.n = 2.0         # Subthreshold slope factor
        self.Voff = -1.0     # Offset voltage (V)
    
    def calculate_Vgsteff(self, Vgs):
        """Simplified effective gate voltage calculation"""
        Vgst = Vgs - self.Vth
        if Vgst <= 0:
            return 0
        return Vgst  # Simple approximation
    
    def calculate_Vdsat(self, Vgs):
        """Simplified saturation voltage calculation"""
        return self.calculate_Vgsteff(Vgs)  # Simple approximation
    
    def calculate_linear_current(self, Vgs, Vds):
        """Simple linear region current calculation"""
        Vgsteff = self.calculate_Vgsteff(Vgs)
        if Vgsteff <= 0:
            return 0
        return self.mu * self.Cox * (self.W/self.L) * ((Vgsteff * Vds) - (Vds**2)/2)
    
    def calculate_saturation_current(self, Vgs, Vds):
        """Simple saturation region current calculation"""
        Vgsteff = self.calculate_Vgsteff(Vgs)
        if Vgsteff <= 0:
            return 0
        Vdsat = self.calculate_Vdsat(Vgs)
        Idsat = self.mu * self.Cox * (self.W/self.L) * (Vgsteff**2)/2
        return Idsat * (1 + self.lambda_ch * (Vds - Vdsat))
    
    def calculate_subthreshold_current(self, Vgs, Vds):
        """Simple subthreshold current calculation"""
        Vgst = Vgs - self.Vth
        if Vgst > 0:
            return 0
        I_s0 = 1e-9  # Arbitrary scaling factor
        return I_s0 * np.exp((Vgst - self.Voff) / (self.n * 0.025)) * (1 - np.exp(-Vds / 0.025))
    
    def compute(self, Vgs, Vds):
        """Calculate drain current for given bias conditions"""
        Vgsteff = self.calculate_Vgsteff(Vgs)
        
        if Vgsteff <= 0:  # Subthreshold region
            return self.calculate_subthreshold_current(Vgs, Vds)
        else:
            Vdsat = self.calculate_Vdsat(Vgs)
            if Vds < Vdsat:  # Linear region
                return self.calculate_linear_current(Vgs, Vds)
            else:  # Saturation region
                return self.calculate_saturation_current(Vgs, Vds)

if __name__ == "__main__":
    model = Simplified_BSIM3_Model()
    
    # Voltage ranges
    vds_range = np.linspace(0, 5, 100)  # Drain-source voltage range
    vgs_range = np.linspace(0, 5, 6)    # Gate-source voltage range (for Id-Vds plot)
    vgs_fine = np.linspace(-0.5, 5, 100)  # Fine Vgs range (for Id-Vgs plot)
    
    # Plot Id-Vds characteristics
    plt.figure(figsize=(10, 6))
    for vgs in vgs_range:
        ids = [model.compute(vgs, vds) for vds in vds_range]
        plt.plot(vds_range, ids, label=f'Vgs={vgs:.1f}V')
    
    plt.title('Simplified MOSFET I-V Characteristics')
    plt.xlabel('Drain-Source Voltage (V)')
    plt.ylabel('Drain Current (A)')
    plt.grid(True)
    plt.legend()
    plt.show()
    
    # Plot Id-Vgs characteristics (log scale)
    plt.figure(figsize=(10, 6))
    ids_vgs = [model.compute(vgs, 0.1) for vgs in vgs_fine]  # Small Vds
    plt.semilogy(vgs_fine, np.maximum(1e-20, ids_vgs))
    plt.title('Simplified MOSFET Transfer Characteristics')
    plt.xlabel('Gate-Source Voltage (V)')
    plt.ylabel('Drain Current (A)')
    plt.grid(True, which="both", ls="-")
    plt.show()