import math
import copy
import pandas            as pd
import matplotlib.pyplot as plt
from earth               import Earth
from graphs              import *
from pyquaternion        import Quaternion
from rotation_matrix     import rotate_Z
from ground_track        import calc_distance_to_horizon
import simplekml



class FlightRecorder(object):

    def __init__(self):

        cols            = ['t','ax','ay','az','px_rel','py_rel','pz_rel','px','py','pz','vx','vy','vz','s1px_rel','s1py_rel','s1pz_rel','s1_lox','s1_fuel','s2_lox','s2_fuel','alt','q','v','a','dr']
        self.data       = pd.DataFrame(columns = cols)
        self.counter    = 1
        self.kml        = simplekml.Kml()

        self.trajectory = self.kml.newlinestring(name="Trajectory")
        # self.stage1_trajectory = self.kml.newlinestring(name="Stage1 Trajectory")
        # self.fairing_trajectory = self.kml.newlinestring(name="Fairing Trajectory")
        self.ground_track  = self.kml.newlinestring(name="Ground Track")
        self.ground_track1 = self.kml.newlinestring(name="Ground Track 1")
        self.ground_track2 = self.kml.newlinestring(name="Ground Track 2")
        self.ground_track.style.linestyle.color = '77000000'
        self.ground_track1.style.linestyle.color = '77000000'
        self.ground_track2.style.linestyle.color = '77000000'

        self.trajectory.altitudemode = simplekml.AltitudeMode.relativetoground
        # self.stage1_trajectory.altitudemode = simplekml.AltitudeMode.relativetoground
        # self.fairing_trajectory.altitudemode = simplekml.AltitudeMode.relativetoground
        self.ground_track.altitudemode = simplekml.AltitudeMode.relativetoground
        self.ground_track1.altitudemode = simplekml.AltitudeMode.relativetoground
        self.ground_track2.altitudemode = simplekml.AltitudeMode.relativetoground

    def record_data(self, elapsed, acceleration, rocket, drag):

        stage1       = rocket.stages[0]
        stage2       = rocket.stages[1]
        s1           = stage1.state.vector
        s1_pos       = Vector3D([s1[0].p, s1[1].p, s1[2].p])
        s1_pos_rel   = rotate_Z(-rocket.params.theta * self.counter, s1_pos)
        pos_rel      = rotate_Z(-rocket.params.theta * self.counter, rocket.position)
        f            = rocket.fairing.state.vector
        f_pos        = Vector3D([f[0].p, f[1].p, f[2].p])
        f_pos_rel    = rotate_Z(-rocket.params.theta * self.counter, f_pos)

        g            = Earth.calc_gravity(rocket.position.magnitude())
        gravity      = rocket.position.unit().inverse()
        gravity.scale(g)
        acceleration.subtract(gravity)


        data = [    elapsed,
                    acceleration.x,         acceleration.y,         acceleration.z,
                    pos_rel.x,              pos_rel.y,              pos_rel.z,
                    rocket.position.x,      rocket.position.y,      rocket.position.z,
                    rocket.velocity.x,      rocket.velocity.y,      rocket.velocity.z,
                    s1[0].p,                s1[1].p,                s1[2].p,
                    stage1.tanks[0].lox_mass,   stage1.tanks[0].fuel_mass,
                    stage2.tanks[0].lox_mass,   stage2.tanks[0].fuel_mass,
                    rocket.altitude,        drag,
                    rocket.velocity.magnitude(), acceleration.magnitude(), rocket.downrange   ]


        if self.counter % 10.0 == 0:
            lat, lon, alt = Earth.get_lat_lon(pos_rel)
            # lat, lon, alt = Earth.get_lat_lon(rocket.position)

            self.trajectory.coords.addcoordinates([(math.degrees(lon),math.degrees(lat),round(rocket.altitude))])
            self.ground_track.coords.addcoordinates([(math.degrees(lon),math.degrees(lat),0)])

            # if rocket.params.recover:
            #     lat, lon, alt = Earth.get_lat_lon(s1_pos_rel)
            #     self.stage1_trajectory.coords.addcoordinates([(math.degrees(lon),math.degrees(lat),round(alt))])
            #
            #     lat, lon, alt = Earth.get_lat_lon(f_pos_rel)
            #     self.fairing_trajectory.coords.addcoordinates([(math.degrees(lon),math.degrees(lat),round(alt))])

            if elapsed >= 10.0:
                # ground track width
                d, theta     = calc_distance_to_horizon(pos_rel)
                A            = rocket.velocity_rel
                B            = pos_rel.unit().inverse()
                proj         = A.dot(B) / B.dot(B)
                B.scale(proj)
                axis         = A.difference(B)
                q1           = Quaternion(axis=axis.points, radians=math.pi*0.5)
                q2           = Quaternion(axis=axis.points, radians=-math.pi*0.5)
                w            = pos_rel.unit().inverse()
                w_prime1     = q1.rotate(w.points)
                w_prime2     = q2.rotate(w.points)
                vec1         = Vector3D(w_prime1)
                vec2         = Vector3D(w_prime2)
                vec1.scale(d)
                vec2.scale(d)
                vec1.add(pos_rel)
                vec2.add(pos_rel)

                lat, lon, alt = Earth.get_lat_lon(vec1)
                self.ground_track1.coords.addcoordinates([(math.degrees(lon),math.degrees(lat),0)])
                lat, lon, alt = Earth.get_lat_lon(vec2)
                self.ground_track2.coords.addcoordinates([(math.degrees(lon),math.degrees(lat),0)])

            # self.data.loc[self.counter/10] = data
            self.data.loc[self.counter] = data

        if elapsed > 0.0:
            self.counter += 1




    def save_kml(self):

        self.kml.save("trajectory.kml")




    def graph(self, *args):

        height = len(args) * 4

        fig, axes = plt.subplots(nrows=len(args),ncols=1,figsize=(13,height))

        if len(args) > 1:

            for i, arg in enumerate(args):
                if arg == 'Altitude':
                    plot_altitude(self.data, axes[i])
                elif arg == 'Velocity':
                    plot_velocity(self.data, axes[i])
                elif arg == 'Drag':
                    plot_drag(self.data, axes[i])
                elif arg == 'Acceleration':
                    plot_acceleration(self.data, axes[i])
                elif arg == 'Propellant':
                    plot_propellant(self.data, axes[i])
                elif arg == 'Downrange':
                    plot_downrange(self.data, axes[i])




            for a in axes:
                a.legend()
                a.grid(color='#999999', ls=':', linewidth=0.6)
                a.set_xlim(left=0)
                a.set_xticklabels(a.get_xticks() * 0.1)




        else:

            if args[0] == 'Altitude':
                plot_altitude(self.data, axes)
            elif args[0] == 'Velocity':
                plot_velocity(self.data, axes)
            elif args[0] == 'Drag':
                plot_drag(self.data, axes)
            elif args[0] == 'Acceleration':
                plot_acceleration(self.data, axes)
            elif args[0] == 'Propellant':
                plot_propellant(self.data, axes)
            elif args[0] == 'Downrange':
                plot_downrange(self.data, axes)

            axes.legend()
            axes.grid(color='#999999', ls=':', linewidth=0.6)
            axes.set_xlim(left=0)
            axes.set_xlabel('Seconds')
            axes.set_xticklabels(axes.get_xticks() * 0.1)


        plt.tight_layout()
        plt.show()
