from sympy import * 
import matplotlib as mp
from sympy.plotting import plot

k = 1000

def NtcTempToVoltage():
    #Here although less accurate its used the Beta model
    #Because it gives the resistance at a certain temperature 
    R, R0, T0, b,Rntc,T, Vout  = symbols("R, R_0, T_0, beta,R_{NTC}, T, V_{out}")
    
    vcc  = 3.3 
    Tmin = 10  + 273.15
    Tmax = 40 + 273.15
    R0   = 10*k
    T0   =  298.15
    b    = 3965
    Rntc = R0*( exp( b*( (1/T) - (1/T0) ) ) )
    Vout = Rntc/(Rntc+R)
    Vout = Vout * vcc
    
    p = plot(Vout.subs(R,8*k) ,(T,Tmin,Tmax), xlabel='Temperature (°K)', ylabel='$V_{out}$', title='Output Voltage vs Temperature (8k$\Omega$)',show=False,axis_center=(282,1.3))
    #p.show()
    p = plot(Vout.subs(R,100*k),(T,Tmin,Tmax), xlabel='Temperature (°K)', ylabel='$V_{out}$', title='Output Voltage vs Temperature (100k$\Omega$)',show=False,axis_center=(282,0.15))
    p.show()
    print( str( Vout.evalf(subs={R:8*k,T:Tmax}) ) + " " +str(Vout.evalf(subs={R:8*k,T:Tmin})) )
    #print( Vout.evalf(subs={R:100*k,T:Tmax}) - Vout.evalf(subs={R:100*k,T:Tmin}) )

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

def AfeNtc():

    vo, vp, vcc , r3, r1,r2,it,rf = symbols("V_{out}, V_p, V_{cc}, R_3, R_1,R_2, i_t, R_f")
    
    it = -(vp/r2) + ( vcc - vp )/r1
    vo = vp - it*rf
    #Here the circuit's function is found
    print("Circuit Function: ")
    print(latex(factor(vo,vp)))
    print()
    #r1= 10*k
    
    #After having the circuit function we analyse the equation
    # and find the part that's responsible for the offset and gain
    # and solve the equation system that gives us the desired offset and gain 
    rf  = 10*k
    vcc = 3.3
    
    of = rf/r1 #Offset
    of = of * vcc
    gain = 1 + rf*( (r2+r1)/(r2*r1) )
    #gain = gain.subs(rf,10*k).evalf()
    #of   = of.subs(rf,10*k).evalf()

    print("R1,R2")
    s = solve( [ gain - 2.92,of - 3.53 ],r1,r2 )
    print(s)


#----------------LM35----------------#
#Com o circuito novo ]e sem offset

def lm35():
    vin, T, vout, s, ra, rb,ro,rf,r1,r2,vcc = symbols("V_{in},T,V_{out},sigma,R_a,R_b,R_o,R_f,R_1,R_2,V_{cc}")
    emax = symbols("epsilon_{max}")

    sr, st = symbols("sigma_r, sigma_s")

    vin = T*0.01 

    """
    #Sem offset
    vout = vin * (1 + (rf/ro))

    s = sqrt(

        (diff( vout,T  )**2)*((st)**2) + 
        (diff( vout,ro )**2)*((sr)**2) + 
        (diff( vout,rf )**2)*((sr)**2) 
    )

    print( "Equação da propagação do erro para o circuito sem offset: " )
    print( latex(s) ) 
    """

    #Com offset
    vout =  vin*( rb/ro )*( (rf+ro)/(ra+rb)  )  - ( rf/ro )* ( r1/(r1+r2) ) *vcc
    tolerance = 10/100 #tolerancia da resistencia

    sr = tolerance/(sqrt(3))
    st = (1/100)/sqrt(3) 
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

    p = plot(s,(T, 5, 45), xlabel='Temperature (°C)', ylabel='$\sigma_{AFE}$', title='Error vs Temperature',show=False,axis_center=(5,0.01))

    p.show()


#NtcResToVoltage()
#NtcTempToVoltage()
AfeNtc()