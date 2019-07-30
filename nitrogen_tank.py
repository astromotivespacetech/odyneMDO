from math                       import pi
from structures                 import *
from units                      import *
from constants                  import atm_1, T_stp
from functions                  import normalize
from commodities.carbon_fiber   import CarbonFiber
from commodities.n2             import N2
from engine                     import Hadley
from pressure                   import ideal_gas



class NitrogenTank(object):

    commodity                        = N2
    material                         = CarbonFiber

    def __init__(self, rocket=None, stage=None):

        self.engine                  = rocket.params.engine  if rocket else Hadley
        self.engines                 = len(stage.engines)    if stage  else 1

        self.config()



    def config(self):

        chill                        = self.engine.Chill[NitrogenTank.commodity.id]
        start                        = self.engine.Start[NitrogenTank.commodity.id]
        shutdown                     = self.engine.Shutdown[NitrogenTank.commodity.id]

        burn_duration                = 180.0
        IPS_flow_rate                = self.engine.IPS_purge[NitrogenTank.commodity.id]
        IPS_mass                     = IPS_flow_rate * burn_duration
        resid                        = 0.5

        self.commodity_mass          = (chill + start + shutdown + IPS_mass) * self.engines / resid
        moles                        = self.commodity_mass * 1000 / NitrogenTank.commodity.mol
        self.pressure                = psi2pascal(5000.0)
        self.volume                  = ideal_gas(T_stp, moles, self.pressure)
        self.num_tanks, self.dry_mass = self.steelhead_composites(self.volume)
        self.mass                    = self.dry_mass + self.commodity_mass





    def update_mass(self):

        self.mass                    = self.dry_mass + self.commodity_mass



    def steelhead_composites(self, vol):
        ''' Returns mass of Steelhead Composites COPV given a volume.

            https://steelheadcomposites.com/composite-pressure-vessels/
        '''

        steelhead_composites_tank_mass = [lbm2kilogram(26.0), lbm2kilogram(12.0)]     # [kg]
        steelhead_composites_tank_vol  = [19.0, 10.0]                                 # [L]
        stage                          = 1 if self.engines == 1 else 0
        num_tanks                      = 0

        while num_tanks * steelhead_composites_tank_vol[stage] <= cubicm2liter(vol):
            num_tanks += 1

        return num_tanks, num_tanks * steelhead_composites_tank_mass[stage]




if __name__ == "__main__":

    tank = NitrogenTank()
    tank.engines = 1
    tank.config()

    print( "Volume: %.2f L" %  (cubicm2liter(tank.volume)) )
    print( "Number of tanks: %i" % (tank.num_tanks))
    print( "Dry Mass: %.2f kg" % (tank.dry_mass))
    print( "Commodity Mass: %.2f kg" % (tank.commodity_mass))
    print( "Mass: %.2f kg" % (tank.mass))


# end
