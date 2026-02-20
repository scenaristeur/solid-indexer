import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import json
from openai import OpenAI

from solid_auth import SolidAuthenticatedSession
from solid_crud_store import SolidCRUDStore
from solid_rag_query import SolidRAG
from solid_indexer import SolidIndexer
from tools.internal.commands import ToolsInternalCommands

load_dotenv()

# CONFIG
CONFIG={
    "tool_calls_limit": 6,
    "logger_name": "assistant_core",
    "logging_level": logging.INFO,
    "log_file": 'logs/assistant_solid_indexer.log',
    "collection_name":"mon_pod",
    "persist_directory":"./chroma_storage",
    "base_container":"http://localhost:3000/david/notes/",
    "tools_definition": 'tools.json',
    "assistant_name": "Assistant",
    "premier_message": "Assistant prêt. Tapez votre question (ou 'quit' pour quitter), ':commande [params]' pour les commandes internes, '/commande [params]' pour les commandes llm"
}

# LOGGER
# Configuration basique du logger
# https://blog.stephane-robert.info/docs/developper/programmation/python/logging/
# https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
# https://sametmax.oprax.fr/lencoding-en-python-une-bonne-fois-pour-toute.html
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler(
    CONFIG['log_file'],  # Nom du fichier de log
    mode='a',
    maxBytes=5*1024*1024, 
    backupCount=3,
    encoding=None,
    delay=0
    )
# Configurer le format et le niveau
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Créer un logger et ajouter le handler
logger = logging.getLogger(CONFIG['logger_name'])
logger.setLevel(CONFIG['logging_level'])
logger.addHandler(handler)
# DEBUG BY MODULE
logging.getLogger('solid_auth').setLevel(logging.INFO)
logging.getLogger('solid_indexer').setLevel(logging.DEBUG)

# MODULES
indexer = SolidIndexer(collection_name=CONFIG['collection_name'], persist_directory=CONFIG['persist_directory'])
rag = SolidRAG(collection_name=CONFIG['collection_name'], persist_directory=CONFIG['persist_directory'])
session = SolidAuthenticatedSession(
    idp_url=os.getenv("SOLID_IDP_URL"),
    client_id=os.getenv("SOLID_CLIENT_ID"),
    client_secret=os.getenv("SOLID_CLIENT_SECRET")
)
store = SolidCRUDStore(session, base_container=CONFIG['base_container'], webid=session.webid)
# Client OpenAI
openai_client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
chat_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
til = ToolsInternalCommands()

# LOAD TOOLS
with open(CONFIG['tools_definition']) as f:
    tools = json.load(f)

# PROMPTS
system_prompt = f"""Tu es un assistant personnel qui gère des notes sur un pod Solid.
Tu as accès à des fonctions pour créer, modifier, supprimer et lister des notes.
Le container de base est : {CONFIG['base_container']}
Lorsque l'utilisateur te demande de créer une note, tu DOIS utiliser la fonction 'create_note'.
N'écris pas de longs discours : utilise les fonctions pour agir directement.
Par exemple, si l'utilisateur dit "crée une note sur le projet", appelle create_note avec un titre et un contenu appropriés.
Pour rechercher dans le contenu des notes, utilise la fonction retrieve.
Pou
Ne donne pas de conseils sur la façon de créer une note : crée-la réellement via la fonction.
"""
messages = [{"role": "system", "content": system_prompt}]


# MAIN

logger.debug(f"[CONFIG] {json.dumps(CONFIG, indent=4)}")
logger.debug(f"[TOOLS] {json.dumps(tools, indent=4)}")
logger.debug(f"[SYSTEM_PROMPT] {json.dumps(system_prompt, indent=4)}")
logger.debug("_________________________________NEW SESSION__________________________")



def call_function(name, args):
    try: 
        if name == "create_note":
            uri = store.create_note(args["title"], args["content"], tags=args.get("tags", ""))
            return f"Note créée : {uri}"
        elif name == "read_note":
            content = store.read_note(args["uri"])
            return json.dumps(content) if content else "Échec suppression"
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
        elif name == "retrieve":
            context = rag.retrieve(args["query"])
            
            # Convertir le contexte en format texte lisible
            if context:
                context_text = "\n\n---\n\n".join(
                    f"Document (source: {item[1]['uri']}):\n{item[0]}"
                    for item in context
                )
                return context_text
        elif name == "index":
            success = indexer.run(CONFIG['base_container'])
            return "Notes indexes" if success else "Échec index"
        else:
            return "Fonction inconnue"
    except Exception as e:
        # logger.debug(f"******* ERREUR CALL_LLM\n{e}\n**********\n")
        # logger.error(f"Erreur call_llm: {e}")
        logger.error("Une erreur est survenue dans call_function", exc_info=True)
        return True, tool_calls, e

def call_llm(messages, tool_calls):
# Appel au LLM avec fonctions
    logger.debug(f"########################### START NEW CALL_LLM with tool_calls already done = { tool_calls}")
    # logger.debug(f"******* TOOLS\n{ json.dumps(tools, indent=4)}\n**********\n")
    logger.debug(f"******* MESSAGES\n{messages}\n**********\n")
    try : 
        response = openai_client.chat.completions.create(
            model=chat_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",  # Laissez le modèle décider
        )
        logger.debug(f"******* RESPONSE\n{response}\n**********\n")
        message = response.choices[0].message
        logger.debug(f"********** RESPONSE MESSAGE\n{message}\n**********\n")

        if message.tool_calls:
            logger.debug(f"******* message.tool_calls True")
            tool_calls+=1
            logger.info(f"[TOOL CALL]: {tool_calls}")
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            logger.info(f"Appel fonction {tool_name} avec args {arguments}")
            result = call_function(tool_name, arguments)
            logger.debug(f"********** TOOL_CALL RESULT\n{result}\n**********\n")
            # Ajouter la réponse de la fonction à la conversation
            messages.append(message)  # le message avec tool_call
            messages.append({
            "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result
            })
            logger.debug(f"******* MESSAGES AFTER TOOL_CALL\n{messages}\n**********\n")
            return False, tool_calls, message
        else:
            # Réponse directe
            logger.debug(f"******* REPONSE DIRECTE message.tool_calls False")
            return True, tool_calls, message
    except Exception as e:
        # logger.debug(f"******* ERREUR CALL_LLM\n{e}\n**********\n")
        # logger.error(f"Erreur call_llm: {e}")
        logger.error("Une erreur est survenue dans call_llm", exc_info=True)
        return True, tool_calls, e



print(CONFIG['premier_message'])
logger.debug(CONFIG['premier_message'])
while True:
    logger.debug(f"\n\n############# START NEW CONVERSATION LOOP ################################")
    user_input = input("\nVous: ").strip()
    logger.debug(f"\n******\n USER_INPUT\n{user_input}\n******\n")
    if user_input.lower() in ('quit', 'exit'):
        break
    elif user_input.startswith(':'):
        logger.info("TODO: commandes internes : cd, ls, mkdir...")
        internal_command_result = til.process({"user_input": user_input})
        continue
    elif user_input.startswith(':'):
        logger.info("TODO: commandes llm (enchaine comande + llm)...")
    if not user_input:
        continue

    if len(user_input) > 0:
        messages.append({"role": "user", "content": user_input})
        tool_calls = 0
        done = False
        while done is not True and tool_calls < CONFIG['tool_calls_limit']:
            result = call_llm(messages= messages, tool_calls=tool_calls)
            logger.debug(f"CALL_LLM_RESULT with done boolean, tool_calls counter and assistant reply: {result}")
            done, tool_calls, message = result
            logger.debug(f"DONE: {done}")
            logger.debug(f"TOOL_CALLS_AFTER: {tool_calls}")

        assistant_reply = message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        print(f"{CONFIG['assistant_name']}: {assistant_reply}")
        logger.debug(f"{CONFIG['assistant_name']}: {assistant_reply}")

