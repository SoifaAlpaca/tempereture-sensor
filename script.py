from sympy import * 
import matplotlib as mp
from sympy.plotting import plot

k = 1000

def NtcResToVoltage():
    vcc, rwb, R,V1 ,V2, V3,NTC = symbols( "V_{cc}, R_{wb}, R,V_1,V_2,V_3, R_{NTC}" )
    
    vcc    = 3.3 
    NTCmin = 0.5*k
    NTCmax = 20*k

    #V1 - divisor de tensao NTC em cima
    #R = 10000
    V1 = R/(R+NTC)
    V1 = V1 * vcc    
    #V2 - divisor de tensao NTC em baixo

    V2 = NTC/(NTC+R)
    V2 = V2 * vcc

    p = plot(V2.subs(R,10*k) ,(NTC,NTCmin,NTCmax))
    p = plot(V2.subs(R,100*k),(NTC,NTCmin,NTCmax))

    print( V2.evalf(subs={R:10*k,NTC:NTCmax}) - V2.evalf(subs={R:10*k,NTC:NTCmin}) )
    print( V2.evalf(subs={R:100*k,NTC:NTCmax}) - V2.evalf(subs={R:100*k,NTC:NTCmin}) )

#How the voltage divider output value changes with temperature
# for different resistor values
def NtcTempToVoltage():
    #Here although less accurate its used the Beta model
    #Because it gives the resistance at a certain temperature 
    R, R0, T0, b,Rntc,T, Vout  = symbols("R, R_0, T_0, beta,R_{NTC}, T, V_{out}")
    
    vcc  = 3.3 
    Tmin = 10 + 273.15  #Minimum temperature in Kelvin
    Tmax = 40 + 273.15  #Maximum temperature in Kelvin
    R0   = 10*k         #Resistance at 25°C
    T0   = 298.15       #25°c -> °K
    b    = 3965         #beta value (Datasheet)
    Rntc = R0*( exp( b*( (1/T) - (1/T0) ) ) ) #Beta model equation
    Vout = Rntc/(Rntc+R)
    Vout = Vout * vcc

    p = plot(Vout.subs(R,8*k) ,(T,Tmin,Tmax), xlabel='Temperature (°K)', ylabel='$V_{out}$', title='Output Voltage vs Temperature (8k$\\Omega$)',show=False,axis_center=(282,1.3))
    p.show()
    p = plot(Vout.subs(R,100*k),(T,Tmin,Tmax), xlabel='Temperature (°K)', ylabel='$V_{out}$', title='Output Voltage vs Temperature (100k$\\Omega$)',show=False,axis_center=(282,0.15))
    p.show()

    VTmax = Vout.evalf(subs={R:8*k,T:Tmax})
    VTmin = Vout.evalf(subs={R:8*k,T:Tmin})
    Slope = (VTmax - VTmin)/(Tmax - Tmin)
    inter = VTmax - Slope*Tmax

    print( "V(T = 40°C): "+str( VTmax ) + " V\nV(T = 10°C): " +str( VTmin )+" V" )
    print( "Slope : "+str( Slope ) )
    print( "Interception: "+str( inter ) )
    #print( Vout.evalf(subs={R:100*k,T:Tmax}) - Vout.evalf(subs={R:100*k,T:Tmin}) )

#Calculates the AFE function and solves 
#for the offset for the offset and gain goal

def AfeNtc():

    vo, vp, vcc , r3, r1,r2,it,rf,ntc = symbols("V_{out}, V_p, V_{cc}, R_3, R_1,R_2, i_t, R_f,ntc")
    
    #rf          = 10*k
    vcc         = 3.3
    OffsetGoal  = - 3.53    #Desired Offset
    GainGoal    = 2.92      #Desired Gain
    A           = 0.001303923920
    B           = 0.0002143913551
    C           = 0.00000009659997359
    tolerance   = 1/100 #Resistors tolerance 
    sr          = tolerance/(sqrt(3))
    st          = (5/100)/sqrt(3) #NTC's resistance standard deviation 
    
    it = -(vp/r2) + ( vcc - vp )/r1
    vo = vp - it*rf
    #Here the circuit's function is found
    print("Circuit Function: ")
    print(latex(factor(vo,vp)))
    print()
    #r1= 10*k
    
    #Error propagation
        
    vo = vo.subs(vp, vcc*( ntc/(ntc+r3) ) )
    
    s = sqrt(

        (diff( vo,ntc)**2)*((st)**2)  + 
        (diff( vo,r1 )**2)*((sr)**2)  + 
        (diff( vo,r2 )**2)*((sr)**2)  + 
        (diff( vo,r3 )**2)*((sr)**2)  + 
        (diff( vo,rf )**2)*((sr)**2) 
    )

    err = diff( 1/( A + B*ln( ntc ) + C*(ln(ntc)**3) ),ntc )*s

    err = err*2.58 #2.58 for 99% confidence 
    err = err.evalf(subs={r1:8.2*k,r2:12*k,r3:8.2*k,rf:10*k})
    err = err + 3.3/(4096*2) # adding ADC's error
    print(latex(err.simplify()))

    #Because this values were weird, they were discarded
    
    p = plot(err ,(ntc,5*k,20*k), xlabel='NTC\'s Resistance ($\\Omega$)', ylabel='$Temperature (°C)$', title='Temperature Error',show=False,axis_center=(5000,0.00040265))
    p.show()
    
    #After having the circuit function we analyse the equation
    # and find the part that's responsible for the offset and gain
    # and solve the equation system that gives us the desired offset and gain 
    
    of   = rf/r1     #Offset
    of   = - (of * vcc)
    gain = 1 + rf*( (r2+r1)/(r2*r1) )

    #gain = gain.subs(rf,10*k).evalf()
    #of   = of.subs(rf,10*k).evalf()

    print("R1,R2")
    s = solve( [ gain - GainGoal,of - OffsetGoal ],r1,r2 )
    print(s)


#----------------LM35----------------#
#Com o circuito novo ]e sem offset

def lm35():

    vin, T, vout, s, ra, rb,ro,rf,r1,r2,vcc = symbols("V_{in},T,V_{out},sigma,R_a,R_b,R_o,R_f,R_1,R_2,V_{cc}")
    emax = symbols("epsilon_{max}")

    sr, st = symbols("sigma_r, sigma_s")
    tolerance = 1/100 #Resistors tolerance 
    
    #Standard deviation for the resistors and LM35 output
    sr = tolerance/(sqrt(3))
    st = (1/100)/sqrt(3) 
    
    vin = T*0.01 

    #Sem offset
    vout = vin * (1 + (rf/ro))

    s = sqrt(

        (diff( vout,T  )**2)*((st)**2) + 
        (diff( vout,ro )**2)*((sr)**2) + 
        (diff( vout,rf )**2)*((sr)**2) 
    )

    print( "Equação da propagação do erro para o circuito sem offset: " )
    print( latex(s) ) 
    s = s.subs(ro,68*k).subs(rf,10*k)*2.58 + 3.3/(4096*2)
    p = plot(s,(T, 5, 45), xlabel='Temperature (°C)', ylabel='$\\sigma_{AFE}$', title='Error vs Temperature',show=False,axis_center=(5,6.6225472e-5*2.58+ 3.3/(4096*2)))
    p.show()
    """
    #Com offset
    vout =  vin*( rb/ro )*( (rf+ro)/(ra+rb)  )  - ( rf/ro )* ( r1/(r1+r2) ) *vcc

   s = sqrt(  

        (diff( vout,T  )**2)*((st*T)**2) + 
        (diff( vout,ra )**2)*((ra*sr)**2) + 
        (diff( vout,rb )**2)*((rb*sr)**2) + 
        (diff( vout,ro )**2)*((ro*sr)**2) + 
        (diff( vout,r1 )**2)*((r1*sr)**2) + 
        (diff( vout,r2 )**2)*((r2*sr)**2) + 
        (diff( vout,rf )**2)*((rf*sr)**2) 
    )

    print( "Equação da propagação do erro para o circuito com offset: " )
    print(s)
    print( latex(s) ) 

    print( "Equacao com os valores substituidos\n" )
    s = s.subs(ro,ra).subs(rf,rb).subs(ra,15*k).subs(rb,16*k).subs(r1,1*k).subs(r2,32*k).subs(vcc,3.3)
    print(latex(simplify(s)))

    p = plot(s,(T, 5, 45), xlabel='Temperature (°C)', ylabel='$\\sigma_{AFE}$', title='Error vs Temperature',show=False,axis_center=(5,0.01))

    p.show()
    """
def potdissipada():
    vontc, vntc, vcc, r1, r2, rf, rntc, pntc, T, T0, plm, vlm, voutlm, ptotal = symbols("V_{out_ntc}, V_{NTC}, V_{cc}, R_1, R_2, R_f, R_{NTC}, P_{NTC_AFE}, T, T_0, P_{LM_AFE}, V_{LM}, V_{out_lm}, P_{Total}")
   
    vcc  = 3.3 
    Tmin = 10 + 273.15  #Minimum temperature in Kelvin
    Tmax = 40 + 273.15  #Maximum temperature in Kelvin
    R0   = 10*k         #Resistance at 25°C
    T0   = 298.15       #25°c -> °K
    b    = 3965         #beta value (Datasheet)
    ia = 100e-6
    r1 = 9100
    r2 = 12000
    r3 = 8200
    rf = 10000
    ra = 10000
    rb = 68000
    rntc = R0*( exp( b*( (1/T) - (1/T0) ) ) ) #Beta model equation
    vntc = rntc/(rntc+r3)*vcc
    vlm = 0.01*(T-273.15)
    
    it = -(vntc/r2) + ( vcc - vntc )/r1
    vontc = vntc - it*rf

    voutlm = vlm * (1 + rb/ra)

    pntc = (2*(vcc - vntc)**2/r1 + (vntc)**2/r2 + (vntc - vontc)**2/rf + ia*vcc)*1000

    plm = ((voutlm - vlm)**2/rb + (vlm)**2/ra + ia*vcc)*1000000

    ptotal = pntc + (plm/1000)

    m1 = (1.16-0.72)/(303.15 - 308.15)
    b1 = 1.16 - m1 * 303.15
    m = m1 /  (1 + rf * ((1 / r1) + (1 / r2)))
    bb = (b1 + (3.3 * (rf / r1)))/ (1 + rf * ((1 / r1) + (1 / r2)))
    vrealntc = m* T + bb



    print("m b")
    print(m, bb)
    #print("minimum power")
    #print(minimum(ptotal, T))

    p = plot(vrealntc, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$V_{NTCAFE}$ [V]', title='NTC AFE total energy dissipation',show=False, axis_center=(282,1.3))
    p.show()

    p = plot(vntc, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$V_{NTCAFE}$ [V]', title='NTC AFE total energy dissipation',show=False, axis_center=(282,1.1))
    p.show()

    p = plot(voutlm, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$V_{LM35AFE}$ [V]', title='LM35 AFE output voltage',show=False, axis_center=(282,0.7))
    p.show()

    p = plot(vontc, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$V_{NTCAFE}$ [V]', title='NTC AFE output voltage',show=False, axis_center=(282,0))
    p.show()

    p = plot(pntc, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$P_{NTCAFE}$ [mW]', title='NTC AFE power consumption',show=False, axis_center=(282,1.03))
    p.show()

    p = plot(plm, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$P_{LMAFE}$ [µW]', title='LM35 AFE power consumption',show=False,axis_center =(282, 335))
    p.show()

    p = plot(ptotal, (T, Tmin, Tmax), xlabel='Temperature (°K)', ylabel='$P_{NTCAFE}$ [mW]', title='Total power consumption',show=False, axis_center=(282,1.365))
    p.show()

    oi=(1/(ln(10.70/10)/3965 + 1/298.15))-273.15
    print(oi)

#NtcResToVoltage()
#NtcTempToVoltage()
#AfeNtc()
#lm35()
potdissipada()