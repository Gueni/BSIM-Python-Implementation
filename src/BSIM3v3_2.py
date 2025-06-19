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
        self.epsSi    = 11.7 * 8.854e-12  # F/m,   Silicon permittivity
        self.epsOx    = 3.9 * 8.854e-12   # F/m,   Silicon dioxide permittivity
        self.q        = 1.602e-19         # C,     Electron charge
        self.k_B      = 1.38e-23          # J/K,   Boltzmann constant
        # Threshold voltage related parameters
        self.Vth0     = 0.40              # V,     Zero-bias threshold voltage
        self.K1       = 0.3               # √V,    First body effect coefficient
        self.K2       = 0.01              # -,     Second body effect coefficient
        self.K3       = 2.0               # -,     Narrow width effect coefficient
        self.K3b      = -0.05             # -,     Body effect on narrow width coefficient
        self.Dvt0     = 2.5               # -,     Short-channel effect coefficient at Vbs=0
        self.Dvt1     = 0.6               # -,     Short-channel effect coefficient
        self.Dvt2     = -0.03             # 1/V,   Short-channel effect coefficient for body bias
        self.Dvt0w    = 0.0               # -,     Narrow width effect coefficient at Vbs=0
        self.Dvt1w    = 5.3e6             # -,     Narrow width effect coefficient
        self.Dvt2w    = -0.032            # 1/V,   Narrow width effect coefficient for body bias
        self.Nlx      = 1.5e-7            # m,     Lateral non-uniform doping parameter
        self.W0       = 2.0e-6            # m,     Narrow width parameter
        # DIBL and substrate effect parameters
        self.Dsub     = 0.8               # -,     DIBL coefficient in subthreshold region
        self.Eta0     = 0.1               # -,     DIBL coefficient in strong inversion
        self.Etab     = -0.07             # -,     Body bias effect on DIBL coefficient
        # Mobility parameters (180nm NMOS)
        self.mobMod   = 1                 # -,     Mobility model selector
        self.U0       = 0.4               # m2/V·s, Low-field mobility
        self.Ua       = 0.5e-9            # m/V,   First-order mobility degradation coefficient
        self.Ub       = 0.5e-18           # (m/V)2, Second-order mobility degradation coefficient
        self.Uc       = -1.0              # -,     Body-effect coefficient for mobility degradation
        # Velocity saturation parameters
        self.VSAT     = 1.2e5             # m/s,   Saturation velocity
        self.A0       = 1.2               # -,     Bulk charge effect coefficient
        self.A1       = 0.01              # -,     Saturation voltage parameter
        self.A2       = 1.0               # -,     Saturation voltage parameter
        self.Abulk0   = 0.8               # -,     Bulk charge effect coefficient at Vbs=0
        self.B0       = 0.5e-6            # -,     Width effect on Abulk
        self.B1       = 0.5e-6            # -,     Width effect on Abulk
        # Output resistance parameters
        self.Pclm     = 1.5               # -,     Channel length modulation coefficient
        self.Pdibl1   = 0.5               # -,     DIBL coefficient for output resistance
        self.Pdibl2   = 0.02              # -,     DIBL coefficient for output resistance
        self.Pdiblb   = -0.05             # -,     Body effect on DIBL for output resistance
        self.Drout    = 0.6               # -,     Output resistance DIBL coefficient
        self.Pvag     = 1e-7              # 1/V,   Gate voltage effect on output resistance
        self.Alpha0   = 0.01              # -,     Substrate current parameter
        self.Alpha1   = 0.01              # -,     Substrate current parameter
        self.Beta0    = 30.0              # V/m,   Substrate current parameter
        # Geometry parameters (180nm process)
        self.Leff     = 180e-9            # m,     Effective channel length
        self.Weff     = 1e-6              # m,     Effective channel width (1um)
        self.Ldrawn   = 180e-9            # m,     Drawn channel length
        self.Wdrawn   = 1e-6              # m,     Drawn channel width
        self.Xj       = 100e-9            # m,     Junction depth
        self.Tox      = 2.0e-9            # m,     Oxide thickness
        self.Toxm     = 2.0e-9            # m,     Oxide thickness for modeling
        # Doping concentrations
        self.Nch      = 1.0e23            # m-3,   Channel doping concentration
        self.Ngate    = 1e25              # m-3,   Poly doping concentration
        self.Nds      = 1e26              # m-3,   Source/drain doping concentration
        # Parasitic resistance
        self.Rds      = 50.0              # ohm,     Source-drain resistance
        # Subthreshold parameters
        self.n        = 1.5               # -,     Subthreshold swing coefficient
        self.Voff     = -0.1              # V,     Offset voltage for subthreshold current
        self.Keta     = 0.05              # -,     Body effect coefficient for Voff
        self.delta    = 0.01              # -,     Smoothing parameter for Voff
        # Temperature parameters
        self.Tnom     = 300.0             # K,     Nominal temperature
        self.Kt1      = -0.15             # V,     Temperature coefficient for Vth
        self.Kt1l     = 1e-9              # V·m,   Temperature coefficient for Vth
        self.Kt2      = 0.03              # -,     Temperature coefficient for Vth
        self.Ute      = -1.8              # -,     Mobility temperature exponent
        self.At       = 4.0e4             # m/s,   Velocity saturation temperature coefficient
        self.Ags      = 0.5               # -,     Body effect coefficient for bulk charge
        # Additional parameters
        self.Pscbe1   = 0.001             # -,     Substrate current body-effect coefficient 1
        self.Pscbe2   = 0.001             # -,     Substrate current body-effect coefficient 2
        # State variables
        self.Cit      = 0.1               # F/m2,  Interface trap capacitance
        self.Citd     = 0.1               # F/m2,  Interface trap capacitance derivative
        self.Citb     = 0.1               # F/m2,  Interface trap capacitance body effect
        self.Nfactor  = 0.1               # -,     Subthreshold slope factor
        self.NI0      = 1.45e16           # m-3,   Intrinsic carrier concentration at 300K
        self.NITEXP   = 1.5               # -,     Exponent for temperature dependence of ni

    def Cox(self):
        """Calculate oxide capacitance per unit area (Cox).
        
        Returns:
            float: Oxide capacitance per unit area in F/m²
        """
        return self.epsOx / self.Tox
    
    def lit(self):
        """Calculate intrinsic length (lit) for short-channel effects.
        
        Returns:
            float: Intrinsic length in meters
        """
        return np.sqrt(self.epsSi * self.Xj * self.Tox / self.epsOx)
    
    def Esat(self):
        """Calculate saturation electric field (Esat) for velocity saturation.
        
        Returns:
            float: Saturation electric field in V/m
        """
        return 2 * self.VSAT / self.U0
    
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
        return self.v_t(T) * np.log(self.Nch * self.Nds / self.ni(T)**2)
    
    def ni(self, T):
        """Calculate intrinsic carrier concentration (ni) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Intrinsic carrier concentration in m^-3
        """
        return self.NI0 * (T / self.Tnom) ** self.NITEXP
    
    def Phi_s(self, T):
        """Calculate surface potential (Phi_s) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Surface potential in volts
        """
        Phi_s = 2 * self.v_t(T) * np.log(self.Nch / self.ni(T))
        return Phi_s
    
    def v_t(self, T):
        """Calculate thermal voltage (Vt) based on temperature.
        
        Args:
            T (float): Temperature in Kelvin
            
        Returns:
            float: Thermal voltage in volts
        """
        return self.k_B * T / self.q
    
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
        Vbc         = 0.9 * (self.Phi_s(T) - self.K1**2 / (4 * self.K2**2))
        self.Vbseff = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt((Vbs - Vbc - self.delta)**2 + 4 * self.delta * Vbc))
        # Depletion widths and characteristic lengths
        self.Xdep   = np.sqrt(2 * self.epsSi * (self.Phi_s(T) - self.Vbseff) / (self.q * self.Nch))
        lt0         = np.sqrt(self.epsSi * self.Xdep0(T) * self.Tox / self.epsOx)
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
        self.Vth    = term1 + term2 + term3 + term4 + term5 + term6 + term7
        return self.Vth
    
    def calculate_mobility(self, Vgs, T):
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
        Vgst        = Vgs - self.Vth
        Vgsteff     = 2 * self.n * self.v_t(T) * np.log(1 + np.exp(Vgst / (2 * self.n * self.v_t(T))))
        Vgsteff     = Vgsteff / (1 + 2 * self.n * self.Cox() * np.sqrt(2 * self.Phi_s(T) / (self.q * self.epsSi * self.Nch)) * np.exp(-(Vgst - 2 * self.Voff) / (2 * self.n * self.v_t(T))))
        mob_temp    = self.U0 * (T/self.Tnom)**self.Ute # Temperature effect on mobility
        # Mobility degradation models
        if self.mobMod == 1:
            denom = 1 + (self.Ua + self.Uc * self.Vbseff) * ((Vgsteff + 2*self.Vth)/self.Tox) + self.Ub * ((Vgsteff + 2*self.Vth)/self.Tox)**2
        elif self.mobMod == 2:
            denom = 1 + (self.Ua + self.Uc * self.Vbseff) * (Vgsteff/self.Tox) + self.Ub * (Vgsteff/self.Tox)**2
        else:  
            denom = 1 + (self.Ua * (Vgsteff + 2*self.Vth)/self.Tox + self.Ub * ((Vgsteff + 2*self.Vth)/self.Tox)**2) * (1 + self.Uc * self.Vbseff)
        self.mob_eff = mob_temp / denom
        return self.mob_eff
    
    def calculate_Vgsteff(self, Vgs, Vbs, T):
        """Calculate effective Vgs-Vth including subthreshold smoothing (Eq. 3.1.3).
        
        Provides smooth transition between subthreshold and strong inversion regions.
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Effective gate overdrive voltage in volts
        """
        Vgst            = Vgs - self.Vth
        Vgsteff         = 2 * self.n * self.v_t(T) * np.log(1 + np.exp(Vgst / (2 * self.n * self.v_t(T))))
        denom           = 1 + 2 * self.n * self.Cox() * np.sqrt(2 * self.Phi_s(T) / (self.q * self.epsSi * self.Nch)) * np.exp(-(Vgst - 2 * self.Voff) / (2 * self.n * self.v_t(T)))
        self.Vgsteff    = Vgsteff / denom
        return self.Vgsteff
    
    def calculate_Vdsat(self, Vgs, Vbs, T):
        """Calculate saturation voltage (Vdsat) (Eq. 3.4.3).
        
        The voltage at which the channel reaches velocity saturation.
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Saturation voltage in volts
        """
        self.calculate_Vgsteff(Vgs, Vbs, T)
        self.Vdsat = (self.Esat() * self.Leff * (self.Vgsteff + 2 * self.v_t(T))) / (self.Abulk * self.Esat() * self.Leff + self.Vgsteff + 2 * self.v_t(T))
        return self.Vdsat
    
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
        term1       = 1 + (K1ox / (2 * np.sqrt(self.Phi_s(T) - self.Vbseff))) * (self.A0 * self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * self.Xdep))) * (1 - self.Ags * (self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * self.Xdep)))**2)
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
        Vdsat       = self.calculate_Vdsat(Vgs, Vbs, T)
        Vdext       = Vdsat - 0.5 * (Vdsat - Vds - 0.02 + np.sqrt((Vdsat - Vds - 0.02)**2 + 4 * 0.02 * Vdsat))
        self.Vdseff = Vdext - 0.5 * (Vdext - Vds - self.delta + np.sqrt((Vdext - Vds - self.delta)**2 + 4 * self.delta * Vdext))
        return self.Vdseff
    
    def calculate_subthreshold_current(self, Vgs, Vds, T):
        """Calculate subthreshold current (Eq. 2.7.1).
        
        Models the current when Vgs < Vth (weak inversion region).
        
        Args:
            Vgs (float): Gate-source voltage in volts
            Vds (float): Drain-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Subthreshold drain current in amperes
        """
        Vgst    = Vgs - self.Vth
        n       = 1 + (self.Cit + self.Citd * Vds + self.Citb * self.Vbseff) / self.Cox() + self.Nfactor * self.epsSi / (self.Cox() * self.Xdep)
        I_s0    = self.mob_eff * (self.Weff / self.Leff) * np.sqrt(self.q * self.epsSi * self.Nch * self.v_t(T)**2 / (2 * self.Phi_s(T)))
        I_sub   = I_s0 * (1 - np.exp(-Vds / self.v_t(T))) * np.exp((Vgst - self.Voff) / (n * self.v_t(T)))
        return I_sub
    
    def calculate_linear_current(self, Vds, T):
        """Calculate linear region current (triode region) (Eq. 3.3.4).
        
        Models the current when Vds < Vdsat.
        
        Args:
            Vds (float): Drain-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Drain current in amperes
        """
        Vb      = (self.Vgsteff + 2 * self.v_t(T)) / self.Abulk
        I_dso   = self.mob_eff * self.Cox() * (self.Weff / self.Leff) * self.Vgsteff * Vds * (1 - Vds / (2 * Vb)) / (1 + Vds / (self.Esat() * self.Leff))
        # Add source-drain resistance effect (Eq. 3.3.5)
        if Vds == 0:
            # Handle the case where Vds is zero (maybe return 0 or a small value)
            I_ds = 0
        else:
            I_ds = I_dso / (1 + self.Rds * I_dso / Vds)
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
        Vdsat       = self.calculate_Vdsat(Vgs, Vbs, T)
        I_dsat      = self.Weff * self.VSAT * self.Cox() * (self.Vgsteff - self.Abulk * Vdsat)
        # Calculate Early voltages
        V_Asat      = (self.Esat() * self.Leff + Vdsat + 2 * self.Rds * self.VSAT * self.Cox() * self.Weff * self.Vgsteff * (1 - self.Abulk * Vdsat / (2 * (self.Vgsteff + 2 * self.v_t(T))))) / (2/self.A2 - 1 + self.Rds * self.VSAT * self.Cox() * self.Weff * self.Abulk)
        V_ACLM      = (self.Abulk * self.Esat() * self.Leff + self.Vgsteff) / (self.Pclm * self.Abulk * self.Esat() * self.lit()) * (Vds - Vdsat)
        theta_rout  = self.Pdibl1 * (np.exp(-self.Drout * self.Leff / (2 * self.lit())) + 2 * np.exp(-self.Drout * self.Leff / self.lit())) + self.Pdibl2
        V_ADIBL     = (self.Vgsteff + 2 * self.v_t(T)) / (theta_rout * (1 + self.Pdiblb * self.Vbseff)) * (1 - self.Abulk * Vdsat / (self.Abulk * Vdsat + self.Vgsteff + 2 * self.v_t(T)))
        V_A         = V_Asat + (1 + self.Pvag * self.Vgsteff / (self.Esat() * self.Leff)) * (1 / V_ACLM + 1 / V_ADIBL)**-1
        # Substrate current induced body effect
        V_ASCBE     = np.exp(self.Pscbe1 * self.lit() / (Vds - Vdsat)) * self.Leff / self.Pscbe2
        # Saturation current with all effects
        I_ds        = I_dsat * (1 + (Vds - Vdsat) / V_A) * (1 + (Vds - Vdsat) / V_ASCBE)
        return I_ds
    
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
        self.calculate_V_th(Vds, Vbs, T)
        self.calculate_Vgsteff(Vgs, Vbs, T)
        self.calculate_mobility(Vgs, T)
        self.calculate_Abulk(T)
        self.calculate_Vdseff(Vds, Vgs, Vbs, T)
        # Determine operation region and calculate current
        if self.Vgsteff <= 0:  # Subthreshold region
            I_ds = self.calculate_subthreshold_current(Vgs, Vds, T)
        else:
            if self.Vdseff < self.Vdsat:  # Linear region
                I_ds = self.calculate_linear_current(self.Vdseff, T)
            else:  # Saturation region
                I_ds = self.calculate_saturation_current(Vgs, self.Vdseff, Vbs, T)
        return I_ds
#? -------------------------------------------------------------------------------
if __name__ == "__main__":
    model = BSIM3v3_Model()
    #! ------------------------------
    # Test 1: Vth vs Vds
    vds_range   = np.linspace(0, 10, 50)
    vth_vds     = [model.calculate_V_th(vds, 0, 400) for vds in vds_range]
    
    plt.figure(figsize=(10, 6))
    plt.plot(vds_range, vth_vds)
    plt.title('Threshold Voltage vs Drain-Source Voltage')
    plt.xlabel('Vds (V)')
    plt.ylabel('Vth (V)')
    plt.grid(True)
    plt.show()
    #! ------------------------------
    # Test 2: Id vs Vgs for different Vds
    vgs_range   = np.linspace(0, 15, 50)
    vds_values  = np.linspace(0, 10, 50)
    plt.figure(figsize=(10, 6))
    for vds in vds_values:
        ids = [model.compute(vgs, vds) for vgs in vgs_range]
        plt.plot(vgs_range, ids, label=f'Vds={vds}V')
    
    plt.title('Drain Current vs Gate-Source Voltage')
    plt.xlabel('Vgs (V)')
    plt.ylabel('Id (A)')
    # plt.legend()
    plt.grid(True)
    plt.yscale('log')
    plt.show()
    #! ------------------------------
    # Test 3: Id vs Vds for different Vgs
    vds_range   = np.linspace(0, 10, 50)
    vgs_values  = np.linspace(0, 15, 50)
    
    plt.figure(figsize=(10, 6))
    for vgs in vgs_values:
        ids = [model.compute(vgs, vds) for vds in vds_range]
        plt.plot(vds_range, ids, label=f'Vgs={vgs}V')
    
    plt.title('Drain Current vs Drain-Source Voltage')
    plt.xlabel('Vds (V)')
    plt.ylabel('Id (A)')
    # plt.legend()
    plt.grid(True)
    plt.show()
#? -------------------------------------------------------------------------------
