import math
def sealed(Fs,Qts,Vas,Vb):
    a=Vas/Vb; Qtc=Qts*math.sqrt(1+a); Fc=Fs*math.sqrt(1+a)
    # F3 of 2nd-order highpass with Q=Qtc
    def H2(f):
        r=(f/Fc)**2
        return r*r/((1-r)**2+r/Qtc**2)
    lo,hi=1.0,5000.0
    for _ in range(80):
        m=(lo+hi)/2
        if H2(m)<0.5: lo=m
        else: hi=m
    peak=max(10*math.log10(H2(Fc*10**(i/200))) for i in range(-200,300))
    return Qtc,Fc,lo,peak
def vented(Fs,Qts,Vas,Vb,Fb,QL=7.0):
    """4th-order vented/PR approximation (Thiele-Small), returns F3 and max ripple dB"""
    a=Vas/Vb; h=Fb/Fs
    def Hn(f):
        s=1j*f/Fs
        den=s**4 + s**3*(1/(QL*h)+1/Qts) + s**2*((1+a)+h**2+1/(QL*h*Qts)) + s*(h**2/Qts+1/(QL*h)) + h**2
        return abs(s**4/den)**2
    lo,hi=1.0,5000.0
    for _ in range(80):
        m=(lo+hi)/2
        if Hn(m)<0.5: lo=m
        else: hi=m
    peak=max(10*math.log10(Hn(Fs*10**(i/200))) for i in range(-200,400))
    return lo,peak
if __name__=='__main__':
    # sanity: Qts .4 Vas 1L Vb 1L -> Qtc .566 Fc 1.41 Fs
    print(sealed(100,0.4,1.0,1.0))
    print(vented(100,0.4,1.0,1.0,100))
    # DMA45-4 (Fs 148 Hz, Qts 0.56, Vas 0.17 L) in 115 cm3 sealed -> Qtc ~0.73, F3 ~190 Hz
    print(sealed(148,0.56,0.17,0.115))
