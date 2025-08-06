import uvicorn
from src.tariff_management_chatbot.api.app import app

def main():
    # CLI mode placeholder:
    # TODO: add CLI logic here as needed
    # For now, only launch API
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
