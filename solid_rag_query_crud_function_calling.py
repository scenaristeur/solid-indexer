import os
from dotenv import load_dotenv
from solid_auth import SolidAuthenticatedSession
import json
# from solid_versioned_store import SolidVersionedStore
from solid_crud_store import SolidCRUDStore
from openai import OpenAI
import logging

load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation de la session Solid
session = SolidAuthenticatedSession(
    idp_url=os.getenv("SOLID_IDP_URL"),
    client_id=os.getenv("SOLID_CLIENT_ID"),
    client_secret=os.getenv("SOLID_CLIENT_SECRET")
)

base_container="http://localhost:3000/david/notes/"
webid= "http://localhost:3000/david/profile/card#me"
# webid = session.get_webid()
# print(webid)  # Affiche http://localhost:3000/david/profile/card#me

# print( session.toJSON())
# Initialisation
# store = SolidVersionedStore(session, base_container="http://localhost:3000/david/notes/")
store = SolidCRUDStore(session, base_container="http://localhost:3000/david/notes/", webid=webid)

# Client OpenAI
openai_client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
chat_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")

system_prompt = f"""Tu es un assistant personnel qui gère des notes sur un pod Solid.
Tu as accès à des fonctions pour créer, modifier, supprimer et lister des notes.
Le container de base est : {base_container}
Lorsque l'utilisateur te demande de créer une note, tu DOIS utiliser la fonction 'create_note'.
N'écris pas de longs discours : utilise les fonctions pour agir directement.
Par exemple, si l'utilisateur dit "crée une note sur le projet", appelle create_note avec un titre et un contenu appropriés.
Ne donne pas de conseils sur la façon de créer une note : crée-la réellement via la fonction.
"""
messages = [{"role": "system", "content": system_prompt}]
# # Exemple pour montrer l'utilisation correcte
# example_messages = [
#     {"role": "user", "content": "crée une note avec le titre 'Idées' et le contenu 'Acheter du lait'"},
#     {"role": "assistant", "content": None, "tool_calls": [{
#         "id": "12356789",
#         "type": "function",
#         "function": {
#             "name": "create_note",
#             "arguments": json.dumps({"title": "Idees", "content": "Acheter du lait", "tags": ""})
#         }
#     }]},
#     {"role": "tool", "tool_call_id": "123456789", "name": "create_note", "content": "Note créée : http://localhost:3000/david/notes/Idees"},
#     {"role": "assistant", "content": "J'ai créé la note 'Idées' pour vous. Vous pouvez la consulter à l'URI : http://localhost:3000/david/notes/Idees"},
#     {"role": "user", "content": "Super, continuons"}
# ]
# messages.extend(example_messages)

# Définition des fonctions disponibles
tools = [
    {
                "type": "function",
        "function": {
        "name": "create_note",
        "description": "Crée une nouvelle note avec un titre et un contenu",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Titre de la note (slug)"},
                "content": {"type": "string", "description": "Contenu textuel de la note"},
                "tags": {"type": "string", "description": "Tags optionnels séparés par des virgules"}
            },
            "required": ["title", "content"]
        }
        }
    },
        {        "type": "function",
        "function": {
        "name": "read_note",
        "description": "Lit le contenu d'une note existante",
        "parameters": {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "description": "URI de la note à lire"}
            },
            "required": ["uri"]
        }
        }
    },
    {        "type": "function",
        "function": {
        "name": "update_note",
        "description": "Met à jour le contenu d'une note existante",
        "parameters": {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "description": "URI de la note à modifier"},
                "new_content": {"type": "string", "description": "Nouveau contenu"}
            },
            "required": ["uri", "new_content"]
        }
        }
    },
    {        "type": "function",
        "function": {
        "name": "delete_note",
        "description": "Supprime (archive) une note",
        "parameters": {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "description": "URI de la note à supprimer"}
            },
            "required": ["uri"]
        }
        }
    },
    {        "type": "function",
        "function": {
        "name": "list_notes",
        "description": "Liste toutes les notes actives",
        "parameters": {"type": "object",
                     "properties": {
                "uri": {"type": "string", "description": "URI du container à lister"}
            },
            "required": ["uri"]}
    }
    }
]

# def call_function(name, args):
#     if name == "create_note":
#         uri = store.create_resource(args["title"], args["content"], tags=args.get("tags", ""))
#         return f"Note créée : {uri}"
#     elif name == "update_note":
#         version = store.update_resource(args["uri"], args["new_content"])
#         return f"Note mise à jour, nouvelle version : {version}"
#     elif name == "delete_note":
#         store.delete_resource(args["uri"])
#         return f"Note {args['uri']} supprimée (archivée)"
#     elif name == "list_notes":
#         # Implémenter la logique pour lister les notes actives (nécessite de parcourir le conteneur)
#         # Pour l'instant, on renvoie un message
#         return "Liste des notes : ..."
#     else:
#         return "Fonction inconnue"
def call_function(name, args):
    if name == "create_note":
        uri = store.create_note(args["title"], args["content"], tags=args.get("tags", ""))
        return f"Note créée : {uri}"
    elif name == "update_note":
        # adapter si update_note attend new_content et autres paramètres
        success = store.update_note(args["uri"], args["new_content"])
        return "Note mise à jour" if success else "Échec mise à jour"
    elif name == "delete_note":
        success = store.delete_note(args["uri"])
        return "Note supprimée" if success else "Échec suppression"
    elif name == "list_notes":
        notes = store.list_notes()
        # notes = store.list_notes(args["uri"])
        if notes:
            return "Notes trouvées :\n" + "\n".join(notes)
        else:
            return "Aucune note trouvée."
    else:
        return "Fonction inconnue"

print("Assistant prêt. Tapez votre question (ou 'quit' pour quitter).")
while True:
    user_input = input("\nVous: ").strip()
    if user_input.lower() in ('quit', 'exit'):
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    # Appel au LLM avec fonctions
    response = openai_client.chat.completions.create(
        model=chat_model,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Laissez le modèle décider
    )
    message = response.choices[0].message
    logger.info(message)

    # Vérifier si le modèle a demandé d'appeler une fonction
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        logger.info(f"Appel fonction {tool_name} avec args {arguments}")
        result = call_function(tool_name, arguments)
        logger.info(f"result {result}")
        # Ajouter la réponse de la fonction à la conversation
        messages.append(message)  # le message avec tool_call
        messages.append({
           "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": result
        })
        # Deuxième appel pour obtenir la réponse finale
        second_response = openai_client.chat.completions.create(
            model=chat_model,
            messages=messages
        )
        final_message = second_response.choices[0].message
        assistant_reply = final_message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        print(f"\nAssistant: {assistant_reply}")
    else:
        # Réponse directe
        assistant_reply = message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        print(f"\nAssistant: {assistant_reply}")

# # Dans la boucle de conversation, après avoir reçu la réponse du LLM, on vérifie s'il y a un appel de fonction
# # Exemple avec l'API OpenAI :
# response = openai_client.chat.completions.create(
#     model=chat_model,
#     messages=messages,
#     functions=functions,
#     function_call="auto"
# )

# logger.info(f"Réponse du LLM: {response.choices[0].message}")

# message = response.choices[0].message
# if message.tool_calls:
#     print("✅ Le modèle supporte le function calling !")
#     tool_call = message.tool_calls[0]
#     tool_name = message.tool_call.name
#     print(f"Outil appelé : {tool_name}")
#     arguments = json.loads(tool_call.function.arguments)
#     print(f"Arguments : {arguments}")
#     result = call_function(tool_name, arguments)
#     print("RESULT", result)
#     # Dans call_function, après avoir fait l'opération, on réindexe
#     #indexer.process_resource(uri, force=True)  # Il faudrait modifier process_resource pour accepter un flag force
#     # Envoyer le résultat au LLM pour qu'il génère une réponse finale
#     messages.append(message)  # message avec function_call
#     messages.append({
#         "role": "tool",
#         "tool_call_id": tool_call.id,
#         "name": tool_call.function.name,
#         "content": result
#     })
#     second_response = openai_client.chat.completions.create(
#         model=chat_model,
#         messages=messages
#     )
#     final_answer = second_response.choices[0].message.content
# else:
#     final_answer = message.content
# # print("test function_calling ", final_answer)



# print("Assistant prêt. Tapez votre question (ou 'quit' pour quitter).")
# while True:
#     user_input = input("\nVous: ").strip()
#     if user_input.lower() in ('quit', 'exit'):
#         break
#     if not user_input:
#         continue

#     messages.append({"role": "user", "content": user_input})

#     # Appel au LLM avec fonctions
#     response = openai_client.chat.completions.create(
#         model=chat_model,
#         messages=messages,
#         functions=functions,
#         function_call="auto"
#     )
#     message = response.choices[0].message

#     if message.function_call:
#         # L'assistant veut appeler une fonction
#         tool_name = message.function_call.name
#         arguments = json.loads(message.function_call.arguments)
#         logger.info(f"Appel fonction {tool_name} avec args {arguments}")
#         result = call_function(tool_name, arguments)
#         # Ajouter la réponse de la fonction à la conversation
#         messages.append(message)  # le message avec function_call
#         messages.append({
#             "role": "function",
#             "name": tool_name,
#             "content": result
#         })
#         # Deuxième appel pour obtenir la réponse finale
#         second_response = openai_client.chat.completions.create(
#             model=chat_model,
#             messages=messages
#         )
#         final_message = second_response.choices[0].message
#         assistant_reply = final_message.content
#         messages.append({"role": "assistant", "content": assistant_reply})
#         print(f"\nAssistant: {assistant_reply}")
#     else:
#         # Réponse directe
#         assistant_reply = message.content
#         messages.append({"role": "assistant", "content": assistant_reply})
#         print(f"\nAssistant: {assistant_reply}")