import math
from earth      import Earth
from params     import Params
from functions  import normalize
from vector3d   import Vector3D



class Render3D(object):

    def __init__(self, data):

        import vpython as vp
        vp.scene.visible = False

        self.vp            = vp
        self.data          = data
        vp.scene.width     = 1280
        vp.scene.height    = 720
        vp.scene.lights    = []
        vp.scene.ambient   = vp.color.gray(0.3)
        vp.scene.camera.rotate(angle=math.radians(Params.longitude), axis=vp.vector(0, 1, 0), origin=vp.vector(0, 0, 0))
        vp.scene.camera.rotate(angle=-math.pi/4, axis=vp.vector(0, 0, 1), origin=vp.vector(0, 0, 0))

        x                  = normalize(data.loc[0][5], 0, Earth.radius_equator)
        y                  = normalize(data.loc[0][6], 0, Earth.radius_equator)
        z                  = normalize(data.loc[0][4], 0, Earth.radius_equator)
        vp.distant_light(direction=vp.vector(x,y,z), color=vp.vector(0.8, 0.8, 0.8))

        map                = "images/8081_earthmap10k.jpg"
        # map                = "images/land_shallow_topo_21600.png"

        vp.sphere(pos=vp.vector(0, 0, 0), radius=Earth.radius_equator, texture=map, shininess=0.9)
        vp.ring(  pos=vp.vector(0, 0, 0), radius=Earth.radius_equator, axis=vp.vector(0, 1, 0), thickness=6000,  color=vp.color.black)

        vp.scene.waitfor("textures")
        vp.scene.visible = True


    def plot(self):

        vp                 = self.vp
        data               = self.data

        start              = vp.sphere(radius=1, pos=vp.vector(data.loc[0][5],  data.loc[0][6],  data.loc[0][4]))
        vp.scene.camera.follow(start)

        c                  = vp.curve(radius=3000.0, color=vp.color.yellow)

        for d in self.data:
            c.append(vp.vector(d[5], d[6], d[4]))




    def animate(self):

        vp                 = self.vp
        data               = self.data

        # (175.02557617436787, -351.0469968150348, 0.0) # initial true velocity vector
        # pointer = vp.arrow(pos=vp.vector(data[0][5],  data[0][6],  data[0][4]), axis=vp.vector(-351.0469968150348 * 100, 0.0, 175.02557617436787 * 100), shaftwidth=3000)

        s                  = vp.sphere(radius=10.0, color=vp.color.red, make_trail=True)
        c                  = vp.sphere(radius=10.0, color=vp.color.yellow, make_trail=True)
        vp.scene.camera.follow(c)
        label_elapsed      = vp.label( pixel_pos=True, pos=vp.vector(vp.scene.width - 180,vp.scene.height - 80,0),  text='Elapsed',   box=False, align='left')
        label_velocity     = vp.label( pixel_pos=True, pos=vp.vector(vp.scene.width - 180,vp.scene.height - 100,0), text='Velocity',  box=False, align='left')
        label_altitude     = vp.label( pixel_pos=True, pos=vp.vector(vp.scene.width - 180,vp.scene.height - 120,0), text='Altitude',  box=False, align='left')
        label_downrange    = vp.label( pixel_pos=True, pos=vp.vector(vp.scene.width - 180,vp.scene.height - 140,0), text='Downrange', box=False, align='left')


        for i in range(len(data)):
            vp.rate(100)
            c.pos          = vp.vector(data.loc[i][5],  data.loc[i][6],  data.loc[i][4])
            s.pos          = vp.vector(data.loc[i][14], data.loc[i][15], data.loc[i][13])
            elapsed        = 'Elapsed    '  + str(round(data.loc[i][0])) + ' s'
            v              = Vector3D([data.loc[i][10], data.loc[i][11], data.loc[i][12]]).magnitude()
            velocity       = 'Velocity    ' + str(round(v)) + ' m/s'
            # a              = Vector3D([data.loc[i][7], data.loc[i][8], data.loc[i][9]]).magnitude()
            altitude       = 'Altitude    ' + str(round(data.loc[i][20] * 0.001, 1)) + ' km'
            downrange      = 'Downrange     ' + str(round(data.loc[i][21] * 0.001, 1)) + ' km'

            label_elapsed.text      = elapsed
            label_velocity.text     = velocity
            label_altitude.text     = altitude
            label_downrange.text    = downrange






# end
