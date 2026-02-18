import os
import logging
from dotenv import load_dotenv
from solid_auth import SolidAuthenticatedSession
from solid_crud_store import SolidCRUDStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def test_crud():
    session = SolidAuthenticatedSession(
        idp_url=os.getenv("SOLID_IDP_URL"),
        client_id=os.getenv("SOLID_CLIENT_ID"),
        client_secret=os.getenv("SOLID_CLIENT_SECRET")
    )
    webid = "http://localhost:3000/david/profile/card#me"  # À adapter si nécessaire
    base = "http://localhost:3000/david/test_solid_store6/"

    store = SolidCRUDStore(session, base, webid)

    # 0. Supprimer
    logger.info("Suppression...")
    ok = store.delete_note(base)
    if ok:
        logger.info("Suppression réussie")
    else:
        logger.error("Échec suppression")

    # 1. Créer une note
    logger.info("Création d'une note...")
    uri = store.create_note("ma-note", "Ceci est une note de test.", tags="test, demo")
    if not uri:
        logger.error("Échec création")
        return
    logger.info(f"URI créée: {uri}")

    # 2. Lire la note
    logger.info("Lecture de la note...")
    note = store.read_note(uri)
    if note:
        logger.info(f"Contenu: {note}")
    else:
        logger.error("Lecture échouée")
        return

    # 3. Mettre à jour
    logger.info("Mise à jour...")
    ok = store.update_note(uri, "Nouveau contenu après mise à jour.", tags="test, demo, update")
    if ok:
        logger.info("Mise à jour réussie")
    else:
        logger.error("Échec mise à jour")
        return

    # 4. Lire à nouveau
    note2 = store.read_note(uri)
    logger.info(f"Après mise à jour: {note2}")

    # 5. Supprimer
    logger.info("Suppression...")
    ok = store.delete_note(uri)
    if ok:
        logger.info("Suppression réussie")
    else:
        logger.error("Échec suppression")

if __name__ == "__main__":
    test_crud()