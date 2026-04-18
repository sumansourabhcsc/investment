# utils/xirr.py
import numpy as np

def xirr(cashflows, dates, guess=0.1):
    def npv(rate):
        return sum(
            cf / ((1 + rate) ** ((d - dates[0]).days / 365))
            for cf, d in zip(cashflows, dates)
        )

    rate = guess
    for _ in range(100):
        f = npv(rate)
        df = sum(
            -((d - dates[0]).days / 365) * cf /
            ((1 + rate) ** (((d - dates[0]).days / 365) + 1))
            for cf, d in zip(cashflows, dates)
        )
        new_rate = rate - f / df
        if abs(new_rate - rate) < 1e-7:
            return new_rate
        rate = new_rate

    return rate
