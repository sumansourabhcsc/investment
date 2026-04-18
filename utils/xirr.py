import numpy as np

def xnpv(rate, cashflows):
    t0 = cashflows[0][0]
    return sum(
        cf / (1 + rate) ** ((t - t0).days / 365)
        for t, cf in cashflows
    )


def xirr(cashflows, guess=0.1):
    """
    Stable XIRR using numpy + iteration (no scipy required)
    """

    # sort by date
    cashflows = sorted(cashflows, key=lambda x: x[0])

    # remove invalid entries
    cashflows = [
        (t, cf) for t, cf in cashflows
        if t is not None and cf is not None
    ]

    if len(cashflows) < 2:
        return None

    rate = guess

    for _ in range(100):
        # derivative approximation
        npv = xnpv(rate, cashflows)

        if abs(npv) < 1e-6:
            return rate

        rate += -npv * 0.001  # damping for stability

        if rate <= -0.9999:
            return None

    return None
