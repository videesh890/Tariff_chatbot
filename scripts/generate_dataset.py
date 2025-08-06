# Save this as scripts/generate_dataset.py and run it separately
from faker import Faker
import pandas as pd
import random

fake = Faker()
rows = []
for i in range(10000):
    d = {
        "record_id": i+1,
        "company_name": fake.company(),
        "product_name": fake.word().capitalize() + " " + fake.word().capitalize(),
        "hts_code": fake.numerify(text='########'),
        "country_of_origin": fake.country(),
        "import_country": fake.country(),
        "import_date": fake.date_between(start_date="-2y", end_date="today"),
        "fta_status": fake.boolean(),
        "base_price_usd": round(random.uniform(1, 100), 2),
        "quantity": random.randint(100, 10000),
        "tariff_rate_pct": round(random.uniform(0.01, 0.15), 3),
        "mpf_fee_usd": round(random.uniform(0, 25), 2),
        "landed_cost_usd": round(random.uniform(1, 150), 2),
        "compliance_flag": fake.boolean(),
        "compliance_notes": fake.sentence(),
        "alt_country_1": fake.country(),
        "alt_country_1_savings_usd": round(random.uniform(0, 50000), 2),
        "alt_country_2": fake.country(),
        "alt_country_2_savings_usd": round(random.uniform(0, 50000), 2),
        "suggested_material_1": fake.word().capitalize(),
        "suggested_material_1_pct": round(random.uniform(1, 20), 1),
        "suggested_material_2": fake.word().capitalize(),
        "suggested_material_2_pct": round(random.uniform(1, 20), 1),
        "risk_level": random.choice(['low', 'medium', 'high']),
        "report_notes": fake.text(max_nb_chars=20),
        "last_updated": fake.date_time_between(start_date="-2y", end_date="now"),
    }
    rows.append(d)
df = pd.DataFrame(rows)
df.to_csv("data/tariffs.csv", index=False)
