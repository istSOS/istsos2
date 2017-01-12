# -*- coding: utf-8 -*-

import math
from dateutil import parser


'''
    =======================================================================
    Potential evaporation functions using Penman-Montheit with hourly data
    =======================================================================
'''

def ET0(isodate,T,RH,u2,Rs,lat,lon,z,P=None):
    
    """
    Input:
        isodate: iso datetime (in UTC?)
        T: hourly air temperature at 2m [Celsius]
        RH: hourly relative air humidity [Pa]
        u2: hourly wind speed at 2 m [m/s]
        Rs: hourly incoming solar radiation [J/m2/hour]
        lat: latitude of the mesurement point [decimal degree]
        lon: longitude of the mesurement point [decimal degree]
        z: altitude above sea level of the measurement point [m]
        P: hourly air pressure [Pa] (Opzional) 
    
    Output:
        - ET0: hourly refrence evapotranspiration []
    
    Examples::
        >>> import FAO56
        >>> FAO56.ET0(isodate="2012-10-01T02:00Z",T=28,RH=90,u2=1.9,Rs=0,lat=16.21,lon=-16.26,z=8)
        >>> 
        >>> FAO56.ET0(isodate="2012-10-01T14:00Z",T=38,RH=52,u2=3.3,Rs=2.450,lat=16.21,lon=-16.26,z=8)
        >>> 0.626874880652
    
    Refernces:
        http://www.fao.org/docrep/X0490E/x0490e00.htm#Contents
    
    """
    # get datetime object
    dt = parser.parse(isodate)
    print "dt: %s" % dt
    
    #air pressure (calculation)
    if not P:
        P = 101.3 * ((293-0.0065*z)/293)**5.26
    
    # saturation vapour pressure (eq.11) [kPa]
    e0T = 0.6108 * math.exp( (17.27*T)/(T+237.3) )
    print "e0T: %s" % e0T
    
    # Slope of saturation vapour pressure curve (eq.13) [kPa / °C]
    D = 4098 * (e0T) / pow ((T + 237.3), 2)
    print "D: %s" % D
    
    # Psychrometric constant (eq.8) [kPa / °C]
    g = 0.6665 * (10**-3) * P
    print "g: %s" % g
    
    # Actual vapour pressure (eq.54) [kPa]
    ea = e0T * RH / 100
    print "ea: %s" % ea
    
    # Pressure deficit [kPa]
    ed = e0T - ea
    print "ed: %s" % ed
    
    # Extraterrestrial radiation
    #============================
    
    # solar costant [ MJ / m2 * min ]
    Gsc = 0.0820 
    print "Gsc: %s" % Gsc
    
    # Convert latitude [degrees] to radians
    j = lat * math.pi / 180.0
    print "j: %s" % j
    
    # day of the year [-]
    tt = dt.timetuple()
    J = tt.tm_yday-1
    print "J: %s" % J

    # inverse relative distance Earth-Sun (eq.23) [-]
    dr = 1.0 + 0.033 * math.cos(J* ((2*math.pi)/365) )
    print "dr: %s" % dr
    
    # solar declination (eq.24) [rad]
    d = 0.409 * math.sin( (2*math.pi/365)*J - 1.39)
    print "d: %s" % d
    
    # solar correction (eq.33) [-]
    b = 2 * math.pi * (J-81) / 364
    print "b: %s" % b
    
    # Seasonal correction for solar time
    Sc = (0.1645 * math.sin(2*b)) - (0.1255 * math.cos(b)) - (0.025 * math.sin(b))
    print "Sc: %s" % Sc
    
    # longitude of the centre of the local time zone
    Lz = round(lon/15) * 15
    print "Lz: %s" % Lz
    
    # Solartime angle
    t = dt.hour + 0.5
    print "t: %s" % t
    
    # standard clock time at the midpoint of the perion [hour]
    w = (math.pi/12) * ( (t + 0.06667*(math.fabs(Lz)-math.fabs(lon)) + Sc) - 12 )
    print "w: %s" % w
    
    # time interval [hour]
    ti = 1
    
    # solar time angle at begin of the period
    w1 = w  - (math.pi*ti)/24
    print "w1: %s" % w1
    
    # solar time angle at end of the period
    w2 = w  + (math.pi*ti)/24
    print "w2: %s" % w2
    
    # Sanset hour angle 
    ws = math.acos(-math.tan (j) * math.tan(d))
    print "ws: %s" % ws
    
    # Extraterrestrial radiation (eq.28) [MJ m-2 * hour-1 ]    
    if w<-ws or w>ws:
        Ra = 0
    else:
        Ra = (12*60/math.pi) * Gsc * dr * ( (w2-w1)*math.sin(j)*math.sin(d) + math.cos(j)*math.cos(d)*(math.sin(w2)-math.sin(w1)) )
    print "Ra: %s" % Ra
    
    # Net solar radiation
    #============================
    
    # Solar radiation [ MJ * m-2 * hour-1 ]
    if w<-ws or w>ws:
        # solar radiation
        Rs = 0
        print "Rs: %s" % Rs
        
        # clear sky solar radiation [ MJ * m-2 * hour-1 ]
        Rso = 0
        print "Rso: %s" % Rso
        
        # net solar radiation [ MJ * m-2 * hour-1 ]
        Rns = 0
        print "Rns: %s" % Rns
    else:
        # solar radiation
        Rs = 2.450
        print "Rs: %s" % Rs
        
        # clear sky solar radiation [ MJ * m-2 * hour-1 ]
        Rso = ( 0.75 + 2 * (10**-5) * z ) * Ra
        print "Rso: %s" % Rso

        # for reference hypotetical grass reference crop [-]
        albedo = 0.23        
        
        # net solar radiation [ MJ * m-2 * hour-1 ]
        Rns = (1- albedo) * Rs
        print "Rns: %s" % Rns
    
    # Net longwave Radiation
    #============================
    
    # Steffan-Boltzman constant [ MJ * K-4 * m-2 * hour-1 ]
    sbc = 2.04 * (10**-10)
    
    # cloudiness factor
    if Rso is 0:
        f = 1.35 * 0.8 - 0.35
    else:
        f = 1.35 * (Rs/Rso) - 0.35
    print "f: %s" % f
    
    # net emissivity of the surface
    if ea < 0:
	nes = 0.34
    else:
	nes = 0.34 - 0.14 * math.sqrt(ea)
    print "nes: %s" % nes
    
    # Net longwave Radiation
    Rnl = nes * f * (sbc * (T + 273)**4)
    print "Rnl: %s" % Rnl
    
    # Net Radiation
    #============================
    Rn = Rns - Rnl
    print "Rn: %s" % Rn
    
    # Soil heat flux
    #============================
    if Rn > 0:
        Ghr = 0.1 * Rn
    else:
        Ghr = 0.5 * Rn
    print "Ghr: %s" % Ghr
    
    # Refernce evapotranspiration
    #============================
    
    # alpha
    alpha = 0.408 * D * ( Rn - Ghr)
    print "alpha: %s" % alpha
    
    # beta
    beta =  g * ( 37 / (T+273.3) ) * u2 * (e0T-ea)
    print "beta: %s" % beta
    
    # gamma
    gamma = D + g * (1 + 0.34*u2)
    print "gamma: %s" % gamma
    
    # Regerence evapotranspiration
    ET0 = ( alpha + beta ) / gamma
    print "ET0: %s" % ET0
    
    return ET0
    
    
def Kc(plantation,Li,Ld,Lm,Le,Kci,Kcm,Kce,isodate=None):
    """
    Input:
        plantation: plantation datetime
        Li: Length in days of the initial stage
        Ld: Length in days of the developement stage
        Lm: Length in days of the mid-season
        Le: Length in days of the late season
        Kci: initial crop coefficient
        Kcm: mid-season crop coefficient
        Kce: late season crop coefficient
        isodate: current datetime (optional)
    
    Output:
        - cKc: current crop factor
    Examples::
        >>> import FAO56
        >>> FAO56.Kc(plantation="2014-01-01",Li=25,Ld=25,Lm=30,Le=20,Kci=0.15,Kcm=1.19,Kce=0.35,isodate="2014-01-20")
        >>> 0.15
        >>> FAO56.Kc(plantation="2014-01-01",Li=25,Ld=25,Lm=30,Le=20,Kci=0.15,Kcm=1.19,Kce=0.35,isodate="2014-02-10")
        >>> 0.774
        >>> FAO56.Kc(plantation="2014-01-01",Li=25,Ld=25,Lm=30,Le=20,Kci=0.15,Kcm=1.19,Kce=0.35,isodate="2014-03-12")
        >>> 1.19
        >>> FAO56.Kc(plantation="2014-01-01",Li=25,Ld=25,Lm=30,Le=20,Kci=0.15,Kcm=1.19,Kce=0.35,isodate="2014-04-06")
        >>> 0.559
    
    Refernces:
        http://www.fao.org/docrep/X0490E/x0490e00.htm#Contents
    
    
    """
    # get datetime object
    if isodate:
        dt = parser.parse(isodate)
    else:
        from datetime import datetime
        dt = datetime.now()
    pdt = parser.parse(plantation)
    
    # days from plantation 
    tt = dt.timetuple()
    Jc =  float(tt.tm_yday-1)
    ptt = pdt.timetuple()
    Jp = float(ptt.tm_yday-1)
    J = Jc-Jp
    
    # calculate the day of the year when each crop stage ends
    JLi = Jp+Li
    JLd = JLi + Ld
    JLm = JLd + Lm
    JLe = JLm + Le
    
    print "JLi: %s, JLd: %s,  JLm: %s,  JLe: %s" % (JLi,JLd,JLm,JLe)
    print "cJ: %s, pJ: %s" % (Jc,Jp)
    print "J: %s" % J
    
    if Jc > Jp and Jc < JLe:
        if J <= JLi:
            cKc = Kci
        elif Jc > JLi and Jc <= JLd:
            #cKc = Kci + ( (J-Li)/Ld * (Kcm-Kci) )
            cKc = Kci + ( (Jc-JLi)/Ld * (Kcm-Kci) )
        elif Jc > JLd and Jc <= JLm:
            cKc = Kcm
        elif Jc > JLm and Jc <= JLe:
            #cKc = Kcm + ( (J-(Li+Ld+Lm))/Le * (Kce-Kcm) ) 
            cKc = Kcm + ( (Jc-JLm)/Le * (Kce-Kcm) ) 
    else:
        cKc = 0
    
    return cKc
    
    
    
    
    
    
    
    
    
    
