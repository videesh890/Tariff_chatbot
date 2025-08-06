import pandas as pd
import os
def load_tariff_data(csv_file=None):
    # Assume project is run from the root directory
    if csv_file is None:
        csv_file = os.path.join('data', 'tariffs.csv')
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Tariff data not found at {csv_file}")
    return pd.read_csv(csv_file)
