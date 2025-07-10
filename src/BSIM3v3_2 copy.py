
#? -------------------------------------------------------------------------------
import numpy as np
#? -------------------------------------------------------------------------------
class BSIM3v3_Model:
    """
    The model includes:
    - Threshold voltage calculation with short-channel, narrow width, and DIBL effects :Drain-Induced Barrier Lowering (DIBL)
    - Mobility degradation effects
    - Velocity saturation
    - Channel length modulation
    - Subthreshold conduction
    - Temperature effects
    - Parasitic resistance effects
    """
    def __init__(self):

        # Physical constants (SI units)
        self.epsSi    = 11.7 * 8.854e-12       # F/m,   Silicon permittivity
        self.epsOx    = 3.9 * 8.854e-12        # F/m,   Silicon dioxide permittivity
        self.q        = 1.602e-19              # C,     Electron charge
        self.k_B      = 1.38e-23               # J/K,   Boltzmann constant
        self.NI0      = 1.45e16                # m-3,   Intrinsic carrier concentration at 300K
        
        # Threshold voltage related parameters
        self.Vth0     = 2.4                   # V,     Zero-bias threshold voltage
        self.K1       = 0.5                    # √V,    First body effect coefficient
        self.K2       = 0.01                   # -,     Second body effect coefficient
        self.K3       = 80.0                   # -,     Narrow width effect coefficient
        self.K3b      = 0                      # -,     Body effect on narrow width coefficient
        self.Dvt0     = 2.2                    # -,     Short-channel effect coefficient at Vbs=0
        self.Dvt1     = 0.53                   # -,     Short-channel effect coefficient
        self.Dvt2     = -0.032                 # 1/V,   Short-channel effect coefficient for body bias
        self.Dvt0w    = 0.0                    # -,     Narrow width effect coefficient at Vbs=0
        self.Dvt1w    = 5.3e6                  # -,     Narrow width effect coefficient
        self.Dvt2w    = -0.032                 # 1/V,   Narrow width effect coefficient for body bias
        self.Nlx      = 1.47e-7                # m,     Lateral non-uniform doping parameter
        self.W0       = 2.5e-6                 # m,     Narrow width parameter
        self.Voff     = -0.08                  # V,     Offset voltage for subthreshold current
        self.Keta     = -0.047                 # -,     Body effect coefficient for Voff
        
        # Mobility parameters
        self.mobMod   = 2                      # -,     Mobility model selector
        self.U0       = 0.35                   # m²/V·s, Low-field mobility (final tuned value)
        self.Ua       = 2.25e-9                # m/V,   First-order mobility degradation coefficient
        self.Ub       = 5.87e-19               # (m/V)², Second-order mobility degradation coefficient
        self.Uc       = -0.046                 # -,     Body-effect coefficient for mobility
        self.Ua1      = 4.31e-9                # m/V,   First-order mobility degradation coefficient
        self.Ub1      = -7.61e-18              # (m/V)², Second-order mobility degradation coefficient
        self.Uc1      = -0.056                 # -,     Body-effect coefficient for mobility
        
        # Velocity saturation parameters
        self.VSAT     = 5.0e5                  # m/s,   Saturation velocity (near ballistic limit)
        self.A0       = 1.0                    # -,     Bulk charge effect coefficient
        self.A1       = 0.0                    # -,     Saturation voltage parameter
        self.A2       = 1.0                    # -,     Saturation voltage parameter
        self.B0       = 0.0                    # -,     Width effect on Abulk
        self.B1       = 0.0                    # -,     Width effect on Abulk
        self.At       = 4.0e4                  # m/s,   Velocity saturation temperature coefficient
        
        # DIBL and substrate effect parameters
        self.Pclm     = 1.1                    # -,     Channel length modulation coefficient
        self.Drout    = 0.56                   # -,     Output resistance DIBL coefficient
        self.Pvag     = 1e6                    # 1/V,   Gate voltage effect on output resistance
        self.Alpha0   = 1.2e-6                 # -,     Substrate current parameter
        self.Alpha1   = 0.5e-6                 # -,     Substrate current parameter
        self.Beta0    = 3.0                    # V/m,   Substrate current parameter
        self.Dsub     = 1.2                    # -,     DIBL in subthreshold
        self.Eta0     = 0.15                   # -,     DIBL in strong inversion
        self.Etab     = -0.12                  # -,     Body effect on DIBL
        self.Pdiblc1  = 0.45                   # -,     DIBL coefficient
        self.Pdiblc2  = 0.45                   # -,     DIBL coefficient
        self.Pdiblb   = -0.08                  # -,     Body bias effect on DIBL
        
        # Geometry parameters
        self.Leff     = 50e-9                  # m,     Effective channel length (50nm)
        self.Weff     = 2000e-6                # m,     Effective channel width (2mm)
        self.Ldrawn   = 0.5e-6                 # m,     Drawn channel length
        self.Wdrawn   = 2000e-6                # m,     Drawn channel width
        self.Xj       = 0.5e-6                 # m,     Junction depth
        self.Tox      = 1.2e-9                 # m,     Oxide thickness (1.2nm)
        self.Toxm     = 1.2e-9                 # m,     Oxide thickness for modeling
        self.Cox      = self.epsOx/self.Tox    # F/m²,  Oxide capacitance (~0.029 F/m²)
        
        # Geometry adjustment parameters
        self.Wint     = 0.0                    # m,     Internal width for narrow width effects
        self.Wl       = 0.0                    # m,     Length dependence coefficient for width
        self.Ww       = 0.0                    # m,     Width dependence coefficient for width
        self.Wln      = 0.0                    # -,     Length dependence exponent for width
        self.Wwn      = 0.0                    # -,     Width dependence exponent for width
        self.Lint     = 0.0                    # m,     Internal length for narrow width effects
        self.Ll       = 0.0                    # m,     Length dependence coefficient for length
        self.Lw       = 0.0                    # m,     Width dependence coefficient for length
        self.Lln      = 0.0                    # -,     Length dependence exponent for length
        self.Lwn      = 0.0                    # -,     Width dependence exponent for length
        self.dW       = self.Wint + self.Wl/self.Ldrawn**self.Wln + self.Ww/self.Wdrawn**self.Wwn
        self.dL       = self.Lint + self.Ll/self.Ldrawn**self.Lln + self.Lw/self.Wdrawn**self.Lwn
        
        # Doping concentrations
        self.Nch      = 5e23                   # m-3,   Channel doping concentration
        self.Ngate    = 1e25                   # m-3,   Poly doping concentration
        self.Nds      = 1e26                   # m-3,   Source/drain doping concentration
        
        # Parasitic resistance
        self.Rdsw     = 0.5                    # Ω·µm,  Source/drain resistance (low for high current)
        self.Pr       = 1.0                    # -,     Resistance prefactor
        self.Wr       = 1.0                    # -,     Width dependence for resistance
        self.Prwb     = 0.1                    # -,     Body effect on resistance
        self.Prwg     = 0.0                    # -,     Gate effect on resistance
        
        # Subthreshold parameters
        self.n        = 1.5                    # -,     Subthreshold swing coefficient
        self.delta    = 0.005                  # -,     Smoothing parameter
        self.Nfactor  = 0                      # -,     Subthreshold slope factor
        
        # Temperature parameters
        self.Tnom     = 300.0                  # K,     Nominal temperature
        self.Kt1      = -0.15                  # V,     Temperature coefficient for Vth
        self.Kt1l     = 1e-9                   # V·m,   Temperature coefficient for Vth
        self.Kt2      = 0.03                   # -,     Temperature coefficient for Vth
        self.Ute      = -1.8                   # -,     Mobility temperature exponent
        self.Ags      = 0.0                    # -,     Body effect coefficient for bulk charge
        
        # Additional parameters
        self.Pscbe1   = 4.24e8                 # -,     Substrate current body-effect coefficient 1
        self.Pscbe2   = 1.0e-5                 # -,     Substrate current body-effect coefficient 2
        self.NITEXP   = 1.5                    # -,     Exponent for temperature dependence of ni
        
        # Capacitance parameters
        self.Cit      = 0.0                    # F/m²,  Interface trap capacitance
        self.Citd     = 0                      # F/m²,  Interface trap capacitance derivative
        self.Citb     = 0                      # F/m²,  Interface trap capacitance body effect
        self.Cdsc     = 0                      # F,     Axial capacitance
        self.Cdscd    = 0                      # F/Vm², Drain-bias sensitivity of Cdsc
        self.Cdscb    = 0                      # F/Vm², Body-bias sensitivity of Cdsc
        self.Abulk    = 0.8                    # -,     Bulk charge effect coefficient

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
        """Calculate threshold voltage (Vth) based on BSIM3v3 model (Eq. 45).
        
        Includes:
        - Ideal threshold voltage
        - Non-uniform vertical doping effect (ΔVth(1))
        - Non-uniform lateral doping effect (ΔVth(2))
        - Short-channel effects (ΔVth(3))
        - Narrow width effects (ΔVth(4))
        - DIBL effects (ΔVth(5))
        - Temperature effects
        
        Args:
            Vds (float): Drain-source voltage in volts
            Vbs (float): Bulk-source voltage in volts
            T (float): Temperature in Kelvin
            
        Returns:
            float: Threshold voltage in volts
        """
        Phi_s       = self.Phi_s(T)  # Surface potential
        Vbi         = self.Vbi(T)  # Built-in potential
        Vbc         = 0.9 * (Phi_s - self.K1**2 / (4 * self.K2**2))
        Vbseff      = Vbc + 0.5 * (Vbs - Vbc - 0.001 + np.sqrt((Vbs - Vbc - 0.001)**2 + 4 * 0.001 * Vbc))
        Xdep        = np.sqrt(2 * self.epsSi * (Phi_s - Vbseff) / (self.q * self.Nch))
        lt0         = np.sqrt(self.epsSi * self.Tox * Xdep / self.epsOx)
        lt          = lt0 * (1 + self.Dvt2 * Vbseff)
        ltw         = lt0 * (1 + self.Dvt2w * Vbseff)
        K1ox        = self.K1 * (self.Tox / self.Toxm)
        K2ox        = self.K2 * (self.Tox / self.Toxm)
        V_Tideal    = self.Vth0
        # ΔVth(1): Non-uniform vertical doping effect 
        delta_Vth1 = K1ox * np.sqrt(Phi_s - Vbseff) - K2ox * Vbseff
        # ΔVth(2): Non-uniform lateral doping effect 
        delta_Vth2 = K1ox * (np.sqrt(1 + self.Nlx/self.Leff) - 1) * np.sqrt(Phi_s)
        # ΔVth(3): Short-channel effect 
        delta_Vth3 = self.Dvt0 * (np.exp(-self.Dvt1 * self.Leff/(2 * lt)) + 
                                2 * np.exp(-self.Dvt1 * self.Leff/lt)) * (Vbi - Phi_s)
        # ΔVth(4): Narrow width effect 
        delta_Vth4 = self.Dvt0w * (np.exp(-self.Dvt1w * self.Weff * self.Leff/(2 * ltw)) + 
                                2 * np.exp(-self.Dvt1w * self.Weff * self.Leff/ltw)) * (Vbi - Phi_s)
        # ΔVth(5): Narrow channel effect 
        delta_Vth5 = (self.K3 + self.K3b * Vbseff) * self.Tox * Phi_s / (self.Weff + self.W0)
        # ΔVth(6): DIBL effect 
        delta_Vth6 = (np.exp(-self.Dsub * self.Leff/(2 * lt0)) + 
                    2 * np.exp(-self.Dsub * self.Leff/lt0)) * (self.Eta0 + self.Etab * Vbseff) * Vds
        # Combine all terms 
        Vth = (V_Tideal + delta_Vth1 + delta_Vth2 - delta_Vth3 - delta_Vth4 + 
            delta_Vth5 - delta_Vth6)
        
        Vth += (self.Kt1 + self.Kt1l/self.Leff + self.Kt2 * Vbseff) 
        
        return Vth
    
    def vth_T_dependent(self,Vds, Vbs, T):
        """Calculate temperature-dependent threshold voltage (Vth) based on BSIM3v3 model."""
        Vth_TNOM    = self.calculate_V_th(Vds, Vbs, self.Tnom)
        delta_T = (T / self.Tnom) - 1
        Vth = (Vth_TNOM + (self.Kt1 + self.Kt1l/self.Leff + self.Kt2 * Vbs) * delta_T)
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
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        # Effective body-source voltage with smoothing (Eq. 2.1.26)
        Xdep   = np.sqrt(2 * self.epsSi * (self.Phi_s(T) - Vbseff) / (self.q * self.Nch))


        Cd = self.epsSi / self.Xdep0(T)
        lt          = np.sqrt(self.epsSi * Xdep * self.Tox / (self.epsOx * (1 + self.Dvt2 * Vbseff)))
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
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        # Effective body-source voltage with smoothing (Eq. 2.1.26)
        Xdep   = np.sqrt(2 * self.epsSi * (self.Phi_s(T) - Vbseff) / (self.q * self.Nch))
        K1ox        = self.K1 * (self.Tox / self.Toxm)
        term1       = 1 + (K1ox / (2 * np.sqrt(self.Phi_s(T) - Vbs))) * (self.A0 * self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * Xdep))) * (1 - self.Ags * np.square(self.Leff / (self.Leff + 2 * np.sqrt(self.Xj * Xdep))))
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
        Vbc         = 0.9 * (self.Phi_s(T) - np.square(self.K1) / (4 * np.square(self.K2)))
        Vbseff      = Vbc + 0.5 * (Vbs - Vbc - self.delta + np.sqrt(np.square(Vbs - Vbc - self.delta) + 4 * self.delta * Vbc))
        Vth     = self.vth_T_dependent(Vds, Vbs, T)  
        Xdep   = np.sqrt(2 * self.epsSi * (self.Phi_s(T) - Vbseff) / (self.q * self.Nch))
        Vgst    = Vgs - Vth
        mob_eff = self.calculate_mobility(Vgs, T,Vds, Vbs)
        n       = 1 + (self.Cit + self.Citd * Vds + self.Citb * Vbseff) / self.Cox + self.Nfactor * self.epsSi / (self.Cox * Xdep)
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
            I_ds = I_dso / (1 + ((Rds * I_dso) / Vds)) #Extrinsic Case (Rds > 0)

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
        Vgsteff     = self.calculate_Vgsteff(Vgs, T, Vds, Vbseff)  # Recalculate Vgsteff for consistency
        self.lit    = np.sqrt(self.epsSi * self.Xj * self.Tox / self.epsOx) #Calculate intrinsic length (lit) for short-channel effects.
        Vdsat       = self.calculate_Vdsat(Vgs, Vbseff, T, Vds)
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
        Calculate substrate current (I_sub) based on BSIM3v3.2.2 model.
        
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