# utils/xirr.py
import numpy as np
from datetime import datetime

def xirr(cashflows, dates):
    """Compute XIRR using Newton's method."""
    def f(rate):
        return sum(cf / ((1 + rate) ** ((d - dates[0]).days / 365)) for cf, d in zip(cashflows, dates))

    rate = 0.1  # initial guess
    for _ in range(100):
        f_val = f(rate)
        f_der = sum(
            -cf * ((d - dates[0]).days / 365) / ((1 + rate) ** (((d - dates[0]).days / 365) + 1))
            for cf, d in zip(cashflows, dates)
        )
        new_rate = rate - f_val / f_der
        if abs(new_rate - rate) < 1e-7:
            return new_rate
        rate = new_rate

    return rate
