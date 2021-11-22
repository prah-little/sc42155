import pygame
import math
import numpy as np

# Parameters tanks
# Tank radius and cross section
rT          = 1                     #[m],   radius reservoir and tanks
A           = [np.pi*rT**2, np.pi*rT**2, np.pi*rT**2]  #[m^2], cross section area tanks

# Pipe radius and cross section
rp          = 0.05                  #[m],   pipe radius
At          = np.pi*rp**2           #[m^2], pipe cross section area

# Flow resistence coefficient vector Rw1, Rw2, Rw3, RwOut1, RwOut2
R           = [10,10,10,20,20] #[-], flow resistance

# Flow rate input
wIn_amp     = 1                     # [m^3/s], flow input

# Fluid density and gravitational constant
rho, g      = 1, 9.81               # [kg/m^3], [m/s^2], density and grav constand

# Valve 3 height at 2/3 height of the tank
hR, h       = 3, 3                  #[m], reservoir height, tanks height
h1          = 1.5               #[m], valve height
ls          = [1.5,2.5,2.8,2.8]             #[m], Sensor 1, 2, 3, 4 height respectively

# Parameters transducer, elec-circt, mech
rimp, r     = rp, [0.1,0.2]         #[m], [m], radius of impeller, radius gear 1, 2 
Km, Re, Ce  = 0.001, 0.1, 1         #[],[ohm],[] motor constant, resistor, capacitor
b, J        = 0.000001, 0.001              #[],[],damping constant, inertia
M           = r[1]*At*rimp/r[0]     #placeholder for readability

##### pygame #####

pygame.init()

WIDTH = 600             # Window width
HEIGHT = 600            # Window height
WIN = pygame.display.set_mode((WIDTH, HEIGHT))      # Surface

T_W = 100   # Tank Width
T_H = 100   # Tank Height

# Some colors
water = (0,191,255)
white = (255,255,255)
green = (0,255,0)
dgreen = (0,200,0)
red = (255,0,0)
yellow = (255,255,0)

# Maps meters to pixels
px = int(T_H/h)

# Simulation Parameters
N = 10000                           # Steps
t0 = 0                              # first t
tend = 60*5                         # end t
TIME = np.linspace(t0,tend,N)       # time vector

STATE = np.zeros((6,2))     # State vector
IN = 1
INPUT = wIn_amp                     # Input vector
VALVES = [1,1,1]

FONT = pygame.font.Font("freesansbold.ttf", 15)

def valve(l1,l2,va):
    v = [0,0,0]

    eps = 0.2

    if  va[0] == 1 and l1 <= ls[1] + eps :
        v[0] = 1
    elif l1 >= ls[1] + eps :
        v[0] = 0
    elif va[0]==0 and l1 >= ls[1] - eps :
        v[0] = 0
    elif l1 <= ls[1] - eps :
        v[0] = 1

    if  va[1] == 1 and l2 <= ls[3] + eps :
        v[1] = 1
    elif l2 >= ls[3] + eps :
        v[1] = 0
    elif va[1]==0 and l2 >= ls[3] - eps :
        v[1] = 0
    elif l2 <= ls[3] - eps :
        v[1] = 1
        
    if l1 < ls[0]:
        v[2] = 1
    elif l1 >= ls[0] and l1 < ls[1]:
        v[2] = 0
    elif l1 >= ls[1] and l1 < ls[2]:
        v[2] = 1
    elif l1 >= ls[2]:
        v[2] = 0
        
    return v

def omega3(l1,l2):
    if l1 <= h1 and l2 <= h1:
        w3 = 0
    elif l1 > h1 and l2 <= h1:
        w3 = -rho*g*(l1-h1)/R[2]
    elif l1 <= h1 and l2 > h1:
        w3 = rho*g*(l2-h1)/R[2]
    elif l1 > h1 and l2 > h1:
        w3 = rho*g*(l2-l1)/R[2]
    return w3

def stateSpace(X,U,t,eps=1e-10):
    dt = t[1]-t[0]
    i = 1
    X[0,i] = max(0,X[0,i-1] + dt*(
        U/(np.pi*(rT+X[0,i-1])**2) 
        - np.sqrt(X[0,i-1])*np.sqrt(rho*g)*(valve(X[1,i-1],X[2,i-1],VALVES)[0]/R[0] + valve(X[1,i-1],X[2,i-1],VALVES)[1]/R[1])/(np.pi*(rT+X[0,i-1])**2) 
        ))
    X[1,i] = max(0,X[1,i-1] + dt*(
        np.sqrt(X[0,i-1])*np.sqrt(rho*g)*valve(X[1,i-1],X[2,i-1],VALVES)[0]/(A[0]*R[0]) 
        - np.sqrt(X[1,i-1])*np.sqrt(rho*g)/(A[0]*R[3]) 
        + omega3(X[1,i-1],X[2,i-1])*valve(X[1,i-1],X[2,i-1],VALVES)[2]/(A[0]*rho*g)
        ))            
    X[2,i] = max(0,X[2,i-1] + dt*(
        np.sqrt(X[0,i-1])*np.sqrt(rho*g)*valve(X[1,i-1],X[2,i-1],VALVES)[1]/(A[0]*R[1]) 
        - np.sqrt(X[2,i-1])*np.sqrt(rho*g)/(A[1]*R[4]) 
        + X[4,i-1]/A[1] 
        - omega3(X[1,i-1],X[2,i-1])*valve(X[1,i-1],X[2,i-1],VALVES)[2]/(A[1]*rho*g)
        ))
    X[3,i] = max(0,X[3,i-1] + dt*(
        -X[4,i-1]/A[2]
        ))
    X[4,i] = X[4,i-1] + dt*(-((Km**2/Re) + b)*X[4,i-1]/J + (rho*g*(X[3,i-1] - X[2,i-1])*M**2)/J - (Km*X[5,i-1]*M)/(J*Re))
    X[5,i] = X[5,i-1] + dt*(-(Km*X[4,i-1]/M + X[5,i-1])/(Re*Ce))
    return X

done = False

while done is False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        # This block is executed once for each MOUSEBUTTONDOWN event.
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 1 is the left mouse button, 2 is middle, 3 is right.
            if event.button == 1:
                # `event.pos` is the mouse position.
                if button.collidepoint(event.pos):
                    # Increment the number.
                    IN = 1 - IN
                else :
                    done = True

    # SET SCREEN BLACK
    WIN.fill((0, 0, 0))

    # RUN SIMULATION
    STATE = stateSpace(STATE,INPUT*IN,TIME)
    
    # UPDATE STATE
    STATE[:,0] = STATE[:,1]
    VALVES = valve(STATE[1,1], STATE[2,1],VALVES)

    # SHUT OFF INPUT IF RESERVOIR IS FULL
    if STATE[0,1] >= hR - 0.1:
        IN = 0

    # Reservoir
    pygame.draw.polygon(WIN,water, [(350,200),(450,200),(450+STATE[0,1]*px,200-STATE[0,1]*px),(350-STATE[0,1]*px,200-STATE[0,1]*px)])
    pygame.draw.polygon(WIN,white, [(350,200),(450,200),(450+T_H,200-T_H),(350-T_H,200-T_H)],2)

    # Tank 1
    pygame.draw.rect(WIN,water, pygame.Rect(450,400-STATE[1,1]*px,T_W,STATE[1,1]*px))
    pygame.draw.rect(WIN,white, pygame.Rect(450,300,T_W,T_H),2)

    # Tank 2
    pygame.draw.rect(WIN,water, pygame.Rect(250,400-STATE[2,1]*px,T_W,STATE[2,1]*px))
    pygame.draw.rect(WIN,white, pygame.Rect(250,300,T_W,T_H),2)

    # Tank 3
    pygame.draw.rect(WIN,water, pygame.Rect(50,400-STATE[3,1]*px,T_W,STATE[3,1]*px))
    pygame.draw.rect(WIN,white, pygame.Rect(50,250,T_W,T_H+50),2)

    #### Input
    pygame.draw.line(WIN, white, (200,50), (300,50), 2)
    pygame.draw.line(WIN, white, (200,60), (300,60), 2)
    
    if INPUT*IN > 0:
        # Flow indicator
        pygame.draw.polygon(WIN, green, [(250,38), (254,42),(250,46)])
        pygame.draw.rect(WIN,water, pygame.Rect(150,52,155,8))
        pygame.draw.arc(WIN, water, pygame.Rect(275,52,50,80), 0, 0.5*np.pi,8)
    else:
        pygame.draw.line(WIN, red, (254,48-12), (246,48-4), 2)
        pygame.draw.line(WIN, red, (246,48-12), (254,48-4), 2)

    #### Valve 1 (in)
    pygame.draw.polygon(WIN, white, [(420,200),(420,240),(505,240),(505,300),(495,300),(495,250),(410,250),(410,200)], 2)
    # Flow indicator
    if VALVES[0] == 1:
        pygame.draw.polygon(WIN, green, [(450,240-12),(454,240-8),(450,240-4)])
    elif VALVES[0] == 0:
        pygame.draw.line(WIN, red, (454,240-12), (446,240-4), 2)
        pygame.draw.line(WIN, red, (446,240-12), (454,240-4), 2)

    ##### Valve 2 (in)
    pygame.draw.polygon(WIN, white, [(380,200),(380,240),(295,240),(295,300),(305,300),(305,250),(390,250),(390,200)], 2)
     # Flow indicator
    if VALVES[1] == 1:
        pygame.draw.polygon(WIN, green, [(350,240-12),(346,240-8),(350,240-4)])
    elif VALVES[1] == 0:
        pygame.draw.line(WIN, red, (354,240-12), (346,240-4), 2)
        pygame.draw.line(WIN, red, (346,240-12), (354,240-4), 2)

    ##### Valve 3 (between)
    pygame.draw.line(WIN, white, (450,400-10-h1*px), (350,400-10-h1*px), 2)
    pygame.draw.line(WIN, white, (450,400-h1*px), (350,400-h1*px), 2)
    # Flow indicator
    if VALVES[2] == 1:
        if omega3(STATE[1,1],STATE[2,1]) < 0:
            pygame.draw.polygon(WIN, green, [(404,400-10-h1*px-12),(400,400-10-h1*px-8),(404,400-10-h1*px-4)])
        elif omega3(STATE[1,1],STATE[2,1]) > 0:
            pygame.draw.polygon(WIN, green, [(404,400-10-h1*px-12),(408,400-10-h1*px-8),(404,400-10-h1*px-4)])
        else:
            pygame.draw.polygon(WIN, green, [(404,400-10-h1*px-12),(400,400-10-h1*px-8),(404,400-10-h1*px-4)])
            pygame.draw.polygon(WIN, green, [(404,400-10-h1*px-12),(408,400-10-h1*px-8),(404,400-10-h1*px-4)])          
    else :
        pygame.draw.line(WIN, red, (404,400-10-h1*px-12), (396,400-10-h1*px-4), 2)
        pygame.draw.line(WIN, red, (396,400-10-h1*px-12), (404,400-10-h1*px-4), 2)

    ##### Turbine (3 - 2)
    pygame.draw.line(WIN, white, (250,390), (150,390), 2)
    pygame.draw.line(WIN, white, (250,400), (150,400), 2)
     # Flow indicator
    if  STATE[4,1] > 0:
        pygame.draw.polygon(WIN, green, [(200,390-12),(204,390-8),(200,390-4)])
    elif STATE[4,1] < 0:
        pygame.draw.polygon(WIN, green, [(200,390-12),(196,390-8),(200,390-4)])
    else :
        pygame.draw.line(WIN, red, (204,390-12), (196,390-4), 2)
        pygame.draw.line(WIN, red, (196,390-12), (204,390-4), 2)

    #### Out 1
    pygame.draw.line(WIN, white, (505,400), (505,420), 2)
    pygame.draw.line(WIN, white, (495,400), (495,420), 2)
    if STATE[1,1] > 0:
        pygame.draw.rect(WIN,water, pygame.Rect(497,400,8,40))

    #### Out 2
    pygame.draw.line(WIN, white, (305,400), (305,420), 2)
    pygame.draw.line(WIN, white, (295,400), (295,420), 2)
    if STATE[2,1] > 0:
        pygame.draw.rect(WIN,water, pygame.Rect(297,400,8,40))

    #### Draw sensors
    if STATE[1,1] >= ls[0]:
        pygame.draw.circle(WIN, yellow, (550,400-int(ls[0]*px)), 4)
    else :
        pygame.draw.circle(WIN, red, (550,400-int(ls[0]*px)), 4)
    if STATE[1,1] >= ls[1]:
        pygame.draw.circle(WIN, yellow, (550,400-int(ls[1]*px)), 4)
    else :
        pygame.draw.circle(WIN, red, (550,400-int(ls[1]*px)), 4)
    if STATE[1,1] >= ls[2]:
        pygame.draw.circle(WIN, yellow, (550,400-int(ls[2]*px)), 4)
    else :
        pygame.draw.circle(WIN, red, (550,400-int(ls[2]*px)), 4)
    if STATE[2,1] >= ls[3]:
        pygame.draw.circle(WIN, yellow, (350,400-int(ls[3]*px)), 4)
    else :
        pygame.draw.circle(WIN, red, (350,400-int(ls[3]*px)), 4)

    if IN == 0:
        button = pygame.draw.rect(WIN,red,pygame.Rect(150,30,50,50))
        pygame.draw.circle(WIN, (0,0,0), (175,55), 15,4)
        pygame.draw.rect(WIN,red, pygame.Rect(170,30,10,20))
        pygame.draw.line(WIN, (0,0,0), (174,40), (174,50), 4)
    else:
        button = pygame.draw.rect(WIN,green,pygame.Rect(150,30,50,50))
        pygame.draw.circle(WIN, (0,0,0), (175,55), 15,4)
        pygame.draw.rect(WIN,green, pygame.Rect(170,30,10,20))
        pygame.draw.line(WIN, (0,0,0), (174,40), (174,50), 4)

    if STATE[4,1] == 0:
        LED = (255,255,0)
    else:
        LED = (255,255,0,np.abs(STATE[4,1])*1000)
    pygame.draw.circle(WIN, LED, (200,500), 20)
    
    FRAMERATE = 1000
    pygame.display.update()
    pygame.time.Clock().tick(FRAMERATE)

pygame.quit()
