from fastapi import APIRouter, Query
from ..agents.tariff_agent import TariffAgent
from ..data.loader import load_tariff_data
from ..agents.material_optimizer import MaterialOptimizer
from ..agents.scenario_simulator import ScenarioSimulator
from ..utils.semantic_search import semantic_search

router = APIRouter()

agent = TariffAgent()
material_optimizer = MaterialOptimizer()
simulator = ScenarioSimulator()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/calculate-tariff")
def calculate_tariff(
    material_cost_usd: float = Query(...),
    quantity: int = Query(...),
    tariff_rate_percent: float = Query(...),
    mpf_usd: float = Query(0.0),
    other_fees_usd: float = Query(0.0)
):
    return agent.calculate_tariff(material_cost_usd, quantity, tariff_rate_percent, mpf_usd, other_fees_usd)

@router.get("/hts-lookup")
def hts_lookup(hts_code: str):
    df = load_tariff_data()
    results = df[df['HTS_Code'].astype(str) == str(hts_code)].to_dict(orient='records')
    if not results:
        return {"error": "HTS code not found"}
    return {"count": len(results), "results": results[:5]}

@router.get("/product-search")
def product_search(
    product_name: str = "",
    company_name: str = "",
    country_of_origin: str = ""
):
    df = load_tariff_data()
    query = df
    if product_name:
        query = query[query['Product_Description'].str.contains(product_name, case=False, na=False)]
    if company_name:
        query = query[query['Company'].str.contains(company_name, case=False, na=False)]
    if country_of_origin:
        query = query[query['Country_of_Origin'].str.contains(country_of_origin, case=False, na=False)]
    results = query.to_dict(orient='records')
    if not results:
        return {"count": 0, "results": [], "message": "No matching products found."}
    return {"count": len(results), "results": results[:5]}

@router.get("/material-optimization")
def material_optimization(product_name: str, hts_code: str = ""):
    return material_optimizer.suggest_materials(product_name, hts_code if hts_code else None)

@router.get("/scenario-simulation")
def scenario_simulation(
    product_name: str,
    alt_material: str = "",
    alt_country: str = "",
    sort_by: str = Query("Landed_Cost_USD"),
    direction: str = Query("asc")
):
    result = simulator.simulate(product_name, alt_material or None, alt_country or None)
    if "scenarios" in result and result["scenarios"]:
        if sort_by in result["scenarios"][0]:
            reverse = direction.lower() == "desc"
            result["scenarios"] = sorted(result["scenarios"], key=lambda x: x.get(sort_by, 0), reverse=reverse)
        result["scenarios"] = result["scenarios"][:3]
    return result

@router.get("/smart-product-search")
def smart_product_search(query: str, top_n: int = 3):
    try:
        results = semantic_search(query, top_n)
        return {"results": results}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@router.get("/semantic-scenario-simulation")
def semantic_scenario_simulation(
    query: str,
    top_n: int = 1,
    sort_by: str = "Landed_Cost_USD",
    direction: str = "asc"
):
    try:
        matches = semantic_search(query, top_n)
        if not matches:
            return {"message": "No product matches found for your query."}
        scenarios_all = []
        for match in matches:
            product_name = match["Product_Description"]
            scenarios = simulator.simulate(product_name)
            if "scenarios" in scenarios:
                scenarios_all.extend(scenarios["scenarios"])
        reverse = direction == "desc"
        scenarios_all = sorted(scenarios_all, key=lambda x: x.get(sort_by, 0), reverse=reverse)[:3]
        return {"scenarios": scenarios_all}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@router.get("/semantic-tariff-lookup")
def semantic_tariff_lookup(query: str, top_n: int = 3):
    try:
        matches = semantic_search(query, top_n)
        rows = [
            {
                "Product_Description": m["Product_Description"],
                "HTS_Code": m["HTS_Code"],
                "Tariff_Rate_Percent": m["Tariff_Rate_Percent"],
                "Country_of_Origin": m["Country_of_Origin"],
                "Landed_Cost_USD": m["Landed_Cost_USD"]
            }
            for m in matches
        ]
        return {"matches": rows}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}
