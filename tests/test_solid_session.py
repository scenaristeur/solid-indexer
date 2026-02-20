# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')

from solid_auth import SolidAuthenticatedSession
import os
from dotenv import load_dotenv

load_dotenv()

session = SolidAuthenticatedSession(
    idp_url=os.getenv("SOLID_IDP_URL"),
    client_id=os.getenv("SOLID_CLIENT_ID"),
    client_secret=os.getenv("SOLID_CLIENT_SECRET")
)

# Tester une requête sur une ressource publique ou privée
resp = session.request('GET', 'http://localhost:3000/david/profile/card')
print(resp.status_code)
print(resp.text[:200])