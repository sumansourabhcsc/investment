from datetime import datetime
import numpy as np

def xnpv(rate, cashflows):
    return sum(
        cf / (1 + rate) ** ((t - cashflows[0][0]).days / 365)
        for t, cf in cashflows
    )


def xirr(cashflows, guess=0.1):
    """
    cashflows = [(date, amount), ...]
    """
    try:
        import scipy.optimize as opt

        def f(rate):
            return xnpv(rate, cashflows)

        return opt.newton(f, guess)

    except:
        # fallback simple solver
        rate = guess
        for _ in range(50):
            f = xnpv(rate, cashflows)
            rate += -f * 0.01
        return rate
