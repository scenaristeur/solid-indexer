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