from units              import *
from constants          import T_stp
from commodities.helium import Helium
from pressure           import moles, ideal_gas



class HeliumTank(object):

    def __init__(self, stage):
        self.stage          = stage
        self.moles          = moles(T_stp, HeliumTank.pressure[stage], HeliumTank.volume[stage])
        self.commodity_mass = self.moles * HeliumTank.commodity.mol * 0.001
        self.dry_mass       = HeliumTank.dry_mass[stage]
        self.mass           = self.dry_mass + self.commodity_mass

    commodity               = Helium
    pressure                = [psi2pascal(4000),   psi2pascal(5000)]            # [Pascal]
    dry_mass                = [lbm2kilogram(29.5), lbm2kilogram(12.0)]          # [kg] 1st stage: 2x CTD, Inc, 2nd stage: 1x Steelhead
    volume                  = [liter2cubicm(33.8), liter2cubicm(10.0)]








if __name__ == "__main__":

    stage = 0
    tank = HeliumTank(stage)
    print("Helium Mass: %.2f kg"   % tank.commodity_mass)
    print("Pressure: %.2f psi"     % pascal2psi(HeliumTank.pressure[stage]))
    print("Volume: %.2f L"         % cubicm2liter(tank.volume[stage]))
    print("Dry Mass: %.2f kg"      % tank.dry_mass)
    print("Total Mass: %.2f kg"    % tank.mass)
