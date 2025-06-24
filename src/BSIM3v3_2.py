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
    - Threshold voltage calculation with short-channel, narrow width, and DIBL effects
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
        self.Alpha0   = 0.0                        # -,     Substrate current parameter
        self.Alpha1   = 0.0                        # -,     Substrate current parameter
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
        self.Ngate    = 0                        # m-3,   Poly doping concentration
        self.Nds      = 1e26                        # m-3,   Source/drain doping concentration
        # Parasitic resistance
        self.Rds      = 50.0                        # ohm,     Source-drain resistance
        # Subthreshold parameters
        self.Voff     = -0.08                       # V,     Offset voltage for subthreshold current
        self.Keta     = -0.047                      # -,     Body effect coefficient for Voff
        self.delta    = 0.01                        # -,     Smoothing parameter for Voff
        # Temperature parameters
        self.Tnom     = 300.15                       # K,     Nominal temperature
        self.Kt1      = -0.11                       # V,     Temperature coefficient for Vth
        self.Kt1l     = 0.0                       # V·m,   Temperature coefficient for Vth
        self.Kt2      = 0.022                        # -,     Temperature coefficient for Vth
        self.Ute      = -1.5                        # -,     Mobility temperature exponent
        self.At       = 3.3E4                      # m/s,   Velocity saturation temperature coefficient
        self.Ags      = 0.0                         # -,     Body effect coefficient for bulk charge
        # Additional parameters
        self.Pscbe1   = 4.24E8                      # -,     Substrate current body-effect coefficient 1
        self.Pscbe2   = 1.0E-5                      # -,     Substrate current body-effect coefficient 2
        # State variables
        self.Cit      = 0.0                         # F/m2,  Interface trap capacitance
        self.Citd     = 0.1                         # F/m2,  Interface trap capacitance derivative
        self.Citb     = 0.1                         # F/m2,  Interface trap capacitance body effect
        self.Nfactor  = 1.0                        # -,     Subthreshold slope factor
        self.NI0      = 1.45e16                     # m-3,   Intrinsic carrier concentration at 300K
        self.NITEXP   = 1.5                         # -,     Exponent for temperature dependence of ni
        self.Cox      = self.epsOx / self.Tox       # F/m², Oxide capacitance per unit area
        self.Cdsc     = 2.4E-4                       # Axial capacitance (F)
        self.Cdscd    = 0.0                       # Drain-bias sensitivity of Cdsc F/Vm2
        self.Cdscb    = 0.0                       # Body-bias sensitivity of Cdsc F/Vm2

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
        self.Vbseff = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        # Depletion widths and characteristic lengths
        self.Xdep   = np.sqrt(2 * self.epsSi * (self.Phi_s(T) - self.Vbseff) / (self.q * self.Nch))
        lt0         = np.sqrt(self.epsSi * self.Xdep * self.Tox / self.epsOx)
        ltw         = np.sqrt(self.epsSi * self.Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2w * self.Vbseff)))
        lt          = np.sqrt(self.epsSi * self.Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2 * self.Vbseff)))
        # Scale K1 and K2 for oxide thickness (Eq. 2.1.25)
        K1ox        = self.K1 * (self.Tox / self.Toxm)
        K2ox        = self.K2 * (self.Tox / self.Toxm)
        Vth0ox      = self.Vth0 - K1ox * np.sqrt(self.Phi_s(T))
        # Calculate all terms of threshold voltage (Eq. 2.1.25)
        term1       = Vth0ox + K1ox * np.sqrt(self.Phi_s(T) - self.Vbseff) - K2ox * self.Vbseff
        term2       = K1ox * (np.sqrt(1 + self.Nlx/self.Leff) - 1) * np.sqrt(self.Phi_s(T))
        term3       = (self.K3 + self.K3b * self.Vbseff) * (self.Tox / (self.Weff + self.W0)) * self.Phi_s(T)
        term4       = -self.Dvt0w * (np.exp(-self.Dvt1w * self.Weff * self.Leff/(2 * ltw)) + 2 * np.exp(-self.Dvt1w * self.Weff * self.Leff/ltw)) * (self.Vbi(T) - self.Phi_s(T))
        term5       = -self.Dvt0 * (np.exp(-self.Dvt1 * self.Leff/(2 * lt)) + 2 * np.exp(-self.Dvt1 * self.Leff/lt)) * (self.Vbi(T) - self.Phi_s(T))
        term6       = -(np.exp(-self.Dsub * self.Leff/(2 * lt0)) + 2 * np.exp(-self.Dsub * self.Leff/lt0)) * (self.Eta0 + self.Etab * self.Vbseff) * Vds
        # Temperature effect on threshold voltage
        delta_T     = (T / self.Tnom) - 1
        term7       = (self.Kt1 + self.Kt1l/self.Leff + self.Kt2 * self.Vbseff) * delta_T
        Vth    = term1 + term2 + term3 + term4 + term5 + term6 + term7
        #print(f"Vth: {Vth}, Vbseff: {self.Vbseff}, Xdep: {self.Xdep}, Tox: {self.Tox}, Toxm: {self.Toxm}")
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
        Vth         = self.calculate_V_th(Vds, Vbs, T)  
        Vgsteff     = self.calculate_Vgsteff(Vgs, T, Vds, Vbs)  
        mob_temp    = self.U0 * (T/self.Tnom)**self.Ute # Temperature effect on mobility
        
        # Mobility degradation models
        if self.mobMod == 1:
            # Vertical field mobility degradation model (Eq. 3.2.1)
            denom = 1 + (self.Ua + self.Uc * self.Vbseff) *             \
                    ((Vgsteff + 2*Vth)/self.Tox) +                      \
                    self.Ub * np.square((Vgsteff + 2*Vth)/self.Tox)
            
        elif self.mobMod == 2:  # To account for depletion mode devices, another mobility model option is given by the following
            denom = 1 + (self.Ua + self.Uc * self.Vbseff) *             \
                    (Vgsteff/self.Tox) +                                \
                    self.Ub * np.square(Vgsteff/self.Tox)
        else:  # To consider the body bias dependence of Eq. 3.2.1 further, we have introduced the following expression
            denom = 1 + (self.Ua * ((Vgsteff + 2*Vth)/self.Tox) +       \
                    self.Ub * np.square((Vgsteff + 2*Vth)/self.Tox)) *  \
                    (1 + self.Uc * self.Vbseff)
       
        mob_eff   = mob_temp / denom
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
        lt          = np.sqrt(self.epsSi * self.Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2 * self.Vbseff)))
        # Calculate the exponential terms
        term1 = np.exp(-self.Dvt1 * self.Leff / (2 * lt))
        term2 = np.exp(-self.Dvt1 * self.Leff / (lt))
        
        # Calculate the main equation
        n = 1 + self.Nfactor * (Cd/self.Cox) + \
            ((self.Cdsc+self.Cdscd*Vds+self.Cdscb*Vbseff) *(term1+2*term2))/self.Cox +\
            self.Cit/self.Cox
        Vth             = self.calculate_V_th(Vds, Vbs, T)  
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
        Vgsteff = self.calculate_Vgsteff(Vgs, T, Vds, Vbs)  # Recalculate Vgsteff for consistency
        Esat     = 2 * self.VSAT / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        term1 = (Esat * self.Leff * (Vgsteff + 2 * self.v_t(T))) 
        term2 = (self.calculate_Abulk(T) * Esat * self.Leff + Vgsteff + 2 * self.v_t(T))
        Vdsat = term1 / term2
        
        return Vdsat
    
    def calculate_Abulk(self, T):
        """Calculate bulk charge effect coefficient (Abulk) (Eq. 2.4.1).
        
        Accounts for non-uniform channel doping effects on threshold voltage.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Bulk charge effect coefficient (unitless)
        """
        # Scale K1 and K2 for oxide thickness (Eq. 2.1.25)
        K1ox        = self.K1 * (self.Tox / self.Toxm)
        term1       = 1 + (K1ox / (2 * np.sqrt(self.Phi_s(T) - self.Vbseff))) * (self.A0 * self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * self.Xdep))) * (1 - self.Ags * np.square(self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * self.Xdep))))
        term2       = (self.B0 / (self.Weff + self.B1)) / (1 + self.Keta * self.Vbseff)
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
        Vth     = self.calculate_V_th(Vds, Vbs, T)  
        Vgst    = Vgs - Vth
        mob_eff = self.calculate_mobility(Vgs, T,Vds, Vbs)
        n       = 1 + (self.Cit + self.Citd * Vds + self.Citb * self.Vbseff) / self.Cox + self.Nfactor * self.epsSi / (self.Cox * self.Xdep)
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
        Esat     = 2 * self.VSAT / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 

        mob_eff = self.calculate_mobility(Vgs, T,Vds, Vbs)
        Vb      = (Vgsteff + 2 * self.v_t(T)) / self.calculate_Abulk(T)
        I_dso   = mob_eff * self.Cox * (self.Weff / self.Leff) * Vgsteff * Vds * (1 - Vds / (2 * Vb)) / (1 + Vds / (Esat * self.Leff))
        # Add source-drain resistance effect (Eq. 3.3.5)
        if Vds == 0:
            # Handle the case where Vds is zero (maybe return 0 or a small value)
            I_ds = 0
        else:
            I_ds = I_dso / (1 + self.Rds * I_dso / Vds) #Extrinsic Case (Rds > 0)
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
        Vgsteff = self.calculate_Vgsteff(Vgs, T)
        self.lit    = np.sqrt(self.epsSi * self.Xj * self.Tox / self.epsOx) #Calculate intrinsic length (lit) for short-channel effects.
        Vdsat       = self.calculate_Vdsat(Vgs, Vbs, T)
        I_dsat      = self.Weff * self.VSAT * self.Cox * (Vgsteff - self.calculate_Abulk(T) * Vdsat)
        # Calculate Early voltages
        Esat     = 2 * self.VSAT / (self.U0* (T/self.Tnom)**self.Ute)    #Calculate saturation electric field (Esat) for velocity saturation. 
        V_Asat      = (Esat * self.Leff + Vdsat + 2 * self.Rds * self.VSAT * self.Cox * self.Weff * Vgsteff * (1 - self.calculate_Abulk(T) * Vdsat / (2 * (Vgsteff + 2 * self.v_t(T))))) / (2/self.A2 - 1 + self.Rds * self.VSAT * self.Cox * self.Weff * self.calculate_Abulk(T))
        V_ACLM      = (self.calculate_Abulk(T) * Esat * self.Leff + Vgsteff) / (self.Pclm * self.calculate_Abulk(T) * Esat * self.lit) * (Vds - Vdsat)
        theta_rout  = self.Pdiblc1 * (np.exp(-self.Drout * self.Leff / (2 * self.lit)) + 2 * np.exp(-self.Drout * self.Leff / self.lit)) + self.Pdiblc2
        V_ADIBL     = (Vgsteff + 2 * self.v_t(T)) / (theta_rout * (1 + self.Pdiblb * self.Vbseff)) * (1 - self.calculate_Abulk(T) * Vdsat / (self.calculate_Abulk(T) * Vdsat + Vgsteff + 2 * self.v_t(T)))
        V_A         = V_Asat + (1 + self.Pvag * Vgsteff / (Esat * self.Leff)) * (1 / V_ACLM + 1 / V_ADIBL)**-1
        # Substrate current induced body effect
        V_ASCBE     = np.exp(self.Pscbe1 * self.lit / (Vds - Vdsat)) * self.Leff / self.Pscbe2
        # Saturation current with all effects
        I_ds        = I_dsat * (1 + (Vds - Vdsat) / V_A) * (1 + (Vds - Vdsat) / V_ASCBE)
        return I_ds
    
    def compute(self, Vgs, Vds, Vbs=0.0, T=300.15):
        """Calculate drain current for given bias conditions.
        
        Main interface method that determines operation region and calculates
        the appropriate current (subthreshold, linear, or saturation).
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vds (float): Drain-source voltage in volts
            Vbs (float, optional): Bulk-source voltage in volts. Defaults to 0.
            T (float, optional): Temperature in Kelvin. Defaults to 300.15.
            
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



if __name__ == "__main__":
    model = BSIM3v3_Model()
    
    vds_range   = np.linspace(     0    ,    10, 50)      
    vgs_range   = np.linspace(  -0.5    ,    10, 50)  
    temp_range  = np.linspace(   250    ,   400, 50) 
    Vds         = 0.1  
    Vbs         = 0.0  

    # ------------------------------
    # Test 1: Vth vs Vds
    vth_vds = [model.calculate_V_th(vds, 0, 400) for vds in vds_range]
    
    plt.figure(figsize=(10, 6))
    plt.plot(vds_range, vth_vds)
    plt.title('Threshold Voltage vs Drain-Source Voltage')
    plt.xlabel('Vds (V)')
    plt.ylabel('Vth (V)')
    plt.grid(True)
    plt.show()

    # ------------------------------
    # Test 2: Id vs Vgs for different Vds
    plt.figure(figsize=(10, 6))
    for vds in vds_range:
        ids = [model.compute(vgs, vds) for vgs in vgs_range]
        plt.plot(vgs_range, ids, label=f'Vds={vds}V')
    
    plt.title('Drain Current vs Gate-Source Voltage')
    plt.xlabel('Vgs (V)')
    plt.ylabel('Id (A)')
    plt.grid(True)
    plt.yscale('log')
    plt.show()

    # ------------------------------
    # Test 3: Id vs Vds for different Vgs
    plt.figure(figsize=(10, 6))
    for vgs in vgs_range:
        ids = [model.compute(vgs, vds) for vds in vds_range]
        plt.plot(vds_range, ids, label=f'Vgs={vgs}V')
    
    plt.title('Drain Current vs Drain-Source Voltage')
    plt.xlabel('Vds (V)')
    plt.ylabel('Id (A)')
    plt.grid(True)
    plt.show()

    # ------------------------------
    # Test 4: Vgsteff vs (Vgs-Vth)
    vth = model.calculate_V_th(Vds, Vbs, 300)
    vgsteff_values = []
    vgst_values = []
    
    for vgs in vgs_range:
        Vth = model.calculate_V_th(Vds, Vbs, 300)
        vgst = vgs - Vth
        vgsteff = model.calculate_Vgsteff(vgs, 300, Vds, Vbs)
        vgsteff_values.append(vgsteff)
        vgst_values.append(vgst)
    
    plt.figure(figsize=(10, 6))
    plt.plot(vgst_values, vgsteff_values, label='Vgsteff')
    plt.plot(vgst_values, vgst_values, '--', label='Ideal Vgsteff = Vgs-Vth')
    plt.title('Effective Gate Overdrive Voltage vs (Vgs-Vth)')
    plt.xlabel('Vgs - Vth (V)')
    plt.ylabel('Vgsteff (V)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # ------------------------------
    # Test 4 (log): log(Vgsteff) vs (Vgs-Vth)
    plt.figure(figsize=(10, 6))
    plt.plot(vgst_values, np.log10(np.maximum(1e-20, vgsteff_values)), label='log(Vgsteff)')
    plt.axvline(x=0, color='gray', linestyle='--', label='Vgs=Vth')
    plt.title('log(Effective Gate Overdrive) vs (Vgs-Vth)')
    plt.xlabel('Vgs - Vth (V)')
    plt.ylabel('log(Vgsteff) [log(V)]')
    plt.legend()
    plt.grid(True, which='both')
    plt.show()

    # ------------------------------
    # Test 5: Id vs Temperature for different Vgs
    plt.figure(figsize=(10, 6))
    for vgs in vgs_range:
        ids = [model.compute(vgs, Vds, Vbs, T) for T in temp_range]
        plt.plot(temp_range, ids, label=f'Vgs={vgs}V')
    
    plt.title('Drain Current vs Temperature')
    plt.xlabel('Temperature (K)')
    plt.ylabel('Id (A)')
    # plt.legend()
    plt.grid(True)
    plt.show()

        # ------------------------------
    # Test 6: Mobility vs Temperature for different Vgs
    plt.figure(figsize=(10, 6))
    for vgs in vgs_range:  # Selected Vgs values to show different curves
        mobilities = [model.calculate_mobility(vgs, T, Vds, Vbs) for T in temp_range]
        plt.plot(temp_range, mobilities, label=f'Vgs={vgs}V')
    
    plt.title('Effective Mobility vs Temperature')
    plt.xlabel('Temperature (K)')
    plt.ylabel('Mobility (m²/V·s)')
    plt.grid(True)
    plt.show()