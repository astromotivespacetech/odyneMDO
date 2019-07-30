from __future__     import division, print_function
import copy
from openmdao.api   import Problem, Group, ExplicitComponent, ScipyOptimizeDriver, ExecComp, IndepVarComp
from rocket         import Rocket
from params         import Params

Params.optimized = False



class rocketDV(ExplicitComponent):

    def setup(self):

        for i in range(len(Params.mdo_ratios)):
            self.add_input('v'+str(i), shape=1)
        self.add_output('error', shape=1)
        self.declare_partials('*', '*', method='fd')



    def compute(self, inputs, outputs):

        params              = copy.deepcopy(Params)

        params.payload      = Params.mdo_payload

        params.mass_ratios  = [inputs[i][0] for i in inputs]
        odyne               = Rocket(params)

        while abs(odyne.thrust_GTOW - Params.thrust_GTOW) > 0.01:
            params.payload  += (odyne.thrust_GTOW - Params.thrust_GTOW) * 10
            odyne           = Rocket(params)
        print(odyne.payload, odyne.thrust_GTOW)

        if odyne.payload <= 0.0:
            odyne.modify_payload(0.0)
            odyne.trajectory.calc_pitchover()
        else:
            odyne.trajectory.optimize_pitchover()

        outputs['error']    = odyne.trajectory.simulate()



if __name__ == "__main__":

    prob = Problem()
    model = prob.model = Group()

    model.add_subsystem('dV', rocketDV())

    for i, mr in enumerate(Params.mdo_ratios):
        model.add_subsystem('mr' + str(i), IndepVarComp('v' + str(i), mr ))
        model.connect('mr'+str(i)+'.v'+str(i), 'dV.v'+str(i))


#
#        Constrained Optimization By Linear Approximation Algorithm
#=============================================================================

    prob.driver = ScipyOptimizeDriver()
    # prob.driver.options['optimizer'] = 'Nelder-Mead'
    prob.driver.options['optimizer'] = 'COBYLA'

    for i in range(len(Params.mdo_ratios)):
        prob.model.add_design_var('mr'+str(i)+'.v'+str(i), lower=1.0, upper=24.0)

    prob.model.add_objective('dV.error')

    prob.setup()

    print('T+ | PAYLOAD | PROP_RESID | ALTITUDE | VELOCITY | MASS RATIOS | TRAJECTORY PARAMS | ORBIT INJECTION\n')

    prob.run_driver()

    print('Optimization Finished')
