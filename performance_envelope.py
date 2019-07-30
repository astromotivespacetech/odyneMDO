import copy
import numpy                as np
import pandas               as pd
import matplotlib.pyplot    as plt
import matplotlib.tri       as tri
from rocket                 import compute_max_payload
from params                 import Params
from azimuth                import calc_launch_azimuth




def calc_performance(inclinations, apogees):

        data                            = np.ndarray(shape=(len(inclinations), len(apogees)))

        for x, i in enumerate(inclinations):

            Params.inclination          = i
            Params.launch_site          = 'psc-kodiak' if i >= 60.0 else 'hawaii'
            Params.latitude             = Params.coordinates[Params.launch_site][0]
            Params.longitude            = Params.coordinates[Params.launch_site][1]
            Params.altitude             = Params.coordinates[Params.launch_site][2]

            for y, j in enumerate(apogees):

                Params.apogee           = j
                Params.perigee          = j
                Params.launch_azimuth   = calc_launch_azimuth(Params.latitude, Params.inclination, Params.injection, Params.apogee, Params.direction)
                rocket                  = compute_max_payload()

                data[x][y]              = rocket.payload


        df                              = pd.DataFrame(index=inclinations, columns=apogees, data=data)
        df.to_excel('performance_envelope2.xlsx')




def plot_performance_envelope(inclinations, altitudes, file):



    X, Y                                = np.meshgrid(inclinations, altitudes)
    df                                  = pd.read_excel(file)
    levels                              = np.linspace(100, 180, 21)
    df                                  = df.transpose()
    fig, ax                             = plt.subplots()
    contour                             = ax.contour(X,Y,df.values, levels)
    ax.grid(linestyle=':', linewidth='0.5', color='grey')
    ax.clabel(contour, fontsize=9, inline=1)
    plt.colorbar(contour);
    plt.show()



if __name__ == "__main__":

    # all apogees and all inclinations
    inclinations                        = [i*10.  for i in range(3,10,1)]
    apogees                             = [i*100. for i in range(3,11,1)]

    # calc_performance(inclinations, apogees)

    plot_performance_envelope(inclinations, apogees, 'performance_envelope.xlsx')










# end
