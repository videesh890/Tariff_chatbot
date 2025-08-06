def compute_landed_cost(base_price, tariff_rate, mpf_fee, quantity):
    landed_cost_per_unit = base_price * (1 + tariff_rate) + mpf_fee / quantity
    total_landed_cost = landed_cost_per_unit * quantity
    return landed_cost_per_unit, total_landed_cost
