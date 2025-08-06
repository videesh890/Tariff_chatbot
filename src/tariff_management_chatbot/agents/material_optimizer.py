from ..data.loader import load_tariff_data

class MaterialOptimizer:
    def suggest_materials(self, product_name, hts_code=None):
        try:
            df = load_tariff_data()
            mask = df['Product_Description'].str.lower().str.contains(product_name.lower())
            if hts_code:
                mask &= (df['HTS_Code'].astype(str) == str(hts_code))
            matches = df[mask]
            if matches.empty:
                return {"message": "No data found for this product."}

            suggestions = []
            for _, row in matches.iterrows():
                # We'll suggest materials from Material_Composition and Primary_Material fields
                if isinstance(row['Material_Composition'], str):
                    suggestions.append({
                        "materials": row['Material_Composition'],
                        "primary_material": row['Primary_Material'],
                        "potential_savings_usd": row.get('Potential_Savings_USD', 0)
                    })
            if not suggestions:
                return {"message": "No material optimization suggestions available for this product."}
            # Sort by savings, if any
            suggestions = sorted(suggestions, key=lambda x: x.get("potential_savings_usd",0), reverse=True)
            return {"suggestions": suggestions[:3]}
        except Exception as e:
            print("MATERIAL OPTIMIZER ERROR:", e)
            return {"message": f"Internal server error: {str(e)}"}











































































































































