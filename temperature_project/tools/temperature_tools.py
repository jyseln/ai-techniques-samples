def fetch_temperature(city: str) -> str:
    return f"The temperature in {city.capitalize()} is approximately 35°C "


fetch_temperature_tool_def = {
    "type": "function",
    "function": {
        "name": "fetch_temperature",
        "description": "Use this function to fetch the temperature for the given city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name",
                },
            },
            "required": ["city"],
        },
    },
}
