from core.assistant import Assistant
import logging

# CONFIG
CONFIG={
    "tool_calls_limit": 6,
    "logger_name": "assistant_core",
    "logging_level": logging.INFO,
    "log_file": 'logs/assistant_solid_indexer.log',
    "collection_name":"mon_pod",
    "persist_directory":"./chroma_storage",
    "base_container":"http://localhost:3000/david/",
    "tools_definition": 'tools.json',
    "assistant_name": "Assistant",
    "premier_message": "Assistant prêt. Tapez votre question (ou 'quit' pour quitter), 'commande [params]' pour les commandes internes (cd, rm, ls, mkdir...), '/commande [params]' pour les commandes llm"
}

assistant = Assistant(CONFIG=CONFIG)
assistant.loop()

#
#  import logging
# from logging.handlers import RotatingFileHandler


# # CONFIG
# CONFIG={
#     "tool_calls_limit": 6,
#     "logger_name": "assistant_core",
#     "logging_level": logging.INFO,
#     "log_file": 'logs/assistant_solid_indexer.log',
#     "collection_name":"mon_pod",
#     "persist_directory":"./chroma_storage",
#     "base_container":"http://localhost:3000/david/",
#     "tools_definition": 'tools.json',
#     "assistant_name": "Assistant",
#     "premier_message": "Assistant prêt. Tapez votre question (ou 'quit' pour quitter), 'commande [params]' pour les commandes internes (cd, rm, ls, mkdir...), '/commande [params]' pour les commandes llm"
# }
# current_path = CONFIG['base_container']

# logging.basicConfig(level=CONFIG['logging_level'], format='%(asctime)s - %(levelname)s - %(message)s')
# handler = RotatingFileHandler(
#     CONFIG['log_file'],  # Nom du fichier de log
#     mode='a',
#     maxBytes=5*1024*1024, 
#     backupCount=3,
#     encoding=None,
#     delay=0
#     )
# # Configurer le format et le niveau
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# # Créer un logger et ajouter le handler
# logger = logging.getLogger(CONFIG['logger_name'])
# logger.setLevel(CONFIG['logging_level'])
# logger.addHandler(handler)

# # LOOP
# while True:
#     logger.debug(f"\n\n############# START NEW CONVERSATION LOOP ################################")
#     print(f"current_path: {current_path}")