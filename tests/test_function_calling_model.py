# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')

from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Simuler l'exécution de la fonction
def get_weather(params):
    print("PARAMS", params)
    location = params['location'].rsplit(',')[0] # pour les modèle qui précisent "Paris, France" comme mistralai/Mistral-Small-3.2-24B-Instruct-2506 ou openai/gpt-oss-120b
    print("location", location)
    # Une vraie implémentation irait chercher la météo
    if location == 'Lyon' :
        return f"23°C, risque de pluie 0%, vent 5km/h"
    elif location == 'Paris' :
        return f"3°C, risque de pluie 70%, vent 30km/h"
    else: 
        return f"Il fait beau à {location} aujourd'hui."

# Configurez votre client (base_url et api_key doivent être dans votre .env)
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

chat_model = os.getenv("CHAT_MODEL")
# Définissez un outil très simple, comme la météo
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

messages = [{"role": "user", "content": "Quel temps fait-il à Paris ?"}]

try:
    response = client.chat.completions.create(
        model=chat_model,  # Remplacez par le nom de votre modèle
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Laissez le modèle décider
    )

    # Vérifiez si le modèle a appelé un outil
    # if response.choices[0].message.tool_calls:
    #     print("✅ Le modèle supporte le function calling !  Réponse :", response.choices[0].message.content)
    #     print("Outil appelé :", response.choices[0].message.tool_calls[0].function.name)
    #     print("Arguments :", response.choices[0].message.tool_calls[0].function.arguments)
    #     print("response :", response)
    # else:
    #     # Si pas d'appel, regardez la réponse texte
    #     print("⚠️ Le modèle n'a pas appelé d'outil. Réponse :", response.choices[0].message.content)

    message = response.choices[0].message

    if message.tool_calls:
        print("✅ Le modèle supporte le function calling !")
        tool_call = message.tool_calls[0]
        print(f"Outil appelé : {tool_call.function.name}")
        arguments = json.loads(tool_call.function.arguments)
        print(f"Arguments : {arguments}")


        result = get_weather(arguments)

        print("RESULT", result)

        # Ajouter la réponse de la fonction à la conversation
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": result
        })

        # Deuxième appel pour obtenir la réponse finale
        second_response = client.chat.completions.create(
            model=os.getenv("CHAT_MODEL"),
            messages=messages
        )
        final_answer = second_response.choices[0].message.content
        print(f"Réponse finale : {final_answer}")
    else:
        print("⚠️ Le modèle n'a pas appelé d'outil. Réponse :", message.content)

except Exception as e:
    print(f"❌ Erreur lors de l'appel : {e}")
    print("Cela peut indiquer que le modèle ne supporte pas le function calling ou que l'API n'est pas compatible.")