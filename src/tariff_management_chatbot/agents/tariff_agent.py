class TariffAgent:
    def calculate_tariff(self, material_cost_usd, quantity, tariff_rate_percent, mpf_usd=0.0, other_fees_usd=0.0):
        if quantity == 0:
            return {"error": "Quantity cannot be zero."}
        landed_cost_per_unit = float(material_cost_usd) * (1 + float(tariff_rate_percent) / 100) + (float(mpf_usd) + float(other_fees_usd)) / float(quantity)
        total_landed_cost = landed_cost_per_unit * float(quantity)
        return {
            "landed_cost_per_unit": round(landed_cost_per_unit, 2),
            "total_landed_cost": round(total_landed_cost, 2),
            "details": {
                "material_cost_usd": material_cost_usd,
                "quantity": quantity,
                "tariff_rate_percent": tariff_rate_percent,
                "mpf_usd": mpf_usd,
                "other_fees_usd": other_fees_usd
            }
        }
