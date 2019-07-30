import dv
from constants                          import geostationary
from units                              import cubicm2liter
from hohmann_transfer                   import calc_hohmann_dv
from R4D                                import R_4D
from commodities.dinitrogen_tetroxide   import Dinitrogen_Tetroxide
from commodities.monomethylhydrazine    import Monomethylhydrazine



def calc_geo_transfer(output=False):

    alt1        = 150000     # parking orbit
    alt2        = geostationary   # geostationary altitude
    deltav      = calc_hohmann_dv(alt1, alt2)[0]
    init        = 185.0 # [kg]
    isp         = R_4D.Isp
    mf          = dv.calc_mf(init, deltav, isp)
    payload     = 25.0 # [kg]
    m_prop      = init - mf
    m_tank      = mf - payload - R_4D.mass
    m_fuel      = m_prop / (1 + R_4D.ox_f_ratio)
    m_ox        = m_prop - m_fuel
    v_fuel      = m_fuel / Monomethylhydrazine.rho
    v_ox        = m_ox   / Dinitrogen_Tetroxide.rho

    if output:
        print("Total Mass: %.2f [kg]"        % (init))
        print("Prop Mass: %.2f [kg]"         % (m_prop))
        print("Dry Mass: %.2f [kg]"          % (mf))
        print("Payload: %.1f [kg]"           % (payload))
        print("Propulsion Mass: %.2f [kg]"   % (R_4D.mass))
        print("Total Tank Mass: %.2f [kg]"   % (m_tank))
        print("Fuel Mass: %.2f [kg]"         % (m_fuel))
        print("Fuel Volume: %.2f [L]"        % (cubicm2liter(v_fuel)))
        print("Oxidizer Mass: %.2f [kg]"     % (m_ox))
        print("Oxidizer Volume: %.2f [L]"    % (cubicm2liter(v_ox)))
        print("Delta V: %.2f [m/s]"          % (deltav))

    return (m_tank, m_fuel, m_ox)


if __name__ == "__main__":

    calc_geo_transfer(output=True)
