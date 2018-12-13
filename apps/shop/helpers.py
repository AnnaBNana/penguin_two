INSURANCES = {
    (0, 50): 1.65,
    (50, 100): 2.05,
    (100, 200): 2.45,
    (200, 300): 4.60
}
EXPRESS_INSURANCES = {
    (100, 200): 0.75,
    (200, 500): 2.10,
    
}
# The price per additional $100 of insurance, valued over $300 up to $5,000, is $4.60 plus $0.90 per each $100 or fraction thereof.
def generate_insurance(cost):
    if cost <= 300:
        for bounds, value in INSURANCES.items():
            l, h = bounds
            if cost in range(l, h):
                return value
    else:
        return (((cost - cost % -100) - 300) / 100) * 0.9 + 4.60


def generate_insurance_express(cost):
    if cost <= 100:
        return 0
    elif cost <= 500.01:
        for bounds, value in EXPRESS_INSURANCES.items():
            l, h = bounds
            if cost in range(l, h):
                return value
    else:
        return (((cost - cost % -100) - 500) / 100) * 1.35 + 2.10
