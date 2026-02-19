# import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

class ToolsInternalCommands:
    # def __init__(self, idp_url, client_id, client_secret):
        # self.idp_url = idp_url.rstrip('/')
        # self.client_id = client_id
        # self.client_secret = client_secret
        # self.access_token = None
        # self.token_expires_at = 0

        # # Créer la session HTTP en premier
        # self.session = requests.Session()

        # # Ensuite les autres initialisations
        # self._generate_dpop_key()
        # self._discover_endpoints()
        # self.userinfo_endpoint = None
        # self.webid = None
        # pformat(vars(self.session), indent=4, width=1)

    def process(self, args):
        # logger.setLevel(logging.INFO)
        print("internal command args", args)
        return f"OK, commande {args} executée .done"


    def debug_set_level(self, level):
        # https://blog.stephane-robert.info/docs/developper/programmation/python/logging/
        print("LOGGING set level", level) 
        logging.basicConfig(level=logging.CRITICAL)
        logger.info("done")

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self), indent=4, width=1)