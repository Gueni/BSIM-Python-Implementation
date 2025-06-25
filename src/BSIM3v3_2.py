#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                 ______  ____  _______  _____
#?                / __ \ \/ /  |/  / __ \/ ___/
#?               / /_/ /\  / /|_/ / / / /\__ \
#?              / ____/ / / /  / / /_/ /___/ /
#?             /_/     /_/_/  /_/\____//____/
#?
#? Name:        BSIM3v3_2.py
#? Purpose:     Compute drain current using the BSIM model
#?
#? Author:      Mohamed Gueni (mohamedgueni@outlook.com)
#? Based on:    BSIM3v3_2 Manual 
#? Created:     21/05/2025
#? Licence:     Refer to the LICENSE file
#? -------------------------------------------------------------------------------
from matplotlib import pyplot as plt
import numpy as np
#? -------------------------------------------------------------------------------
class BSIM3v3_Model:
    """BSIM3v3 MOSFET model implementation for circuit simulation.
    
    This class implements the BSIM3v3 (Berkeley Short-channel IGFET Model) version 3.3
    for MOSFET transistors. It calculates drain current (Ids) and other characteristics
    based on the given terminal voltages and physical parameters.
    
    The model includes:
    - Threshold voltage calculation with short-channel, narrow width, and DIBL effects :Drain-Induced Barrier Lowering (DIBL)
    - Mobility degradation effects
    - Velocity saturation
    - Channel length modulation
    - Subthreshold conduction
    - Temperature effects
    - Parasitic resistance effects
    
    Attributes:
        Various physical constants and model parameters initialized in __init__
    """
    
    def __init__(self):
        """Initialize BSIM3v3 model with default parameters for 180nm NMOS transistor.
        
        Sets up:
        - Physical constants (permittivity, charge, etc.)
        - Threshold voltage related parameters
        - Mobility parameters
        - Velocity saturation parameters
        - Output resistance parameters
        - Geometry parameters
        - Doping concentrations
        - Temperature parameters
        - Subthreshold parameters
        """
        # Physical constants (SI units)
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
        self.Ua1       = 4.31E-9                       # m/V,   First-order mobility degradation coefficient
        self.Ub1       = -7.61E-18                       # (m/V)2, Second-order mobility degradation coefficient
        self.Uc1       = -0.056                        # -,     Body-effect coefficient for mobility degradation mob-Mod=1,2:-5.6E-11 mob-Mod=3:-0.056
        # Velocity saturation parameters
        self.VSAT     = 8.0E4                       # m/s,   Saturation velocity
        self.A0       = 1.0                         # -,     Bulk charge effect coefficient
        self.A1       = 0.0                        # -,     Saturation voltage parameter
        self.A2       = 1.0                         # -,     Saturation voltage parameter
        self.B0       = 0.0                      # -,     Width effect on Abulk
        self.B1       = 0.0                     # -,     Width effect on Abulk
        # DIBL and substrate effect parameters
        self.Pclm     = 1.3                         # -,     Channel length modulation coefficient
        self.Drout    = 0.56                         # -,     Output resistance DIBL coefficient
        self.Pvag     = 0.0                       # 1/V,   Gate voltage effect on output resistance
        self.Alpha0   = 1.2e-6                        # -,     Substrate current parameter
        self.Alpha1   = 0.5e-6                        # -,     Substrate current parameter
        self.Beta0    = 3.0                        # V/m,   Substrate current parameter
        self.Dvt0 = 2.5            # Increased from 2.2 (short-channel effect coefficient)
        self.Dvt1 = 0.6            # Increased from 0.53
        self.Dsub = 1.2            # Increased from 0.56 (DIBL in subthreshold)
        self.Eta0 = 0.15           # Increased from 0.08 (DIBL in strong inversion)
        self.Etab = -0.12          # Increased from -0.07 (body effect on DIBL)
        self.Pdiblc1 = 0.45        # Adjusted DIBL coefficient
        self.Pdiblc2 = 0.45        # Matched to Pdiblc1
        self.Pdiblb = -0.08        # Added body bias effect on DIBL
        # Geometry parameters (180nm process)
        self.Leff     = 180e-9                      # m,     Effective channel length
        self.Weff     = 1e-6                        # m,     Effective channel width (1um)
        self.Ldrawn   = 180e-9                      # m,     Drawn channel length
        self.Wdrawn   = 1e-6                        # m,     Drawn channel width
        self.Xj       = 100e-9                      # m,     Junction depth
        self.Tox      = 1.0e-9                      # m,     Oxide thickness
        self.Toxm     = 1.0e-9                      # m,     Oxide thickness for modeling
        self.Wint     = 0.0                         # m,     Internal width for narrow width effects
        self.Wl       = 0.0                         # m,     Length dependence coefficient for width
        self.Ww       = 0.0                         # m,     Width dependence coefficient for width
        self.Wln      = 0.0                         # -,     Length dependence exponent for width
        self.Wwn      = 0.0                         # -,     Width dependence exponent for width
        self.Lint     = 0.0                         # m,     Internal length for narrow width effects
        self.Ll       = 0.0                         # m,     Length dependence coefficient for length
        self.Lw       = 0.0                         # m,     Width dependence coefficient for length
        self.Lln      = 0.0                         # -,     Length dependence exponent for length
        self.Lwn      = 0.0                         # -,     Width dependence exponent for length
        self.dW       = self.Wint + self.Wl/self.Ldrawn**self.Wln + self.Ww/self.Wdrawn**self.Wwn
        self.dL       = self.Lint + self.Ll/self.Ldrawn**self.Lln + self.Lw/self.Wdrawn**self.Lwn
        self.Leff     = max(180e-9, self.Ldrawn - 2*self.dL)  # Prevent negative values
        self.Weff     = max(180e-9, self.Wdrawn - 2*self.dW)
        # Doping concentrations
        self.Nch      = 1.0e23                      # m-3,   Channel doping concentration
        self.Ngate    = 1e25                        # m-3,   Poly doping concentration
        self.Nds      = 1e26                        # m-3,   Source/drain doping concentration
        # Parasitic resistance
        self.Rdsw     = 50.0                       # Typical value might be in the range of 50-200 ohm·µm for modern processes
        self.Pr       = 1.0          # Could range from 0.5 to 2.0 depending on technology
        self.Wr       = 1.0          # Often kept at 1.0 (linear width dependence)
        self.Prwb     = 0.1        # Small value for body effect
        self.Prwg     = 0.0       # Small value for gate voltage effect
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


    def ni(self, T):
        """Calculate intrinsic carrier concentration (ni) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Intrinsic carrier concentration in m^-3
        """
        ni = self.NI0 * (T / self.Tnom) ** self.NITEXP
        return ni
    
    def v_t(self, T):
        """Calculate thermal voltage (Vt) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Thermal voltage in volts
        """
        return self.k_B * T / self.q
    
    def Phi_s(self, T):
        """Calculate surface potential (Phi_s) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Surface potential in volts
        """
        Phi_s = 2 * self.v_t(T) * np.log(self.Nch / self.ni(T))
        return Phi_s
    
    def Xdep0(self, T):
        """Calculate zero-bias depletion width based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Zero-bias depletion width in meters
        """
        Xdep0 = np.sqrt(2 * self.epsSi * self.Phi_s(T) / (self.q * self.Nch))
        return Xdep0
        
    def Vbi(self, T):
        """Calculate built-in potential (Vbi) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Built-in potential in volts
        """
        vbi = self.v_t(T) * np.log((self.Nch * self.Nds) / np.square(self.ni(T)))
        return vbi
   
    def calculate_Rds(self, Vds, Vgs, Vbs, T):
        """Calculate bias-dependent source/drain resistance."""
        Vgsteff     = self.calculate_Vgsteff(Vgs, T, Vds, Vbs)  # Recalculate Vgsteff for consistency
        Rds         = self.Rdsw_T_dependent(T) * (1 + self.Prwg * Vgsteff + self.Prwb*(np.sqrt(self.Phi_s(T)-Vbs) - np.sqrt(self.Phi_s(T))))/(1e6*self.Weff)**self.Wr
        return Rds

    def Rdsw_T_dependent(self, T):
        """Calculate temperature-dependent source/drain resistance (Rdsw)."""
        # Source/drain resistance temperature dependence
        Rdsw = self.Rdsw + self.Pr * (T / self.Tnom - 1)
        return Rdsw
         
    def calculate_V_th(self, Vds, Vbs, T):
        """Calculate threshold voltage (Vth) based on BSIM3v3 model (Eq. 2.1.25).
        
        Includes:
        - Body effect
        - Short-channel effects
        - Narrow width effects
        - DIBL effects
        - Temperature effects
        
        Args:
            Vds (float): Drain-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Threshold voltage in volts
        """
        
        # Effective body-source voltage with smoothing (Eq. 2.1.26)
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        # Depletion widths and characteristic lengths
        self.Xdep   = np.sqrt(2 * self.epsSi * (self.Phi_s(T) - Vbseff) / (self.q * self.Nch))
        lt0         = np.sqrt(self.epsSi * self.Xdep * self.Tox / self.epsOx)
        ltw         = np.sqrt(self.epsSi * self.Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2w * Vbseff)))
        lt          = np.sqrt(self.epsSi * self.Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2 * Vbseff)))
        # Scale K1 and K2 for oxide thickness (Eq. 2.1.25)
        K1ox        = self.K1 * (self.Tox / self.Toxm)
        K2ox        = self.K2 * (self.Tox / self.Toxm)
        Vth0ox      = self.Vth0 - K1ox * np.sqrt(self.Phi_s(T))
        # Calculate all terms of threshold voltage (Eq. 2.1.25)
        term1       = Vth0ox + K1ox * np.sqrt(self.Phi_s(T) - Vbseff) - K2ox * Vbseff
        term2       = K1ox * (np.sqrt(1 + self.Nlx/self.Leff) - 1) * np.sqrt(self.Phi_s(T))
        term3       = (self.K3 + self.K3b * Vbseff) * (self.Tox / (self.Weff + self.W0)) * self.Phi_s(T)
        term4       = -self.Dvt0w * (np.exp(-self.Dvt1w * self.Weff * self.Leff/(2 * ltw)) + 2 * np.exp(-self.Dvt1w * self.Weff * self.Leff/ltw)) * (self.Vbi(T) - self.Phi_s(T))
        term5       = -self.Dvt0 * (np.exp(-self.Dvt1 * self.Leff/(2 * lt)) + 2 * np.exp(-self.Dvt1 * self.Leff/lt)) * (self.Vbi(T) - self.Phi_s(T))
        term6       = -(np.exp(-self.Dsub * self.Leff/(2 * lt0)) + 2 * np.exp(-self.Dsub * self.Leff/lt0)) * (self.Eta0 + self.Etab * Vbseff) * Vds
        # Temperature effect on threshold voltage
        delta_T     = (T / self.Tnom) - 1
        term7       = (self.Kt1 + self.Kt1l/self.Leff + self.Kt2 * Vbseff) * delta_T
        Vth    = term1 + term2 + term3 + term4 + term5 + term6 + term7

        #print(f"Vth: {Vth}, Vbseff: {Vbseff}, Xdep: {self.Xdep}, Tox: {self.Tox}, Toxm: {self.Toxm}")
        return Vth
    
    def vth_T_dependent(self,Vds, Vbs, T):
        """Calculate temperature-dependent threshold voltage (Vth) based on BSIM3v3 model."""
        Vth_TNOM    = self.calculate_V_th(Vds, Vbs, self.Tnom)
        Vth = (Vth_TNOM + (self.Kt1 + self.Kt1l/self.Leff + self.Kt2 * Vbs) * (T / self.Tnom - 1))
        return Vth
    
    def calculate_mobility(self, Vgs, T,Vds, Vbs):
        """Calculate effective mobility including degradation effects (Eq. 3.2.1-3.2.3).
        
        Includes:
        - Vertical field mobility degradation
        - Temperature effects
        - Body effect on mobility
        
        Args:
            Vgs (float): Gate-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Effective mobility in m²/V·s
        """
        Vth         = self.vth_T_dependent(Vds, Vbs, T)  
        Vgsteff     = self.calculate_Vgsteff(Vgs, T, Vds, Vbs)  
        # Temperature effect on mobility
        U0_T    = self.U0 * (T/self.Tnom)**self.Ute 
        # self.Ua = self.Ua + self.Ua1 * (T / self.Tnom - 1)
        # self.Ub = self.Ub + self.Ub1 * (T / self.Tnom - 1)
        # self.Uc = self.Uc + self.Uc1 * (T / self.Tnom - 1)

        # Mobility degradation models
        if self.mobMod == 1:
            # Vertical field mobility degradation model (Eq. 3.2.1)
            denom = 1 + (self.Ua + self.Uc * Vbs) *             \
                    ((Vgsteff + 2*Vth)/self.Tox) +                      \
                    self.Ub * np.square((Vgsteff + 2*Vth)/self.Tox)
            
        elif self.mobMod == 2:  # To account for depletion mode devices, another mobility model option is given by the following
            denom = 1 + (self.Ua + self.Uc * Vbs) *             \
                    (Vgsteff/self.Tox) +                                \
                    self.Ub * np.square(Vgsteff/self.Tox)
        else:  # To consider the body bias dependence of Eq. 3.2.1 further, we have introduced the following expression
            denom = 1 + (self.Ua * ((Vgsteff + 2*Vth)/self.Tox) +       \
                    self.Ub * np.square((Vgsteff + 2*Vth)/self.Tox)) *  \
                    (1 + self.Uc * Vbs)
       
        mob_eff   = U0_T / denom
        # print(f"Vgs: {Vgs}, Vbs: {Vbs}, T: {T}, Vgsteff: {Vgsteff}, Vth: {Vth}, mob_eff: {mob_eff}")
        return mob_eff
    
    def calculate_Vgsteff(self, Vgs,T,Vds, Vbs):
        """Calculate effective Vgs-Vth including subthreshold smoothing (Eq. 3.1.3).
        
        Provides smooth transition between subthreshold and strong inversion regions.
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Effective gate overdrive voltage in volts
        """

        # Effective body-source voltage with smoothing (Eq. 2.1.26)
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        Cd = self.epsSi / self.Xdep0(T)
        lt          = np.sqrt(self.epsSi * self.Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2 * Vbseff)))
        # Calculate the exponential terms
        term1 = np.exp(-self.Dvt1 * self.Leff / (2 * lt))
        term2 = np.exp(-self.Dvt1 * self.Leff / (lt))
        
        # Calculate the main equation
        n = 1 + self.Nfactor * (Cd/self.Cox) + \
            ((self.Cdsc+self.Cdscd*Vds+self.Cdscb*Vbseff) *(term1+2*term2))/self.Cox +\
            self.Cit/self.Cox
        
        Vth             = self.vth_T_dependent(Vds, Vbseff, T)  
        Vgst            = Vgs - Vth
        nom             = 2 * n * self.v_t(T) * np.log(1 + np.exp(Vgst / (2 * n * self.v_t(T))))
        denom           = 1 + 2 * n * self.Cox * \
                          np.sqrt(2 * self.Phi_s(T) / (self.q * self.epsSi * self.Nch)) * \
                          np.exp(-(Vgst - 2 * self.Voff) / (2 * n * self.v_t(T)))
        Vgsteff         = nom / denom
        return Vgsteff

    def calculate_Vdsat(self, Vgs, Vbs, T,Vds):
        """Calculate saturation voltage (Vdsat) (Eq. 3.4.3).
        
        The voltage at which the channel reaches velocity saturation.
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Saturation voltage in volts
        """
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff      = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        Vgsteff     = self.calculate_Vgsteff(Vgs, T, Vds, Vbseff)  # Recalculate Vgsteff for consistency
        Esat        = 2 * self.Vsat_T_dependent(T) / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        Rds         = self.calculate_Rds(Vds, Vgs, Vbseff, T)  # Calculate bias-dependent source/drain resistance

        if Rds == 0:
            term1 = (Esat * self.Leff * (Vgsteff + 2 * self.v_t(T))) 
            term2 = (self.calculate_Abulk(T,Vbs) * Esat * self.Leff + Vgsteff + 2 * self.v_t(T))
            Vdsat = term1 / term2
        elif Rds > 0:

                lamda        = self.A1 * Vgsteff + self.A2

                term1        = self.calculate_Abulk(T,Vbs)**2 * self.Weff * self.Vsat_T_dependent(T) * self.Cox * Rds
                term2        = (1/lamda - 1) * self.calculate_Abulk(T,Vbs)
                a            = term1 + term2
                
                term3        = (Vgsteff + 2*self.v_t(T)) * (2/lamda - 1)
                term4        = self.calculate_Abulk(T,Vbs) * Esat * self.Leff
                term5        = 3 * self.calculate_Abulk(T,Vbs) * (Vgsteff + 2*self.v_t(T)) * self.Weff * self.Vsat_T_dependent(T) * self.Cox * Rds
                b            = -(term3 + term4 + term5)
                
                term6        = (Vgsteff + 2*self.v_t(T)) * Esat * self.Leff
                term7        = 2 * (Vgsteff + 2*self.v_t(T))**2 * self.Weff * self.Vsat_T_dependent(T) * self.Cox * Rds
                c            = term6 + term7
                
                # Calculate discriminant
                discriminant = b**2 - 4*a*c

                if discriminant < 0:
                    raise ValueError("Negative discriminant in Vdsat calculation")
                Vdsat        = (-b - np.sqrt(discriminant)) / (2*a)
    
        return Vdsat

    def Vsat_T_dependent(self,T):
        # Saturation velocity temperature dependence
        v_sat = self.VSAT - self.At * (T / self.Tnom - 1)
        return v_sat

    def calculate_Abulk(self, T,Vbs):
        """Calculate bulk charge effect coefficient (Abulk) (Eq. 2.4.1).
        
        Accounts for non-uniform channel doping effects on threshold voltage.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Bulk charge effect coefficient (unitless)
        """
        # Scale K1 and K2 for oxide thickness (Eq. 2.1.25)
        K1ox        = self.K1 * (self.Tox / self.Toxm)
        term1       = 1 + (K1ox / (2 * np.sqrt(self.Phi_s(T) - Vbs))) * (self.A0 * self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * self.Xdep))) * (1 - self.Ags * np.square(self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * self.Xdep))))
        term2       = (self.B0 / (self.Weff + self.B1)) / (1 + self.Keta * Vbs)
        self.Abulk  = term1 + term2
        return self.Abulk
    
    def calculate_Vdseff(self, Vds, Vgs, Vbs, T):
        """Calculate effective Vds including smoothing at Vdsat (Eq. 3.6.4).
        
        Provides smooth transition between linear and saturation regions.
        
        Args:
            Vds (float): Drain-source voltage in volts
            Vgs (float): Gate-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Effective drain-source voltage in volts
        """
        Vdsat       = self.calculate_Vdsat(Vgs, Vbs, T,Vds)
        Vdext       = Vdsat - 0.5 * (Vdsat - Vds - self.delta + np.sqrt(np.square(Vdsat - Vds - self.delta) + 4 * self.delta * Vdsat))
        Vdseff = Vdext - 0.5 * (Vdext - Vds - self.delta + np.sqrt(np.square(Vdext - Vds - self.delta) + 4 * self.delta * Vdext))
        return Vdseff
    
    def calculate_subthreshold_current(self, Vgs, Vds, T,Vbs):
        """Calculate subthreshold current (Eq. 2.7.1).
        
        Models the current when Vgs < Vth (weak inversion region).
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vds (float): Drain-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Subthreshold drain current in amperes
        """
        Vth     = self.vth_T_dependent(Vds, Vbs, T)  
        Vgst    = Vgs - Vth
        mob_eff = self.calculate_mobility(Vgs, T,Vds, Vbs)
        n       = 1 + (self.Cit + self.Citd * Vds + self.Citb * Vbseff) / self.Cox + self.Nfactor * self.epsSi / (self.Cox * self.Xdep)
        I_s0    = mob_eff * (self.Weff / self.Leff) * np.sqrt(self.q * self.epsSi * self.Nch * np.square(self.v_t(T)) / (2 * self.Phi_s(T)))
        I_sub   = I_s0 * (1 - np.exp(-Vds / self.v_t(T))) * np.exp((Vgst - self.Voff) / (n * self.v_t(T)))
        return I_sub
    
    def calculate_linear_current(self, Vds,Vgs, T,Vbs):
        """Calculate linear region current (triode region) (Eq. 3.3.4).
        
        Models the current when Vds < Vdsat.
        
        Args:
            Vds (float): Drain-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Drain current in amperes
        """
        Vgsteff = self.calculate_Vgsteff(Vgs, T, Vds, Vbs)  # Recalculate Vgsteff for consistency
        Esat     = 2 * self.Vsat_T_dependent(T) / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        Rds     = self.calculate_Rds(Vds, Vgs, Vbs, T)  # Calculate bias-dependent source/drain resistance
        mob_eff = self.calculate_mobility(Vgs, T,Vds, Vbs)
        Vb      = (Vgsteff + 2 * self.v_t(T)) / self.calculate_Abulk(T,Vbs)
        I_dso   = mob_eff * self.Cox * (self.Weff / self.Leff) * Vgsteff * Vds * (1 - Vds / (2 * Vb)) / (1 + Vds / (Esat * self.Leff))
        Qchs0 = self.Cox * Vgsteff
        # Add source-drain resistance effect (Eq. 3.3.5)
        if Rds == 0:
            # Handle the case where Vds is zero (maybe return 0 or a small value)
            I_ds  = (self.Weff * mob_eff * Qchs0 * Vds * (1 - Vds / (2 * Vb))) / (self.Leff * (1 + Vds / (Esat * self.Leff)))
        elif Rds > 0:
            I_ds = I_dso / (1 + Rds * I_dso / Vds) #Extrinsic Case (Rds > 0)

        if Vds == 0: 
            I_ds = 0

        return I_ds
    
    def calculate_saturation_current(self, Vgs, Vds, Vbs, T):
        """Calculate saturation region current (Eq. 3.5.1).
        
        Models the current when Vds > Vdsat, including:
        - Channel length modulation
        - DIBL effects
        - Substrate current induced body effect
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vds (float): Drain-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Drain current in amperes
        """
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff      = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        Vgsteff     = self.calculate_Vgsteff(Vgs, T)
        self.lit    = np.sqrt(self.epsSi * self.Xj * self.Tox / self.epsOx) #Calculate intrinsic length (lit) for short-channel effects.
        Vdsat       = self.calculate_Vdsat(Vgs, Vbseff, T)
        lamda       = self.A1 * Vgsteff + self.A2
        Esat        = 2 * self.Vsat_T_dependent(T) / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        Rds         = self.calculate_Rds(Vds, Vgs, Vbseff, T)  # Calculate bias-dependent source/drain resistance

        # Calculate 1/VASCRE (Equation 3.5.7)
        inv_VASCBE      =   (self.Pscbe2 / self.Leff) * np.exp((-self.Pscbe1*self.lit) / (Vds - Vdsat))
        VASCBE          =   1 / inv_VASCBE

        theta_rout      =   self.Pdiblc1 * (
                            np.exp(-self.Drout * self.Leff / (2 * self.lit)) + 
                            2 * np.exp(-self.Drout * self.Leff / self.lit)
                            ) + self.Pdiblc2

        VADIBLC         =   (Vgsteff + 2 * self.v_t(T)) / (theta_rout * (1 + self.Pdiblb * Vbseff)) *        \
                            (1 - ((self.calculate_Abulk(T,Vbs) * Vdsat) / (self.calculate_Abulk(T,Vbs) * Vdsat + Vgsteff + 2 * self.v_t(T))))

        VACLM           =   ((self.calculate_Abulk(T,Vbs) * Esat * self.Leff + Vgsteff) / (self.Pclm * self.calculate_Abulk(T,Vbs) * Esat * self.lit)) * \
                            (Vds - Vdsat)

        VAsat           =   ((Esat * self.Leff) + Vdsat + (2 * Rds * self.Vsat_T_dependent(T) * self.Cox * self.Weff * Vgsteff) * \
                            (1 - ((self.calculate_Abulk(T,Vbs) * Vdsat) / (2 * (Vgsteff + 2 * self.v_t(T)))))) / \
                            ((2/lamda) - 1 + (Rds * self.Vsat_T_dependent(T) * self.Cox * self.Weff * self.calculate_Abulk(T,Vbs)))

        VA              =   VAsat + (1 + ((self.Pvag * Vgsteff) / (Esat * self.Leff))) * ((1 / VACLM) + (1 / VADIBLC))**-1

        I_dsat          = self.Weff * self.VSAT * self.Cox * (Vgsteff - self.calculate_Abulk(T,Vbs) * Vdsat)
        denominator     = 1 + (Rds * I_dsat) / Vdsat
        first_term      = 1 + (Vds - Vdsat) / VA
        second_term     = 1 + (Vds - Vdsat) / VASCBE
        I_ds            = (I_dsat / denominator) * first_term * second_term
            
        return I_ds

    def Single_Current_Expression(self, Vgs, Vds, Vbs, T):
        """Single Current Expression for All Operating Regimes of Vgs and Vds"""
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff      = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        Vgsteff     = self.calculate_Vgsteff(Vgs, T)
        self.lit    = np.sqrt(self.epsSi * self.Xj * self.Tox / self.epsOx) #Calculate intrinsic length (lit) for short-channel effects.
        Vdsat       = self.calculate_Vdsat(Vgs, Vbseff, T)
        lamda       = self.A1 * Vgsteff + self.A2
        Esat        = 2 * self.Vsat_T_dependent(T) / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        Rds         = self.calculate_Rds(Vds, Vgs, Vbseff, T)  # Calculate bias-dependent source/drain resistance
        Vdsat       = self.calculate_Vdsat(Vgs, Vbs, T, Vds)
        Vdseff      = Vdsat - 1/2 * (Vdsat - Vds - delta + np.sqrt((Vdsat - Vds - delta)**2 + 4 * delta * Vdsat))
        # Calculate 1/VASCRE (Equation 3.5.7)
        inv_VASCBE  = (self.Pscbe2 / self.Leff) * np.exp((-self.Pscbe1*self.lit) / (Vds - Vdsat))
        VASCBE      = 1 / inv_VASCBE

        theta_rout  =   self.Pdiblc1 * (
                        np.exp(-self.Drout * self.Leff / (2 * self.lit)) + 
                        2 * np.exp(-self.Drout * self.Leff / self.lit)
                        ) + self.Pdiblc2
        VADIBLC     =   (Vgsteff + 2 * self.v_t(T)) / (theta_rout * (1 + self.Pdiblb * Vbseff)) *        \
                        (1 - ((self.calculate_Abulk(T,Vbs) * Vdsat) / (self.calculate_Abulk(T,Vbs) * Vdsat + Vgsteff + 2 * self.v_t(T))))

        VACLM       =   ((self.calculate_Abulk(T,Vbs) * Esat * self.Leff + Vgsteff) / (self.Pclm * self.calculate_Abulk(T,Vbs) * Esat * self.lit)) * \
                        (Vds - Vdsat)

        VAsat      =   ((Esat * self.Leff) + Vdsat + (2 * Rds * self.Vsat_T_dependent(T) * self.Cox * self.Weff * Vgsteff) * \
                        (1 - ((self.calculate_Abulk(T,Vbs) * Vdsat) / (2 * (Vgsteff + 2 * self.v_t(T)))))) / \
                        ((2/lamda) - 1 + (Rds * self.Vsat_T_dependent(T) * self.Cox * self.Weff * self.calculate_Abulk(T,Vbs)))
        VA         =   VAsat + (1 + ((self.Pvag * Vgsteff) / (Esat * self.Leff))) * ((1 / VACLM) + (1 / VADIBLC))**-1
        I_dsat      = self.Weff * self.VSAT * self.Cox * (Vgsteff - self.calculate_Abulk(T,Vbs) * Vdsat)
        Ids         = (I_dsat / (1 + (Rds * I_dsat) / Vdseff)) * \
                      (1 + (Vds - Vdseff) / VA) * \
                      (1 + (Vds - Vdseff) / VASCBE)
        
        return Ids

    def calculate_substrate_current(self,Vgs,Vds, Vbs, T):
        """
        Calculate substrate current (I_sub) based on BSIM3v3.2.1 model.
        
        Parameters:
        alpha_0, alpha_1, beta_0: Model parameters (impact ionization coefficients)
        L_eff: Effective channel length
        V_d: Drain voltage
        V_deqf: Effective drain voltage
        I_dio: Drain current
        R_d: Drain resistance
        
        Returns:
        Substrate current I_sub
        """
        # Calculate 1/VASCRE (Equation 3.5.7)
        Vgsteff     = self.calculate_Vgsteff(Vgs, T)
        lamda       = self.A1 * Vgsteff + self.A2
        self.lit    = np.sqrt(self.epsSi * self.Xj * self.Tox / self.epsOx) #Calculate intrinsic length (lit) for short-channel effects.
        Esat        = 2 * self.Vsat_T_dependent(T) / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        theta_rout  =   self.Pdiblc1 * (
                        np.exp(-self.Drout * self.Leff / (2 * self.lit)) + 
                        2 * np.exp(-self.Drout * self.Leff / self.lit)
                        ) + self.Pdiblc2
        VADIBLC     =   (Vgsteff + 2 * self.v_t(T)) / (theta_rout * (1 + self.Pdiblb * Vbseff)) *        \
                        (1 - ((self.calculate_Abulk(T,Vbs) * Vdsat) / (self.calculate_Abulk(T,Vbs) * Vdsat + Vgsteff + 2 * self.v_t(T))))

        VACLM       =   ((self.calculate_Abulk(T,Vbs) * Esat * self.Leff + Vgsteff) / (self.Pclm * self.calculate_Abulk(T,Vbs) * Esat * self.lit)) * \
                        (Vds - Vdsat)

        VAsat      =   ((Esat * self.Leff) + Vdsat + (2 * Rds * self.Vsat_T_dependent(T) * self.Cox * self.Weff * Vgsteff) * \
                        (1 - ((self.calculate_Abulk(T,Vbs) * Vdsat) / (2 * (Vgsteff + 2 * self.v_t(T)))))) / \
                        ((2/lamda) - 1 + (Rds * self.Vsat_T_dependent(T) * self.Cox * self.Weff * self.calculate_Abulk(T,Vbs)))
        VA         =   VAsat + (1 + ((self.Pvag * Vgsteff) / (Esat * self.Leff))) * ((1 / VACLM) + (1 / VADIBLC))**-1
        I_dsat      = self.Weff * self.VSAT * self.Cox * (Vgsteff - self.calculate_Abulk(T,Vbs) * Vdsat)
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff      = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        Vdsat       = self.calculate_Vdsat(Vgs, Vbseff, T)
        Rds         = self.calculate_Rds(Vds, Vgs, Vbseff, T)  # Calculate bias-dependent source/drain resistance
        Vdsat       = self.calculate_Vdsat(Vgs, Vbs, T, Vds)
        Vdseff      = Vdsat - 1/2 * (Vdsat - Vds - delta + np.sqrt((Vdsat - Vds - delta)**2 + 4 * delta * Vdsat))
        
        term1      = (self.Alpha0 + (self.Alpha1 * self.Leff)) / self.Leff
        term2      = Vds - Vdseff
        term3      = np.exp(-self.Beta0 / term2) 
        term4      = I_dsat / (1 + (Rds * I_dsat) / Vdseff) 
        term5      = (1 + (term2 / VA))
        I_sub      = term1 * term2 * term3 * term4 * term5

        return I_sub

    def compute(self, Vgs, Vds, Vbs=0.0, T=300.0):
        """Calculate drain current for given bias conditions.
        
        Main interface method that determines operation region and calculates
        the appropriate current (subthreshold, linear, or saturation).
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vds (float): Drain-source voltage in volts
            Vbs (float, optional): Bulk-source voltage in volts. Defaults to 0.
            T (float, optional): Temperature in Kelvin. Defaults to 300.0.
            
        Returns:
            float: Drain current in amperes
        """
        Vgsteff     = self.calculate_Vgsteff(Vgs, T,Vds, Vbs)
        Vdseff      = self.calculate_Vdseff(Vds, Vgs, Vbs, T)
        Vdsat       =  self.calculate_Vdsat(Vgs,Vbs,T,Vds)

        if Vgsteff <= 0:  # Subthreshold region
            I_ds = self.calculate_subthreshold_current(Vgs, Vds, T, Vbs)
        else:
            if Vdseff < Vdsat:  # Linear region
                I_ds = self.calculate_linear_current(Vdseff, Vgs,T,Vbs)
            else:  # Saturation region
                I_ds = self.calculate_saturation_current(Vgs, Vdseff, Vbs, T)
        return I_ds
#? -------------------------------------------------------------------------------
import numpy as np
import plotly.graph_objects as go
import webbrowser
import os

if __name__ == "__main__":
    model = BSIM3v3_Model()
    
    vds_range = np.linspace(0, 10, 100)
    vgs_range = np.linspace(-0.5, 5, 100)
    temp_range = np.linspace(250, 400, 100)
    Vds = 0.1
    Vbs = 0.0

    # Create HTML file with all plots
    html_file = "bsim3v3_plots.html"
    
    # Initialize HTML content
    html_content = """
    <html>
    <head>
        <title>BSIM3v3 Model Characterization</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            .plot-container {
                width: 100%;
                margin-bottom: 50px;
                border-bottom: 1px solid #ccc;
                padding-bottom: 20px;
            }
            h2 {
                color: #2c3e50;
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        <h1 style="text-align: center; font-family: Arial, sans-serif;">BSIM3v3 Model Characterization</h1>
    """
    
    # ------------------------------
    # Test 1: Vth vs Vds
    vth_vds = [model.vth_T_dependent(vds, 0, 400) for vds in vds_range]
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=vds_range, y=vth_vds, name="Vth vs Vds"))
    fig1.update_layout(
        title="Threshold Voltage vs Drain-Source Voltage",
        xaxis_title="Vds (V)",
        yaxis_title="Vth (V)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Threshold Voltage vs Drain-Source Voltage</h2>
        {div1}
    </div>
    """.format(div1=fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 2: Id vs Vgs for different Vds (log scale)
    fig2 = go.Figure()
    for i, vds in enumerate(np.linspace(0, 5, 5)):  # Fewer traces for clarity
        ids = [model.compute(vgs, vds) for vgs in vgs_range]
        fig2.add_trace(go.Scatter(
            x=vgs_range, 
            y=np.maximum(1e-20, ids),
            name=f'Vds={vds:.1f}V',
            mode='lines',
            line=dict(width=2),
            opacity=0.8
        ))
    fig2.update_layout(
        title="Drain Current vs Gate-Source Voltage (log scale)",
        xaxis_title="Vgs (V)",
        yaxis_title="Id (A)",
        yaxis_type="log",

    )
    html_content += """
    <div class="plot-container">
        <h2>Drain Current vs Gate-Source Voltage (log scale)</h2>
        {div2}
    </div>
    """.format(div2=fig2.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 3: Id vs Vds for different Vgs
    fig3 = go.Figure()
    for i, vgs in enumerate(np.linspace(0, 5, 5)):  # Fewer traces for clarity
        ids = [model.compute(vgs, vds) for vds in vds_range]
        fig3.add_trace(go.Scatter(
            x=vds_range, 
            y=ids,
            name=f'Vgs={vgs:.1f}V',
            mode='lines',
            line=dict(width=2),
            opacity=0.8
        ))
    fig3.update_layout(
        title="Drain Current vs Drain-Source Voltage",
        xaxis_title="Vds (V)",
        yaxis_title="Id (A)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Drain Current vs Drain-Source Voltage</h2>
        {div3}
    </div>
    """.format(div3=fig3.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 4: Vgsteff vs (Vgs-Vth)
    vth = model.vth_T_dependent(Vds, Vbs, 300)
    vgsteff_values = []
    vgst_values = []
    
    for vgs in vgs_range:
        Vth = model.vth_T_dependent(Vds, Vbs, 300)
        vgst = vgs - Vth
        vgsteff = model.calculate_Vgsteff(vgs, 300, Vds, Vbs)
        vgsteff_values.append(vgsteff)
        vgst_values.append(vgst)
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=vgst_values, y=vgsteff_values, name="Vgsteff"))
    fig4.add_trace(go.Scatter(x=vgst_values, y=vgst_values, name="Ideal", line=dict(dash='dash')))
    fig4.update_layout(
        title="Effective Gate Overdrive vs (Vgs-Vth)",
        xaxis_title="Vgs - Vth (V)",
        yaxis_title="Vgsteff (V)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Effective Gate Overdrive vs (Vgs-Vth)</h2>
        {div4}
    </div>
    """.format(div4=fig4.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 5: log(Vgsteff) vs (Vgs-Vth)
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=vgst_values, 
        y=np.log10(np.maximum(1e-20, vgsteff_values)),
        name="log(Vgsteff)",
        mode='lines'
    ))
    fig5.add_shape(
        type="line",
        x0=0, y0=-20, x1=0, y1=5,
        line=dict(color="gray", width=1, dash="dash")
    )
    fig5.update_layout(
        title="log(Effective Gate Overdrive) vs (Vgs-Vth)",
        xaxis_title="Vgs - Vth (V)",
        yaxis_title="log(Vgsteff) [log(V)]",

    )
    html_content += """
    <div class="plot-container">
        <h2>log(Effective Gate Overdrive) vs (Vgs-Vth)</h2>
        {div5}
    </div>
    """.format(div5=fig5.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 6: Id vs Temperature for different Vgs
    fig6 = go.Figure()
    for i, vgs in enumerate(np.linspace(0, 5, 5)):  # Fewer traces for clarity
        ids = [model.compute(vgs, Vds, Vbs, T) for T in temp_range]
        fig6.add_trace(go.Scatter(
            x=temp_range, 
            y=ids,
            name=f'Vgs={vgs:.1f}V',
            mode='lines',
            line=dict(width=2),
            opacity=0.8
        ))
    fig6.update_layout(
        title="Drain Current vs Temperature",
        xaxis_title="Temperature (K)",
        yaxis_title="Id (A)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Drain Current vs Temperature</h2>
        {div6}
    </div>
    """.format(div6=fig6.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 7: Mobility vs Temperature for different Vgs
    fig7 = go.Figure()
    for i, vgs in enumerate(np.linspace(0, 5, 5)):  # Fewer traces for clarity
        mobilities = [model.calculate_mobility(vgs, T, Vds, Vbs) for T in temp_range]
        fig7.add_trace(go.Scatter(
            x=temp_range, 
            y=mobilities,
            name=f'Vgs={vgs:.1f}V',
            mode='lines',
            line=dict(width=2),
            opacity=0.8
        ))
    fig7.update_layout(
        title="Effective Mobility vs Temperature",
        xaxis_title="Temperature (K)",
        yaxis_title="Mobility (m²/V·s)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Effective Mobility vs Temperature</h2>
        {div7}
    </div>
    """.format(div7=fig7.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # ------------------------------
    # Test 8-9: Vdseff vs Vds
    original_delta = model.delta
    
    # Test 8: Vdseff vs Vds for different Vgs values
    fig8 = go.Figure()
    for vgs in [1, 3, 5]:
        vdseff_values = [model.calculate_Vdseff(vds, vgs, Vbs, 300) for vds in vds_range]
        fig8.add_trace(go.Scatter(
            x=vds_range,
            y=vdseff_values,
            name=f'Vgs={vgs}V',
            mode='lines'
        ))
        vdsat = model.calculate_Vdsat(vgs, Vbs, 300, Vds)
        fig8.add_vline(
            x=vdsat,
            line=dict(color="gray", width=1, dash="dash"),
            opacity=0.3
        )
    
    fig8.add_trace(go.Scatter(
        x=vds_range,
        y=vds_range,
        name='Ideal',
        line=dict(color="black", dash="dash")
    ))
    fig8.update_layout(
        title="Vdseff vs Vds (Varying Vgs)",
        xaxis_title="Vds (V)",
        yaxis_title="Vdseff (V)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Vdseff vs Vds (Varying Vgs)</h2>
        {div8}
    </div>
    """.format(div8=fig8.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # Test 9: Vdseff vs Vds for different delta values
    fig9 = go.Figure()
    for delta in [0.001, 0.01, 0.05]:
        model.delta = delta
        vdseff_values = [model.calculate_Vdseff(vds, 1.0, Vbs, 300) for vds in vds_range]
        fig9.add_trace(go.Scatter(
            x=vds_range,
            y=vdseff_values,
            name=f'delta={delta}',
            mode='lines'
        ))
    
    model.delta = original_delta
    vdsat = model.calculate_Vdsat(1.0, Vbs, 300, Vds)
    fig9.add_vline(
        x=vdsat,
        line=dict(color="gray", width=1, dash="dash")
    )
    fig9.add_trace(go.Scatter(
        x=vds_range,
        y=vds_range,
        name='Ideal',
        line=dict(color="black", dash="dash")
    ))
    fig9.update_layout(
        title="Vdseff vs Vds (Varying delta)",
        xaxis_title="Vds (V)",
        yaxis_title="Vdseff (V)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Vdseff vs Vds (Varying delta)</h2>
        {div9}
    </div>
    """.format(div9=fig9.to_html(full_html=False, include_plotlyjs='cdn'))

    # ------------------------------
    # Test 10: Vdsat vs Vgs for different Vbs   
    fig10 = go.Figure()
    for vbs in [0, -1, -2]:
        vdsat_values = [model.calculate_Vdsat(vgs, vbs, 300, Vds) for vgs in vgs_range]
        fig10.add_trace(go.Scatter(
            x=vgs_range,
            y=vdsat_values,
            name=f'Vbs={vbs}V',
            mode='lines'
        ))
    fig10.update_layout(
        title="Saturation Voltage vs Gate-Source Voltage",
        xaxis_title="Vgs (V)",
        yaxis_title="Vdsat (V)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Saturation Voltage vs Gate-Source Voltage</h2>
        {div10} 
    </div>
    """.format(div10=fig10.to_html(full_html=False, include_plotlyjs='cdn'))
    # ------------------------------
    # Test 11: Vdsat vs Temperature for different Vgs
    fig11 = go.Figure()
    for vgs in np.linspace(0, 5, 5):  # F
        vdsat_values = [model.calculate_Vdsat(vgs, Vbs, T, Vds) for T in temp_range]
        fig11.add_trace(go.Scatter(
            x=temp_range,
            y=vdsat_values,
            name=f'Vgs={vgs:.1f}V',
            mode='lines',
            line=dict(width=2),
            opacity=0.8
        ))
    fig11.update_layout(
        title="Saturation Voltage vs Temperature",
        xaxis_title="Temperature (K)",
        yaxis_title="Vdsat (V)",

    )
    html_content += """
    <div class="plot-container">
        <h2>Saturation Voltage vs Temperature</h2>
        {div11}
    </div>
    """.format(div11=fig11.to_html(full_html=False, include_plotlyjs='cdn'))
    # ------------------------------
    
    # ------------------------------
    # Test 12: DIBL Effect - Vth vs Vds and ∂Vth/∂Vds
    vds_range_dibl = np.linspace(0.1, 5, 100)  
    vth_values = np.array([model.vth_T_dependent(vds, 0, 300) for vds in vds_range_dibl])
    # Calculate numerical derivative ∂Vth/∂Vds
    dVth_dVds = np.gradient(vth_values, vds_range_dibl)
    fig12 = go.Figure()
    # Add Vth trace (primary y-axis)
    fig12.add_trace(go.Scatter(
        x=vds_range_dibl,
        y=vth_values,
        name="Threshold Voltage (Vth)",
        mode='lines',
        line=dict(width=2, color='blue'),
        yaxis='y1'
    ))
    
    # Add ∂Vth/∂Vds trace (secondary y-axis)
    fig12.add_trace(go.Scatter(
        x=vds_range_dibl,
        y=dVth_dVds,
        name="DIBL Coefficient (∂Vth/∂Vds)",
        mode='lines',
        line=dict(width=2, color='red', dash='dot'),
        yaxis='y2'
    ))
    
    # Update layout with dual axes
    fig12.update_layout(
        title="<b></b><br>Threshold Voltage vs Drain Voltage and DIBL Coefficient",
        xaxis_title="Drain-Source Voltage (V<sub>DS</sub>) [V]",
        yaxis=dict(
            title="Threshold Voltage (V<sub>th</sub>) [V]",
            range=[min(vth_values)*0.95, max(vth_values)*1.05]
        ),
        yaxis2=dict(
            title="DIBL Coefficient (∂V<sub>th</sub>/∂V<sub>DS</sub>) [V/V]",
            overlaying="y",
            side="right",
            range=[min(dVth_dVds)*1.1, max(dVth_dVds)*1.1]  # Add some padding
        ),
        legend=dict(x=0.05, y=0.95),
        hovermode="x unified",
        template="plotly_white",
        margin=dict(t=100)
    )
    
    # Add annotation explaining DIBL effect
    fig12.add_annotation(
        x=0.5,
        y=0.1,
        xref="paper",
        yref="paper",
        text="DIBL (Drain-Induced Barrier Lowering) shows V<sub>th</sub> reduction at higher V<sub>DS</sub>",
        showarrow=False,
        font=dict(size=11),
        bgcolor="white"
    )
    
    html_content += """
    <div class="plot-container">
        <h2>DIBL Effect Analysis</h2>
        {div12}
    </div>
    """.format(div12=fig12.to_html(full_html=False, include_plotlyjs='cdn'))


    
    # ------------------------------

    # Close HTML tags
    html_content += """
    </body>
    </html>
    """
    
    # Save HTML file
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    # Open in default browser
    webbrowser.open('file://' + os.path.realpath(html_file))