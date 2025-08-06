from ..data.loader import load_tariff_data
class ScenarioSimulator:
    def simulate(self, product_name, alt_material=None, alt_country=None):
        try:
            df = load_tariff_data()
            # Assuming column names in the CSV are like 'Product_Description', 'Landed_Cost_USD', etc.
            # The user needs to ensure their CSV has these exact column names.
            mask = df['Product_Description'].str.lower().str.contains(product_name.lower())
            scenarios = []
            base_df = df[mask]
            if base_df.empty:
                return {"message": "No data found for this product."}

            for _, row in base_df.iterrows():
                # Base scenario
                scenario = {
                    "Product_Description": row.get("Product_Description"),
                    "HTS_Code": row.get("HTS_Code"),
                    "Country_of_Origin": row.get("Country_of_Origin"),
                    "Material_Cost_USD": row.get("Material_Cost_USD"),
                    "Tariff_Rate_Percent": row.get("Tariff_Rate_Percent"),
                    "Landed_Cost_USD": row.get("Landed_Cost_USD"),
                    "Primary_Material": row.get("Primary_Material"),
                    "scenario": "current"
                }
                scenarios.append(scenario)

                # Alternative Material Scenario
                if alt_material and (
                    alt_material.lower() in str(row.get("Material_Composition", "")).lower()
                    or alt_material.lower() == str(row.get('Primary_Material', "")).lower()
                ):
                    alt = scenario.copy()
                    alt["Primary_Material"] = alt_material
                    # In a real model, tariff and cost would be recalculated here.
                    alt["scenario"] = f"alt_material: {alt_material}"
                    scenarios.append(alt)

                # Alternative Country Scenario
                if alt_country and (
                    alt_country.lower() == str(row.get("Alternative_Country", "")).lower()
                ):
                    alt = scenario.copy()
                    alt["Country_of_Origin"] = alt_country
                    # Simulate a new landed cost by applying the potential savings
                    alt["Landed_Cost_USD"] = scenario["Landed_Cost_USD"] - float(row.get("Potential_Savings_USD", 0))
                    alt["scenario"] = f"alt_country: {alt_country}"
                    scenarios.append(alt)
            
            # Sort by landed cost ascending and return the top 3
            scenarios = sorted(scenarios, key=lambda x: x.get('Landed_Cost_USD', float('inf')))
            return {"scenarios": scenarios[:3]}

        except Exception as e:
            print("SCENARIO SIM ERROR:", e)
            return {"message": f"Internal server error: {str(e)}"}
        
    #C:\Users\visha\OneDrive\Desktop\tarrifchatbot\tariff_management_chatbot