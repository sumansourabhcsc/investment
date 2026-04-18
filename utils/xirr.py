import numpy as np

def xnpv(rate, cashflows):
    t0 = cashflows[0][0]
    return sum(
        cf / (1 + rate) ** ((t - t0).days / 365)
        for t, cf in cashflows
    )


def xirr(cashflows):
    cashflows = sorted(cashflows, key=lambda x: x[0])

    def f(rate):
        return xnpv(rate, cashflows)

    # wide search space (IMPORTANT for SIPs)
    low, high = -0.999, 5.0

    f_low = f(low)
    f_high = f(high)

    # if no sign change → fallback CAGR (IMPORTANT FIX)
    if f_low * f_high > 0:
        start = cashflows[0][0]
        end = cashflows[-1][0]

        total_invested = -sum(cf for _, cf in cashflows if cf < 0)
        final_value = sum(cf for _, cf in cashflows if cf > 0)

        years = (end - start).days / 365

        if years <= 0:
            return None

        return (final_value / total_invested) ** (1 / years) - 1

    # stable bisection solver
    for _ in range(200):
        mid = (low + high) / 2
        f_mid = f(mid)

        if abs(f_mid) < 1e-7:
            return mid

        if f_low * f_mid < 0:
            high = mid
        else:
            low = mid

    return mid
