import logging
from logging.handlers import RotatingFileHandler
from core.tools.internal.commands import ToolsInternalCommands

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

til = ToolsInternalCommands()

class Assistant:
    def __init__(self, CONFIG):
        # Créer un logger et ajouter le handler
        self.CONFIG = CONFIG
        self.current_path = CONFIG['base_container']
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
        # self.logger = logging.getLogger(logger_name)
        # self.logger.setLevel(logging_level)
    
    def loop(self):
        print(f"\n{self.CONFIG['premier_message']}")
        logger.debug(self.CONFIG['premier_message'])
        while True:
            logger.debug(f"\n\n############# START NEW CONVERSATION LOOP ################################")
            print(f"current_path: {self.current_path}")
            user_input = input("\nVous: ").strip()
            logger.debug(f"\n******\n USER_INPUT\n{user_input}\n******\n")
            if user_input.lower() in ('quit', 'exit'):
                break
            elif user_input.split(' ', 1)[0] in til.commands:
                # logger.info("TODO: commandes internes : cd, ls, mkdir...")
                base_container=self.CONFIG['base_container']
                internal_command_result = til.process({"user_input": user_input, "current_path": self.current_path, "base_container": base_container})
                current_path = internal_command_result.get('current_path', current_path)
                continue
            elif user_input.startswith(':'):
                logger.info("TODO: commandes llm (enchaine comande + llm)...")
            if not user_input:
                continue

            if len(user_input) > 0:
                messages.append({"role": "user", "content": f"Le dossier courant est : {current_path}\n"+user_input})
                logger.debug(messages[-1]) 