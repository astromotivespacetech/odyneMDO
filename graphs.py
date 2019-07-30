import numpy                as np
import pandas               as pd
import matplotlib.pyplot    as plt
from vector3d               import Vector3D
from constants              import g_earth



def plot_altitude(df, ax):

    ax.plot(df['alt']/1000, color='#0090c0', label='Altitude', ls='-', linewidth=0.7)
    ax.set_ylabel('Altitude [km]')



def plot_velocity(df, ax):

    ax.plot(-df['vx'], color='#cc2a36', label='yVel', ls=':', linewidth=0.8)
    ax.plot(-df['vy'], color='#5555ff', label='xVel', ls=':', linewidth=0.8)
    ax.plot(-df['vz'], color='#9900cc', label='zVel', ls=':', linewidth=0.8)
    ax.plot(df['v'], color='#000000', label='Vel', ls='-', linewidth=0.8)
    ax.set_ylabel('Velocity [m/s]')



def plot_drag(df, ax):

    ymax = max(df['q'])
    xpos = df['q'].values.tolist().index(ymax)

    ax.plot(df['q'], color='#0090c0', label='Drag', ls='-', linewidth=0.8)
    ax.set_ylabel('Drag [N]')
    ax.set_ylim(0, ymax + 1000)
    ax.annotate('Max-Q: ' + str(round(ymax)) + 'N, ' + str(xpos) + ' seconds', xy=(xpos, ymax), xytext=(xpos, ymax+100))



def plot_acceleration(df, ax):

    ax.plot(df['a']/g_earth, color='#0090c0', label='Accel', ls='-', linewidth=0.8)
    ax.set_ylabel('Acceleration [g]')



def plot_propellant(df, ax):

    ax.plot(df['s1_fuel'], color='#c09000', label='Stage 1 Fuel', ls='-', linewidth=0.8)
    ax.plot(df['s2_fuel'], color='#c09000', label='Stage 2 Fuel', ls='-', linewidth=0.8)
    ax.plot(df['s1_lox'], color='#0090c0', label='Stage 1 LOx', ls='-', linewidth=0.8)
    ax.plot(df['s2_lox'], color='#0090c0', label='Stage 2 LOx', ls='-', linewidth=0.8)
    ax.set_ylabel('Propellant Mass [kg]')


def plot_downrange(df, ax):

    ax.plot(df['dr']/1000, color='#0090c0', label='Downrange', ls='-', linewidth=0.7)
    ax.set_ylabel('Distance [km]')
