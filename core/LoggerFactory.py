import logging
from logging.handlers import RotatingFileHandler


class LoggerFactory:
    def __init__(self, logger_name="assistant_core", logging_level=logging.DEBUG, log_file='logs/assistant_solid_indexer.log'):
        # Créer un logger et ajouter le handler
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging_level)

        # Configurer un RotatingFileHandler
        handler = RotatingFileHandler(
            log_file,  # Nom du fichier de log
            maxBytes=5000,  # Taille maximale du fichier en octets (ici, 5 Ko)
            backupCount=3  # Nombre de fichiers de sauvegarde
        )

        # Configurer le format et le niveau
        # https://blog.stephane-robert.info/docs/developper/programmation/python/logging/
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    # def logger():
    #     return self.logger
