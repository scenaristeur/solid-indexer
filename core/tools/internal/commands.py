import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ToolsInternalCommands:
    def __init__(self):
        self.commands = ['cd', 'ls', 'mkdir', 'rm']
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
        # print("internal command args", args)
        user_input = args['user_input']
        user_input= user_input.strip()
        logger.debug(f"user_input : {user_input}")
        match user_input.split(' ', 1)[0]: # first word without first char (:)
            case 'cd':
                return self._cd(args)
            case 'ls':
                return "not implemented yet ls"
            case 'mkdir':
                return "not implemented yet mkdir"

            # If an exact match is not confirmed, this last case will be used if provided
            case _:
                return "Something's wrong with the user_input"
        return f"OK, commande {args} executée .done"

    def _cd(self, args):
        logger.debug(f"change directory {args}")
        if len(args['user_input'].split(' ', 1)) == 1:
            return {"current_path": args['base_container']}
        relative_path=args['user_input'].split(' ', 1)[1]
        logger.debug(f"relative_path {relative_path}")
        match relative_path:
            case "..":
                print(f"remonte")
                path= self.remove_last_folder(args['current_path'])
                logger.debug(f"path {path}")
                return {"current_path": path}
            case "-":
                print(f"precedent")  # Match weekdays
                return {}
            case _:
                path=args['current_path']+relative_path+"/"
                return {"current_path": path}



    # def commands(self):
    #     return self.commands


    def debug_set_level(self, level):
        # https://blog.stephane-robert.info/docs/developper/programmation/python/logging/
        print("LOGGING set level", level) 
        logging.basicConfig(level=logging.CRITICAL)
        logger.info("done")

    def remove_last_folder(self, url: str) -> str:
        """
        Retourne l'URL en supprimant uniquement le dernier dossier du chemin.
        Exemple :  http://localhost:3000/david/notes/test/ → http://localhost:3000/david/notes/
        """
        # 1️⃣ Normaliser : on s'assure que l'URL se termine par un '/' (facilite le traitement)
        if not url.endswith('/'):
            url += '/'

        # 2️⃣ Retirer ce '/' temporairement pour pouvoir repérer le dernier dossier
        trimmed = url.rstrip('/')          # → ".../david/notes/test"

        # 3️⃣ Position du slash qui précède le dernier dossier
        last_slash = trimmed.rfind('/')    # index du '/' avant « test »

        # 4️⃣ Conserver tout jusqu’à ce slash (incluant le slash) → chemin sans le dernier dossier
        new_url = trimmed[:last_slash + 1]  # → ".../david/notes/"

        return new_url

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self), indent=4, width=1)