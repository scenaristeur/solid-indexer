# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')

from openai import OpenAI
import json
import os, re
from dotenv import load_dotenv

load_dotenv()

# Simuler l'exécution de la fonction
def get_weather(params):
    print("weather PARAMS", params)
    location = params['location'].rsplit(',')[0] # pour les modèle qui précisent "Paris, France" comme mistralai/Mistral-Small-3.2-24B-Instruct-2506 ou openai/gpt-oss-120b
    print("location", location)
    # Une vraie implémentation irait chercher la météo
    if location == 'Lyon' :
        return f"23°C, risque de pluie 0%, vent 5km/h"
    elif location == 'Paris' :
        return f"3°C, risque de pluie 70%, vent 30km/h"
    else: 
        return f"Il fait beau à {location} aujourd'hui."

def get_currency(params):
    print("currency PARAMS", params)
    currency = params['currency']
    print("currency", currency)
    # Une vraie implémentation irait chercher la météo
    if currency == 'Yen' :
        return f"le yen a un taux de change de 1 pour 10"
    elif currency == 'Dolar' :
        return f"le dollar s'échange à 5263 €"
    else: 
        return f"pas d'infos sur {currency} aujourd'hui."
def parse_tool_call(text: str):
    """
    Retourne une liste de tuples (tool_name, arguments_dict).
    """
    # 1. Vérifier le préfixe
    if not text.startswith("[TOOL_CALLS]"):
        raise ValueError("Texte ne commence pas par [TOOL_CALLS]")

    # 2. Séparer les appels d'outils
    tool_calls = text.split("[TOOL_CALLS]")[1:]

    results = []
    for tool_call in tool_calls:
        # 3. Trouver le nom de l'outil et le JSON
        tool_name_match = re.search(r'^(\w+)', tool_call)
        if not tool_name_match:
            raise ValueError("Impossible de trouver le nom de l'outil")

        tool_name = tool_name_match.group(1)

        # 4. Extraire le JSON en trouvant les accolades
        json_start = tool_call.find('{')
        json_end = tool_call.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("Impossible de trouver le JSON")

        json_part = tool_call[json_start:json_end]

        # 5. Nettoyer le JSON (dé‑échapper les antislashs)
        # json_clean = json_part.encode('utf-8').decode('unicode_escape')

        print(f"\nTOOL_NAME: {tool_name}")
        print(f"\nàààààààà\nJSON_PART: {json_part}\n------aaaa----------\n")
        # print(f"\nbbbbbbbbb\nJSON_CLEAN: {json_clean}\n-----bbbb\n")
        # json_clean = json_clean.strip("{}")
        # utilisable =  dict(item.split(": ") for item in json_clean.split(", "))
        utilisable = eval(json_part)
        print(f'\nccccccc\nTITRE : {utilisable.titre}\n----------ccccc\n')

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
    },
        {
        "type": "function",
        "function": {
            "name": "get_currency",
            "description": "Get the current currency course",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "The currency",
                    },
                },
                "required": ["currency"],
            },
        },
    },
        {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Crée une nouvelle note avec un titre et un contenu",
            "parameters": {
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": "URI de la note à créer"
                    },
                    "title": {
                        "type": "string",
                        "description": "Titre de la note (slug)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenu au format turtle VALIDE de la note"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Tags optionnels séparés par des virgules"
                    }
                },
                "required": [
                    "uri",
                    "title",
                    "content"
                ]
            }
        }
    },
]

# messages = [{"role": "user", "content": "Quel temps fait-il à Paris et à Lyon ?"}]
# messages = [{"role": "user", "content": "créé deux notes : une sur Paris, l'autre sur Python."}]
messages = [{"role": "user", "content": "créé deux notes : une sur javascript, l'autre sur Python."}]


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

    print(f"\n99999\nRESPONSE: {response}\n----------999----")

    message = response.choices[0].message
    print(f"Message reponse: {message}\n")

    if message.tool_calls:
        print("✅ Le modèle supporte le function calling !")
        tool_call = message.tool_calls[0]
        print(f"Outil appelé : {tool_call.function.name}")
        arguments = json.loads(tool_call.function.arguments)
        print(f"Arguments : {arguments}")
        results = []
        if tool_call.function.name == "get_weather":
            results.append(get_weather(arguments))
        if tool_call.function.name == "get_currency":
            results.append(get_currency(arguments))

        print(f"RESULTS : {results}\n")

        # Ajouter la réponse de la fonction à la conversation
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": ",".join(results)
        })

        # Deuxième appel pour obtenir la réponse finale
        second_response = client.chat.completions.create(
            model=os.getenv("CHAT_MODEL"),
            messages=messages
        )
        final_answer = second_response.choices[0].message.content
        print(f"\nRéponse finale : {final_answer}")
    elif response.choices[0].finish_reason=='stop' and message.content.startswith("[TOOL_CALLS]"):
        # message.content[len("[TOOL_CALLS]"):]
        # calls = json.loads()
        # print(f"_____________ TOOL_CALLS A GERER: \n{response.choices[0]}\n__________\n")
        results = parse_tool_call(message.content)
        print(f"******* TOOL_CALLS RESULTS \n{ json.dumps(results, indent=4)}\n**********\n")
    else:
        print("\n⚠️ Le modèle n'a pas appelé d'outil. Réponse :", message.content)

except Exception as e:
    print(f"❌ Erreur lors de l'appel : {e}")
    print("Cela peut indiquer que le modèle ne supporte pas le function calling ou que l'API n'est pas compatible.")