from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import numpy as np
import datetime


def zig_zag_gcode(Trial="",
                  V_star=0.5, 
                  H_star=2, 
                  L=30, 
                  l=1.2, 
                  h=30, 
                  layer_thickness=0.8, 
                  vertical_transition=True, 
                  wipe=True,
                  centered=True,
                  TwoD_preview=True,
                  ThreeD_preview=True,
                  preview_gcode=False,
                  write_gcode=True,
                  write_α_gcode=False,
                  continuous_testing=False,
                  T_n=215,
                  T_b=60,
                  α=1.63,
                  F1=300,
                  Lw=10,
                  Lα=150,
                  Zα=150,
                  D_f=1.75,
                  D_n=0.4,
                  ρ=1.22,
                  X0=50,
                  Y0=100,
                  view_az=225,
                  view_elev=30):


    # Formulaic Inputs

    H = H_star*α*D_n

    # E = (L/(S*V_star))*(((α*D_n)/D_f)**2) # E as manipulated variable
    E = L # only use when NOT using E as manipulated variable

    S = (L/(E*V_star))*(((α*D_n)/D_f)**2) #Feedrate multiplyer (M221 = Feedrate percentage = S * 100)

    if centered == True:
        X0 = 250/2 - L/2
        Y0 = 210/2 - L/2
    else:
        X0 = X0
        Y0 = Y0

    Z0 = H
    Zfα = Zα + 30

    Eα = Lα
    E1 = L

    Xw = X0 - Lw
    Xα = X0 + Lα

    print(f"H = {H}")
#    print(f"E = {E}")
    print(f"S = {S}")

    print(f"1/H* = {1/H_star}")
#     if V_star <= 1/H_star:
#       print("Will accumulate")
#     else:
#       print("Will not accumulate")



    #Line Functions 

    if vertical_transition == True:
        moves_layer = int(L / l * 2) - (L % l > 0)
    else:
        moves_layer = int(L / l *2 ) + 2 * (L % l > 0)

    #layers_cube = h/layer_thickness

    layers_cube = int(h/layer_thickness) + (h % layer_thickness > 0) #Rounds up to next highest interger (better to overestimate height than underestimate)

    if layers_cube == 0:
        layers_cube = 1

    if layers_cube > 1 and (Z0 + (layer_thickness * layers_cube) + 30) < 210:
        Zf = Z0 + (layer_thickness * layers_cube) + 30 
    elif layers_cube > 1 and (Z0 + (layer_thickness * layers_cube)) < 210:
        Zf = Z0 + (layer_thickness * layers_cube)
    elif layers_cube > 1 and (Z0 + (layer_thickness * layers_cube)) > 210:
        Zf = Z0 + (layer_thickness * layers_cube)
    else:
        Zf = Z0 + 30 # This is the height the head will move up at the end of the print

    def x_move(move_num):
            if move_num == 0:
                x = X0
            else:
                x = X0 + (((move_num+1)//2)%2)*L
            return x

    X1 = x_move(1)

    def y_move(move_num):
            if move_num == 0:
                y = Y0
            else:
                y = Y0 + (move_num//2)*l
            return y

    lines_test_x = []
    lines_test_y = []
    lines_test_z = []
    lines_test_e = []
    lines_test_t = []
    lines_gcode = []
    for layer in range(0, int(layers_cube)):
        for n in range(0, int(moves_layer)):
            if layer == 0 and n == 0 and wipe == True:
                x = Xw
                y = Y0
                z = Z0 + (layer_thickness * layer)
                lines_test_x.append(x)
                lines_test_y.append(y)
                lines_test_z.append(z)
                lines_gcode.append(f'G1 X{x} Y{y} Z{z} \n')
            if layer == 0 and n == 0 and wipe == False:
                x = X0
                y = Y0
                z = Z0 + (layer_thickness * layer)
                lines_test_x.append(x)
                lines_test_y.append(y)
                lines_test_z.append(z)
                lines_gcode.append(f'G1 X{x} Y{y} Z{z} \n')
            elif layer == 0 and n == 1 and wipe == True:
                x = X1
                y = y_move(n)
                z = Z0 + (layer_thickness * layer)
                e = E1 + Lw
                t = e / F1 
                lines_test_x.append(x)
                lines_test_y.append(y)
                lines_test_z.append(z)
                lines_test_e.append(e)
                lines_test_t.append(t)
                lines_gcode.append(f'G1 X{x} Y{y} Z{z} E{e} F{F1} \n')
            elif layer == 0 and n == 1 and wipe == False:
                x = X1
                y = y_move(n)
                z = Z0 + (layer_thickness * layer)
                e = E1
                t = e / F1
                lines_test_x.append(x)
                lines_test_y.append(y)
                lines_test_z.append(z)
                lines_test_e.append(e)
                lines_test_t.append(t)
                lines_gcode.append(f'G1 X{x} Y{y} Z{z} E{e} F{F1} \n')
            elif layer == 0 and n > 1:        
                x = x_move(n) 
                y = y_move(n) 
                z = Z0 
#                 e = abs(x_move(n)-x_move(n-1)+y_move(n)-y_move(n-1))
                e = np.sqrt(((x_move(n) - x_move(n-1))**2) + ((y_move(n) - y_move(n-1))**2))
                t = e / F1
                lines_test_x.append(x)
                lines_test_y.append(y)
                lines_test_z.append(z)
                lines_test_e.append(e)
                lines_test_t.append(t)
                lines_gcode.append(f'G1 X{x} Y{y} Z{z} E{e} \n')
            elif layer > 0:
                theta = np.radians(90 * layer)
                X_rot = X0 + (L / 2)
                Y_rot = (y_move(0)  + y_move(int(moves_layer))) / 2
                x = (np.cos(theta) * (x_move(n) - X_rot)) + (np.sin(theta) * (y_move(n) - Y_rot)) + X_rot
                y = (-np.sin(theta) * (x_move(n) - X_rot)) + (np.cos(theta) * (y_move(n) - Y_rot)) + Y_rot
                z = Z0 + (layer_thickness * layer)
#                 e = abs(x_move(n)-x_move(n-1)+y_move(n)-y_move(n-1))
                e = np.sqrt(((x_move(n) - x_move(n-1))**2) + ((y_move(n) - y_move(n-1))**2))
                t = e / F1
                lines_test_x.append(x)
                lines_test_y.append(y)
                lines_test_z.append(z)
                lines_test_e.append(e)
                lines_test_t.append(t)
                lines_gcode.append(f'G1 X{x} Y{y} Z{z} E{e} \n')
                
    V_f = sum(lines_test_e) * S * np.pi * (D_f/2)**2

    print(f'Length of Filament Fed = {(sum(lines_test_e) * S):.2f}mm ({((sum(lines_test_e) * S)/1000):.2f}m)')
    print(f'Filament Volume = {(V_f):.2f} mm^3')
    if layers_cube > 1:
        print(f'Approximate Effective Volume = {((L**2) * h):.2f}mm^3')
        print(f'Foam to Solid Density Ratio = {((V_f) / ((L**2) * h)):.2f}')
    print(f'Average Volumetric Flow Rate = {(V_f / sum(lines_test_t)):.2f} mm^3/min ({((V_f/1E6) / sum(lines_test_t)):.3} liters/min)')
    print(f'Estimated Printing Time = {(datetime.timedelta(minutes = sum(lines_test_t)))} ({sum(lines_test_t):.2f} minutes)')
    print(f'Estimated Part Weight = {(ρ/1000 * V_f):.2f} g')
    
    # Writing of G-code

    D1 = [f'M73 P0 R0 \n',
          f'M201 X9000 Y9000 Z500 E10000 ; sets maximum accelerations, mm/sec^2 \n',
          f'M203 X500 Y500 Z12 E120 ; sets maximum feedrates, mm/sec \n',
          f'M204 P2000 R1500 T2000 ; sets acceleration (P, T) and retract acceleration (R), mm/sec^2 \n',
          f'M205 X10.00 Y10.00 Z0.20 E4.50 ; sets the jerk limits, mm/sec \n',
          f'M205 S0 T0 ; sets the minimum extruding and travel feed rate, mm/sec \n',
          f'M107 ; turns off fan \n',
          f'M862.3 P "MK2.5S" ; printer model check \n',
          f'M862.1 P{D_n} ; nozzle diameter check \n',
          f'G90 ; use absolute coordinates \n',
          f'M83  ; extruder relative mode \n',

          f'\n'

          f'M104 S{T_n} ; set extruder temp \n',
          f'M140 S{T_b} ; set bed temp \n',
          f'M190 S{T_b} ; wait for bed temp \n',
          f'M109 S{T_n} ; wait for extruder temp \n',

          f'\n',

          f'G28 W ; home all without mesh bed level \n',
          f'G80 ; mesh bed leveling \n',
          f'G1 Y-3.0 F1000.0 ; go outside print area \n',
          f'G92 E0.0 \n',
          f'G1 X60.0 E9.0 F1000.0 ; intro line \n',
          f'G1 X100.0 E12.5 F1000.0 ; intro line \n',
          f'G92 E0.0 \n',
          f'G21 ; set units to millimeters \n',
          f'G90 ; use absolute coordinates \n',
          f'M83 ; use relative distances for extrusion \n',
          f'M900 K0.05 ; Filament gcode LA 1.5 \n',
          f'M900 K30 ; Filament gcode LA 1.0 \n',
          f'G92 E0.0 \n',

          f'M221 S{S * 100} \n',

          f'G1 Z0.200 F10800.000 \n',

          f'M204 S1000 \n',      

          f'\n',
          f'\n']


    lines_α = [f'G1 X{X0} Y{Y0} Z{Zα} \n',
               f'G1 X{Xα} E{Eα} F{F1} \n']

    Dt = [f'\n',
          f'\n',

          f'G1 F10800.000 \n',
          f'G4 ; wait \n',
          f'M104 S0 ; turn off temperature \n',
          f'M140 S0 ; turn off heatbed \n',
          f'M107 ; turn off fan \n',]

    Dt_continuous = [f'\n',
          f'\n',

          f'G1 F10800.000 \n',
          f'G4 ; wait \n',]

    D2 = [f'G1 Z{Zf} ; Move print head up \n',
          f'M73 P91 R0 \n',
          f'G1 X0 Y200 F3000 ; home X axis \n',
          f'M900 K0 ; reset LA \n',
          f'M84 ; disable motors \n',
          f'M73 P100 R0 \n']

    D2α = [f'G1 Z{Zfα} ; Move print head up \n',
          f'M73 P91 R0 \n',
          f'G1 X0 Y200 F3000 ; home X axis \n',
          f'M900 K0 ; reset LA \n',
          f'M84 ; disable motors \n',
          f'M73 P100 R0 \n']

    fail_build_area = False

    if Xw < 0 or 0 < X0 > 250 or 0 < (X0 + L) > 250 or 0 < Y0 > 210 or 0 < (Y0 + L) > 210 or Zf > 210: #These limits are for a build area of 25cm x 21cm
        fail_build_area = True

    def write():
        if continuous_testing == False:
            if write_α_gcode == True:
                with open (f'gcode/{Trial}_αTest.gcode', 'w') as f:
                    f.writelines(D1)
                    f.writelines(lines_α)
                    f.writelines(Dt)
                    f.writelines(D2α)
            with open (f'gcode/{Trial}.gcode', 'w') as f:
                f.writelines(D1)
                f.writelines(lines_gcode)
                f.writelines(Dt)
                f.writelines(D2)
        if continuous_testing == True:
            if write_α_gcode == True:
                with open (f'gcode/{Trial}_αTest.gcode', 'w') as f:
                    f.writelines(D1)
                    f.writelines(lines_α)
                    f.writelines(Dt_continuous)
                    f.writelines(D2α)
            with open (f'gcode/{Trial}.gcode', 'w') as f:
                f.writelines(D1)
                f.writelines(lines_gcode)
                f.writelines(Dt_continuous)
                f.writelines(D2)

    if write_gcode == True and fail_build_area == True:
        print("PART WILL EXCEED BUILD AREA, CANNOT BE PRINTED.")
    elif write_gcode == True and fail_build_area == False:
        write()


    #Line Testing 
    
    if ThreeD_preview == True:
        
#         %matplotlib inline 

        fig = plt.figure(figsize=plt.figaspect(1))
        fig.set_size_inches(24, 11)

        ax =  fig.add_subplot(1, 2, 1, projection='3d')
        ax.plot3D(lines_test_x, lines_test_y, lines_test_z,
               color = "indigo")    
        ax.set_xlim(0.0, 250.0)
        ax.set_ylim(0.0, 210.0)
        ax.set_zlim(0.0, 210.0)
        
        ax.view_init(azim = view_az, elev = view_elev)

        ax =  fig.add_subplot(1, 2, 2, projection='3d')
        ax.plot3D(lines_test_x, lines_test_y, lines_test_z,
               color = "indigo")    

        ax.view_init(azim = view_az, elev = view_elev) #azim = odd multiples of 45 work well to examine different sides, elev = 20 Default

        plt.show()

    if TwoD_preview == True:

        fig, ax = plt.subplots(1,2)
        fig.set_size_inches(20, 20)
        fig.tight_layout(w_pad=3.5, h_pad=3.5)

        ax[0].grid(b=None, which='major', axis='both')
        ax[1].grid(b=None, which='major', axis='both')

        ax[0].set_xlim(0.0, 250.0)
        ax[0].set_ylim(0.0, 210.0)

        ax[0].set_aspect(1/1)
        ax[1].set_aspect(1/1)

        ax[0].set_facecolor('whitesmoke')
        ax[1].set_facecolor('whitesmoke')

        ax[0].set_xlabel('X')
        ax[0].set_ylabel('Y')
        ax[0].set_title('Build Plate Preview')

        ax[1].set_xlabel('X')
        ax[1].set_ylabel('Y')
        ax[1].set_title('Part Preview')

        ax[0].plot(lines_test_x, lines_test_y, 
               color = "indigo")

        plt.sca(ax[0])
        plt.xticks(np.arange(0, 251, 50))
        plt.yticks(np.arange(5, 211, 50))

        plt.sca(ax[1])
        plt.xticks(np.arange(0, 251, 50))
        plt.yticks(np.arange(5, 211, 50))

        ax[1].plot(lines_test_x, lines_test_y, 
               color = "indigo")
        
        plt.show()


    #gcode preview

    if preview_gcode == True and fail_build_area == False:
        trial_gcode = open(f"{Trial}.gcode", "r") #opens the written gcode file
        print(trial_gcode.read())
        
        
        
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual

def txt(value, placeholder, description):
    return widgets.Text(value=value, placeholder=placeholder, description=description)
    
def FS(value, min, max, step, description):
    return widgets.FloatSlider(value=value, min=min, max=max, step=step, description=description, continuous_update=False, style={'description_width': 'initial'})

def ChB(value, description):
    return widgets.Checkbox(value=value, description=description, indent=False)

def run_int_cube():
    Trial=txt("", "Trial Name", "Trial:")
    V_star=FS(0.5, 0.001, 5.01, 0.01, "V*:")
    H_star=FS(2, 1, 10, 0.1, "H*:")
    L=FS(30, 0, 210, 1, "Long Move Length (mm):")
    l=FS(1.2, 0, 20, 0.01, "Short Move Length (mm):")
    h=FS(30, 0, 210, 1, "Cube Height (mm):")
    layer_thickness=FS(0.8, 0, 5, 0.01, "Layer Thickness (mm):")
    vertical_transition=ChB(True, "Vertical Transition?")
    wipe=ChB(True, "Wipe?")
    centered=ChB(True, "Centered?")
    TwoD_preview=ChB(True, "2D Preview?")
    ThreeD_preview=ChB(True, "3D Preview?")
    preview_gcode=ChB(False, "Preview gcode?")
    write_gcode=ChB(True, "Write gcode?")
    write_α_gcode=ChB(False, "Write Die-Swell Test?")
    continuous_testing=ChB(False, "Continuous Testing?")
    T_n=FS(215, 0, 280, 1, "Nozzle Temperature (°C):")
    T_b=FS(60, 0, 110, 1, "Bed Temperature (°C):")
    α=FS(1.63, 1, 2, 0.01, "Assumed Die-Swell:")
    F1=FS(300, 1, 600, 1, "Feed Rate (mm/min):")
    Lw=FS(10, 1, 50, 1, "Wipe Length (mm):")
    Lα=FS(150, 50, 210, 1, "Die-Swell Test Length (mm):")
    Zα=FS(150, 20, 210, 1, "Die-Swell Test Height (mm):")
    D_f=widgets.Dropdown(options=[1.75, 2.85], value=1.75, description='Filament Diameter (mm):', style={'description_width': 'initial'})
    D_n=widgets.Dropdown(options=[0.25, 0.4, 0.5, 0.8], value=0.4, description='Nozzle Diameter (mm):', style={'description_width': 'initial'})
    ρ=FS(1.22, 0, 5, 0.01, "Filament Density (g/cm^3):")
    X0=FS(50, 0, 250, 1, "Default Initial X Coordinate:")
    Y0=FS(100, 0, 210, 1, "Default Initial Y Coordinate:")
    view_az=FS(225, -360, 360, 15, "Preview Azimuth:") 
    view_elev=FS(30, -360, 360, 15, "Preview Elevation:") 


    #Create your button.
    button = widgets.Button(description="Generate!", layout=widgets.Layout(width='90%', height='50px'))
    #Output field.
    output = widgets.Output()

    #function to handle input.
    def showOutput(btn):
        output.clear_output()
    #     return_value = slider.value
        with output:
            zig_zag_gcode( 
                 Trial=Trial.value, 
                 V_star=V_star.value,
                 H_star=H_star.value,
                 L=L.value,
                 l=l.value,
                 h=h.value,
                 layer_thickness=layer_thickness.value,
                 vertical_transition=vertical_transition.value,
                 wipe=wipe.value,
                 centered=centered.value,
                 TwoD_preview=TwoD_preview.value,
                 ThreeD_preview=ThreeD_preview.value,
                 preview_gcode=preview_gcode.value,
                 write_gcode=write_gcode.value,
                 write_α_gcode=write_α_gcode.value,
                 continuous_testing=continuous_testing.value,
                 T_n=T_n.value,
                 T_b=T_b.value,
                 α=α.value,
                 F1=F1.value,
                 Lw=Lw.value,
                 Lα=Lα.value,
                 Zα=Zα.value,
                 D_f=D_f.value,
                 D_n=D_n.value,
                 ρ=ρ.value,
                 X0=X0.value,
                 Y0=Y0.value,
                 view_az=view_az.value, 
                 view_elev=view_elev.value)


    button.on_click(showOutput)
    
    box1 = widgets.VBox([Trial, V_star, H_star, L, l, h, layer_thickness,F1 , button])
    box2 = widgets.VBox([vertical_transition, wipe, centered, TwoD_preview, ThreeD_preview, preview_gcode, write_gcode, write_α_gcode, continuous_testing])
    box3 = widgets.VBox([T_n, T_b, α, ρ, D_f, D_n])
    box4 = widgets.VBox([Lw, Lα, Zα, X0, Y0, view_az, view_elev])

    top = widgets.HBox([box1, box2 ,box3, box4], layout = widgets.Layout(display='flex', flex_flow='row', justify_content='space-between', align_items='stretch', width='90%'))
    bottom = widgets.HBox([output])
    
    ui = widgets.VBox([top, bottom])
    return ui        