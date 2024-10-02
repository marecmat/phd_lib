from numpy.lib.scimath import sqrt

def JCA(om, porous_material, saturating_fluid, return_F=False, return_G=False):
    """
    Johnson-Champoux-Allard model
    exp(-1j*om*t) convention --> use np.conjugate if K_eq, rho_eq are needed in the other convention
    """
    p = porous_material;        f = saturating_fluid

#    om_c = p['sigma']*p['phi']/(f['rho']*p['tort'])
#    G_om = sqrt(1 - 4j*(f['eta']*f['rho']*p['tort']**2/(p['sigma']*p['phi']*p['ldp'])**2)*f['Pr']*om)     
#    F_om = sqrt(1 - 4j*(f['eta']*f['rho']*p['tort']**2/(p['sigma']*p['phi']*p['ld'])**2)*om)
#
#    K_eq = f['gamma']*f['p0']/(p['phi']*(f['gamma'] - (f['gamma'] - 1)/(1 + 1j*om_c/(f['Pr']*om)*G_om)))
#    rho_eq = f['rho']*p['tort']/p['phi']*(1 + 1j*om_c/om*F_om)

    nu = f['eta']/f['rho'];                 q0 = f['eta']/p['sigma']
    nu_p = f['eta']/(f['rho']*f['Pr']);     q0_p = 1/8*p['phi']*p['ldp']**2

    F = (1 - 1j*om/nu*(2*p['tort']*q0/(p['phi']*p['ld']))**2)**(1/2)
    G = (1 - 1j*om/nu_p*(p['ldp']/4)**2)**(1/2)

    rho_eq = f['rho']/p['phi']*(p['tort'] - F*(nu*p['phi'])/(1j*om*q0))
    K_eq = f['gamma']*f['p0']/p['phi']/(f['gamma'] - (f['gamma'] - 1)/(1 - G*(nu_p*p['phi'])/(1j*om*q0_p)))
    
    if return_F: 
        return K_eq, rho_eq, F
    if return_G: 
        return K_eq, rho_eq, G
    if return_F and return_G: 
        return K_eq, rho_eq, F,G
    return K_eq, rho_eq

def  biot(om, porous_material, saturating_fluid, 
          fullBiotcoefficients=True, dict_out=False, 
          u_p_formulation=False):
    
    """
    Computes the Biot coefficient, equivalent densities and wavenumbers for poroelastic materials

    Parameters
    ----------
    om: float or array
        The frequency(ies) at which the biotStuff will be computed
    porous_material: dict
        Porous material properties
    saturating_fluid: dict
        Saturating fluid properties
    fullBiotcoefficients: bool
        Whether to use the complete expressions for Biot coefficients 
        or the rigid approximations
        
    Returns
    -------
        
    parameters: tuple or tuple of lists
        The parameters calculated. The order is:
        Kf, rho_eq, mu1, mu2, mu3, k1, k2, k3, P, Q, R, rho11t, rho12t, rho22t
    """
    p = porous_material;     f = saturating_fluid


    Kf, rho_eq  = JCA(om, p, f)

    if fullBiotcoefficients:

        P = ((1 - p['phi'])*(1 - p['phi'] - p['Kb']/p['Ks'])*p['Ks'] + p['phi']*(p['Ks']/Kf)*p['Kb'])/ \
                            (1 - p['phi'] - p['Kb']/p['Ks'] + p['phi']*p['Ks']/Kf) + 4/3*p['N']

        Q = (1 - p['phi'] - p['Kb']/p['Ks'])*p['phi']*p['Ks']/ \
                            (1 - p['phi'] - p['Kb']/p['Ks'] + p['phi']*p['Ks']/Kf)

        R = p['phi']**2*p['Ks']/ \
                            (1 - p['phi'] - p['Kb']/p['Ks'] + p['phi']*p['Ks']/Kf)

    else: 
        P = 4/3*p['N'] + p['Kb'] + (1 - p['phi']**2)/p['phi']*Kf
        Q = Kf*(1 - p['phi'])
        R = p['phi']*Kf

    # Equivalent densities
    rho11t = p['rho1'] - p['phi']*f['rho'] + p['phi']**2*rho_eq
    rho12t = p['phi']*f['rho'] - p['phi']**2*rho_eq
    rho22t = p['phi']**2*rho_eq

    Delta = (P*rho22t + R*rho11t - 2*Q*rho12t)**2 - 4*(P*R - Q**2)*(rho11t*rho22t - rho12t**2)
    delta1_sq = om**2/(2*(P*R - Q**2))*(P*rho22t + R*rho11t - 2*Q*rho12t - sqrt(Delta))
    delta2_sq = om**2/(2*(P*R - Q**2))*(P*rho22t + R*rho11t - 2*Q*rho12t + sqrt(Delta))
    delta3_sq = om**2/p['N']*(rho11t*rho22t - rho12t**2)/rho22t

    mu1 = (P*delta1_sq - om**2*rho11t)/(om**2*rho12t - Q*delta1_sq)
    mu2 = (P*delta2_sq - om**2*rho11t)/(om**2*rho12t - Q*delta2_sq)
    # mu3 = (p['N']*delta3_sq - om**2*rho11t)/(om**2*rho22t)
    mu3 = -rho12t/rho22t

    k1, k2, k3 = sqrt(delta1_sq), sqrt(delta2_sq), sqrt(delta3_sq)

    if dict_out:
        out_dict = {
            'Kf':Kf, 'rho_eq':rho_eq, 'mu1':mu1, 'mu2':mu2, 'mu3':mu3, 'k1':k1, 'k2':k2, 'k3':k3, 
            'P':P, 'Q':Q, 'R':R, 'rho11t':rho11t, 'rho12t':rho12t, 'rho22t':rho22t
        }
        if u_p_formulation: 
            out_dict.update({
                'gamma_t' : p['phi']*(rho12t/rho22t - Q/R),
                'rho_t'   : rho11t - rho12t**2/rho22t, 
                'p_hat'   : P - Q**2/R,
                'a_hat'   : P - Q**2/R - 2*p['N']
            })
        return out_dict
    else:
        out_list = Kf, rho_eq, mu1, mu2, mu3, k1, k2, k3, P, Q, R, rho11t, rho12t, rho22t
    #              0        1   2    3    4    5   6   7  8  9  10    11       12      13
        if u_p_formulation: out_list.extend([
            p['phi']*(rho12t/rho22t - Q/R), rho11t - rho12t**2/rho22t, 
            P - Q**2/R, out_dict['p_hat'] - 2*p['N']])
    
        return out_list
