#!/usr/bin/env python
# coding=utf-8
from matplotlib import pyplot as plt
import numpy as np

class BSIM3v3_Model:
    """BSIM3v3 MOSFET model with simplified intermediate calculations."""
    
    def __init__(self):
        # Physical constants (SI units)
        self.epsSi = 11.7 * 8.854e-12      # F/m, Silicon permittivity
        self.epsOx = 3.9 * 8.854e-12       # F/m, Silicon dioxide permittivity
        self.q = 1.602e-19                 # C, Electron charge
        self.k_B = 1.38e-23                # J/K, Boltzmann constant
        self.epsSi    = 11.7 * 8.854e-12            # F/m,   Silicon permittivity
        self.epsOx    = 3.9 * 8.854e-12             # F/m,   Silicon dioxide permittivity
        self.q        = 1.602e-19                   # C,     Electron charge
        self.k_B      = 1.38e-23                    # J/K,   Boltzmann constant
        # Threshold voltage related parameters
        self.Vth0     = 0.40                        # V,     Zero-bias threshold voltage
        self.K1       = 0.5                         # √V,    First body effect coefficient
        self.K2       = 0.01                        # -,     Second body effect coefficient
        self.K3       = 80.0                         # -,     Narrow width effect coefficient
        self.K3b      = 0                       # -,     Body effect on narrow width coefficient
        self.Dvt0     = 2.2                         # -,     Short-channel effect coefficient at Vbs=0
        self.Dvt1     = 0.53                         # -,     Short-channel effect coefficient
        self.Dvt2     = -0.032                       # 1/V,   Short-channel effect coefficient for body bias
        self.Dvt0w    = 0.0                         # -,     Narrow width effect coefficient at Vbs=0
        self.Dvt1w    = 5.3e6                       # -,     Narrow width effect coefficient
        self.Dvt2w    = -0.032                      # 1/V,   Narrow width effect coefficient for body bias
        self.Nlx      = 1.47e-7                      # m,     Lateral non-uniform doping parameter
        self.W0       = 2.5e-6                      # m,     Narrow width parameter

        # Mobility parameters (180nm NMOS)
        self.mobMod   = 3                           # -,     Mobility model selector
        self.U0       = 0.067                        # m2/V·s, Low-field mobility
        self.Ua       = 2.25E-9                       # m/V,   First-order mobility degradation coefficient
        self.Ub       = 5.87E-19                       # (m/V)2, Second-order mobility degradation coefficient
        self.Uc       = -0.046                        # -,     Body-effect coefficient for mobility degradation mobMod =1, 2:-4.65e-11 mobMod=3:-0.046
        # Velocity saturation parameters
        self.VSAT     = 8.0E4                       # m/s,   Saturation velocity
        self.A0       = 1.0                         # -,     Bulk charge effect coefficient
        self.A1       = 0.0                        # -,     Saturation voltage parameter
        self.A2       = 1.0                         # -,     Saturation voltage parameter
        self.B0       = 0.0                      # -,     Width effect on Abulk
        self.B1       = 0.0                     # -,     Width effect on Abulk
        # Output resistance parameters
        self.Pclm     = 1.3                         # -,     Channel length modulation coefficient
        self.Pdiblc1   = 0.5                         # -,     DIBL coefficient for output resistance
        self.Pdiblc2   = 0.39                        # -,     DIBL coefficient for output resistance
        self.Pdiblb   =  0.0                       # -,     Body effect on DIBL for output resistance
        self.Drout    = 0.56                         # -,     Output resistance DIBL coefficient
        self.Pvag     = 0.0                       # 1/V,   Gate voltage effect on output resistance
        self.Alpha0   = 0.01                        # -,     Substrate current parameter
        self.Alpha1   = 0.01                        # -,     Substrate current parameter
        self.Beta0    = 30.0                        # V/m,   Substrate current parameter
        # DIBL and substrate effect parameters
        self.Dsub     = self.Drout                         # -,     DIBL coefficient in subthreshold region
        self.Eta0     = 0.08                         # -,     DIBL coefficient in strong inversion
        self.Etab     = -0.07                       # -,     Body bias effect on DIBL coefficient
        # Geometry parameters (180nm process)
        self.Leff     = 180e-9                      # m,     Effective channel length
        self.Weff     = 1e-6                        # m,     Effective channel width (1um)
        self.Ldrawn   = 180e-9                      # m,     Drawn channel length
        self.Wdrawn   = 1e-6                        # m,     Drawn channel width
        self.Xj       = 100e-9                      # m,     Junction depth
        self.Tox      = 2.0e-9                      # m,     Oxide thickness
        self.Toxm     = 2.0e-9                      # m,     Oxide thickness for modeling
        # Doping concentrations
        self.Nch      = 1.0e23                      # m-3,   Channel doping concentration
        self.Ngate    = 1e25                        # m-3,   Poly doping concentration
        self.Nds      = 1e26                        # m-3,   Source/drain doping concentration
        # Parasitic resistance
        self.Rds      = 50.0                        # ohm,     Source-drain resistance
        # Subthreshold parameters
        self.n        = 1.5                         # -,     Subthreshold swing coefficient
        self.Voff     = -0.08                       # V,     Offset voltage for subthreshold current
        self.Keta     = -0.047                      # -,     Body effect coefficient for Voff
        self.delta    = 0.01                        # -,     Smoothing parameter for Voff
        # Temperature parameters
        self.Tnom     = 300.0                       # K,     Nominal temperature
        self.Kt1      = -0.15                       # V,     Temperature coefficient for Vth
        self.Kt1l     = 1e-9                        # V·m,   Temperature coefficient for Vth
        self.Kt2      = 0.03                        # -,     Temperature coefficient for Vth
        self.Ute      = -1.8                        # -,     Mobility temperature exponent
        self.At       = 4.0e4                       # m/s,   Velocity saturation temperature coefficient
        self.Ags      = 0.0                         # -,     Body effect coefficient for bulk charge
        # Additional parameters
        self.Pscbe1   = 4.24E8                      # -,     Substrate current body-effect coefficient 1
        self.Pscbe2   = 1.0E-5                      # -,     Substrate current body-effect coefficient 2
        # State variables
        self.Cit      = 0.0                         # F/m2,  Interface trap capacitance
        self.Citd     = 0                         # F/m2,  Interface trap capacitance derivative
        self.Citb     = 0                         # F/m2,  Interface trap capacitance body effect
        self.Nfactor  = 0                        # -,     Subthreshold slope factor
        self.NI0      = 1.45e16                     # m-3,   Intrinsic carrier concentration at 300K
        self.NITEXP   = 1.5                         # -,     Exponent for temperature dependence of ni
        self.Cox      = self.epsOx / self.Tox       # F/m², Oxide capacitance per unit area
        self.Cdsc     = 0                       # Axial capacitance (F)
        self.Cdscd    = 0                       # Drain-bias sensitivity of Cdsc F/Vm2
        self.Cdscb    = 0                       # Body-bias sensitivity of Cdsc F/Vm2
        # Model parameters for 180nm NMOS
        self.Vth0 = 0.40                   # V, Zero-bias threshold voltage
        self.K1 = 0.5                      # √V, First body effect coefficient
        self.K2 = 0.01                     # -, Second body effect coefficient
        self.K3 = 80.0                     # -, Narrow width effect coefficient
        self.K3b = 0                       # -, Body effect on narrow width coefficient
        self.Dvt0 = 2.2                    # -, Short-channel effect coefficient
        self.Dvt1 = 0.53                   # -, Short-channel effect coefficient
        self.Dvt2 = -0.032                 # 1/V, Short-channel effect coefficient
        self.Dvt0w = 0.0                   # -, Narrow width effect coefficient
        self.Dvt1w = 5.3e6                 # -, Narrow width effect coefficient
        self.Dvt2w = -0.032                # 1/V, Narrow width effect coefficient
        self.Nlx = 1.47e-7                 # m, Lateral non-uniform doping parameter
        self.W0 = 2.5e-6                  # m, Narrow width parameter
        self.U0 = 0.067                    # m²/V·s, Low-field mobility
        self.VSAT = 8.0e4                  # m/s, Saturation velocity
        self.A0 = 1.0                      # -, Bulk charge effect coefficient
        self.Pclm = 1.3                    # -, Channel length modulation coefficient
        self.Pdiblc1 = 0.5                 # -, DIBL coefficient
        self.Pdiblc2 = 0.39                # -, DIBL coefficient
        self.Drout = 0.56                  # -, Output resistance DIBL coefficient
        self.Leff = 180e-9                 # m, Effective channel length
        self.Weff = 1e-6                   # m, Effective channel width
        self.Tox = 2.0e-9                  # m, Oxide thickness
        self.Toxm = 2.0e-9                 # m, Oxide thickness for modeling
        self.Nch = 1.0e23                  # m⁻³, Channel doping concentration
        self.Nds = 1e26                    # m⁻³, Source/drain doping
        self.Rds = 50.0                    # Ω, Source-drain resistance
        self.n = 1.5                       # -, Subthreshold swing coefficient
        self.Voff = -0.08                  # V, Offset voltage for subthreshold
        self.Tnom = 300.0                  # K, Nominal temperature
        self.Kt1 = -0.15                   # V, Temperature coefficient for Vth
        self.Kt1l = 1e-9                   # V·m, Temperature coefficient for Vth
        self.Kt2 = 0.03                    # -, Temperature coefficient for Vth
        
        # Pre-calculated constant values (originally from functions)
        self.Phi_s = 0.9                   # V, Surface potential (fixed)
        self.Xdep = 1e-7                   # m, Depletion width (fixed)
        self.Xdep0 = 1e-7                  # m, Zero-bias depletion width (fixed)
        self.Vbi = 1.0                     # V, Built-in potential (fixed)
        self.ni = 1.45e16                  # m⁻³, Intrinsic carrier concentration (fixed)
        self.v_t = 0.026                   # V, Thermal voltage at 300K (fixed)
        self.Abulk = 1.1                    # -, Bulk charge effect coefficient (fixed)
        self.Vgsteff = 0.5                  # V, Effective gate overdrive (fixed)
        self.Vdsat = 0.5                    # V, Saturation voltage (fixed)
        self.Vdseff = 0.5                   # V, Effective drain voltage (fixed)
        self.mob_eff = 0.05                 # m²/V·s, Effective mobility (fixed)

    def calculate_V_th(self, Vds, Vbs, T):
        """Calculate threshold voltage (Vth) with simplified intermediate calculations."""
        # Temperature effect
        delta_T = (T / self.Tnom) - 1
        temp_effect = (self.Kt1 + self.Kt1l/self.Leff + self.Kt2 * Vbs) * delta_T
        
        # Body effect
        body_effect = self.K1 * np.sqrt(self.Phi_s - Vbs) - self.K2 * Vbs
        
        # Short-channel effects
        sc_effect = -self.Dvt0 * np.exp(-self.Dvt1 * self.Leff/(2*1e-7)) * (self.Vbi - self.Phi_s)
        
        # Narrow width effect
        nw_effect = (self.K3 + self.K3b * Vbs) * (self.Tox/(self.Weff + self.W0)) * self.Phi_s
        
        # DIBL effect
        dibl_effect = -(self.Eta0 + self.Etab * Vbs) * Vds
        
        # Combine all effects
        Vth = self.Vth0 + body_effect + sc_effect + nw_effect + dibl_effect + temp_effect
        return Vth

    def compute(self, Vgs, Vds, Vbs=0.0, T=300.0):
        """Calculate drain current with simplified intermediate calculations."""
        Vth = self.calculate_V_th(Vds, Vbs, T)
        Vgst = Vgs - Vth
        
        # Subthreshold region
        if Vgst <= 0:
            I_ds = (self.U0 * self.Cox * self.Weff/self.Leff * 
                   np.square(self.v_t) * np.exp((Vgst - self.Voff)/(self.n * self.v_t))) * (1 - np.exp(-Vds/self.v_t))
        
        # Linear region
        elif Vds < self.Vdsat:
            I_dso = (self.U0 * self.Cox * (self.Weff/self.Leff) * 
                    Vgst * Vds * (1 - Vds/(2 * self.Abulk * (Vgst + 2*self.v_t))))
            I_ds = I_dso / (1 + self.Rds * I_dso / max(1e-6, Vds))
        
        # Saturation region
        else:
            I_dsat = (self.Weff * self.VSAT * self.Cox * 
                     (Vgst - self.Abulk * self.Vdsat))
            I_ds = I_dsat * (1 + (Vds - self.Vdsat)/5.0)  # Simplified CLM effect
        
        return I_ds


if __name__ == "__main__":
    model = BSIM3v3_Model()
    
    # Test parameters
    vds_range = np.linspace(0, 1.0, 50)
    vgs_range = np.linspace(0, 1.0, 50)
    
    # Test 1: Id vs Vgs for different Vds
    plt.figure(figsize=(10, 6))
    for vds in [0.1, 0.5, 1.0]:
        ids = [model.compute(vgs, vds) for vgs in vgs_range]
        plt.plot(vgs_range, ids, label=f'Vds={vds}V')
    
    plt.title('Drain Current vs Gate-Source Voltage')
    plt.xlabel('Vgs (V)')
    plt.ylabel('Id (A)')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Test 2: Id vs Vds for different Vgs
    plt.figure(figsize=(10, 6))
    for vgs in [0.3, 0.5, 0.7, 1.0]:
        ids = [model.compute(vgs, vds) for vds in vds_range]
        plt.plot(vds_range, ids, label=f'Vgs={vgs}V')
    
    plt.title('Drain Current vs Drain-Source Voltage')
    plt.xlabel('Vds (V)')
    plt.ylabel('Id (A)')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Test 3: Vth vs Vds
    vth_vds = [model.calculate_V_th(vds, 0, 300) for vds in vds_range]
    plt.figure(figsize=(10, 6))
    plt.plot(vds_range, vth_vds)
    plt.title('Threshold Voltage vs Drain-Source Voltage')
    plt.xlabel('Vds (V)')
    plt.ylabel('Vth (V)')
    plt.grid(True)
    plt.show()