import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import json
from openai import OpenAI

from solid_auth import SolidAuthenticatedSession
# from solid_versioned_store import SolidVersionedStore
# from core.LoggerFactory import LoggerFactory
from solid_crud_store import SolidCRUDStore
from solid_rag_query import SolidRAG
from solid_indexer import SolidIndexer
from tools.internal.commands import ToolsInternalCommands

load_dotenv()

# CONFIG
CONFIG={
    "tool_calls_limit": 6,
    "logger_name": "assistant_core",
    "logging_level": logging.DEBUG,
    "log_file": 'logs/assistant_solid_indexer.log',
    "collection_name":"mon_pod",
    "persist_directory":"./chroma_storage",
    "base_container":"http://localhost:3000/david/notes/"
}

# LOGGER
# Configuration basique du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exemples de messages de log
# logging.debug("Ceci est un message de débogage.")
# logging.info("Ceci est un message d'information.")
# logging.warning("Ceci est un message d'avertissement.")
# logging.error("Ceci est un message d'erreur.")
# logging.critical("Ceci est un message critique.")
# Configurer un RotatingFileHandler
handler = RotatingFileHandler(
    CONFIG['log_file'],  # Nom du fichier de log
    maxBytes=5000,  # Taille maximale du fichier en octets (ici, 5 Ko)
    backupCount=3  # Nombre de fichiers de sauvegarde
)

# # Configurer le format et le niveau
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)



# https://betterstack.com/community/questions/how-to-color-python-logging-output/
# class CustomFormatter(logging.Formatter):
#     grey = "\\x1b[38;21m"
#     yellow = "\\x1b[33;21m"
#     red = "\\x1b[31;21m"
#     bold_red = "\\x1b[31;1m"
#     reset = "\\x1b[0m"
#     format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.INFO: grey + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#         logging.CRITICAL: bold_red + format + reset
#     }

#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)
# handler = logging.StreamHandler()
# handler.setFormatter(CustomFormatter())

# Créer un logger et ajouter le handler
logger = logging.getLogger(CONFIG['logger_name'])
logger.setLevel(CONFIG['logging_level'])
logger.addHandler(handler)

# Exemple de messages de log
# logger.debug("Log de débogage")
# logger.info("Log d'information")
# logger.warning("Log d'avertissement")


logging.info("[MAIN] - ******************************************NEW SESSION**************************************")
# # https://blog.stephane-robert.info/docs/developper/programmation/python/logging/
# #logger = LoggerFactory(log_file=CONFIG['log_file'], logging_level=CONFIG['logging_level'], logger_name=CONFIG['logger_name']).logger
# logging.basicConfig(level=CONFIG['logging_level'], format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(CONFIG['logger_name'])
# # Configurer un RotatingFileHandler
# handler = RotatingFileHandler(
#         CONFIG['log_file'],  # Nom du fichier de log
#         maxBytes=5000,  # Taille maximale du fichier en octets (ici, 5 Ko)
#         backupCount=3  # Nombre de fichiers de sauvegarde
#     )
# # Configurer le format et le niveau
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# # Configure logging to show info but suppress noisy libraries
# # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# # logging.getLogger("solid_auth").setLevel(logging.WARNING)


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
with open('tools.json') as f:
    tools = json.load(f)

# PROMPTS
system_prompt = f"""Tu es un assistant personnel qui gère des notes sur un pod Solid.
Tu as accès à des fonctions pour créer, modifier, supprimer et lister des notes.
Le container de base est : {CONFIG['base_container']}
Lorsque l'utilisateur te demande de créer une note, tu DOIS utiliser la fonction 'create_note'.
N'écris pas de longs discours : utilise les fonctions pour agir directement.
Par exemple, si l'utilisateur dit "crée une note sur le projet", appelle create_note avec un titre et un contenu appropriés.
Pour rechercher dans le contenu des notes, utilise la fonction retrieve.
Ne donne pas de conseils sur la façon de créer une note : crée-la réellement via la fonction.
"""
messages = [{"role": "system", "content": system_prompt}]


# MAIN
logging.info("[MAIN] - ******************************************NEW SESSION**************************************")
logging.info("f[CONFIG] {config}")



def call_function(name, args):
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
        success = indexer.run(base_container)
        return "Notes indexes" if success else "Échec index"
    else:
        return "Fonction inconnue"

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



print("Assistant prêt. Tapez votre question (ou 'quit' pour quitter), ':commande [params]' pour les commandes internes, '/commande [params]' pour les commandes llm")
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
        print(f"\nAssistant: {assistant_reply}")

