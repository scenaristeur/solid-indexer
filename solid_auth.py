import requests
import base64
import json
import time
import os
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from jose import jwt
from jose.constants import ALGORITHMS
from pprint import pformat
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SolidAuthenticatedSession:
    def __init__(self, idp_url, client_id, client_secret):
        self.idp_url = idp_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0

        # Créer la session HTTP en premier
        self.session = requests.Session()

        # Ensuite les autres initialisations
        self._generate_dpop_key()
        self._discover_endpoints()
        self.userinfo_endpoint = None
        self.webid = None
        # pformat(vars(self.session), indent=4, width=1)


    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self), indent=4, width=1)

    def _generate_dpop_key(self):
        """Génère une paire de clés RSA pour DPoP et prépare le JWK."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

        # Exporter la clé privée au format PEM pour jose
        self.dpop_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # Construire le JWK (clé publique) pour l'en-tête DPoP
        numbers = self.public_key.public_numbers()
        self.jwk = {
            "kty": "RSA",
            "n": base64.urlsafe_b64encode(
                numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, 'big')
            ).decode('utf-8').rstrip("="),
            "e": base64.urlsafe_b64encode(
                numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, 'big')
            ).decode('utf-8').rstrip("="),
            "alg": "RS256",
            "use": "sig"
        }

    def _discover_endpoints(self):
        """Découvre le token_endpoint via OpenID Configuration."""
        well_known = f"{self.idp_url}/.well-known/openid-configuration"
        resp = self.session.get(well_known)
        resp.raise_for_status()
        config=resp.json()
        # print(config)
        self.token_endpoint = config['token_endpoint']
        self.userinfo_endpoint = config['authorization_endpoint']

    def _create_dpop_header(self, method, url, ath=None):
        """
        Crée un en-tête DPoP JWT conforme à la spécification.
        - method: HTTP method (GET, POST, etc.)
        - url: URL complète de la requête
        - ath: optionnel, hash du token d'accès
        """
        now = int(time.time())
        payload = {
            "jti": os.urandom(16).hex(),  # identifiant unique
            "htm": method,
            "htu": url,
            "iat": now,
            "exp": now + 120,  # expiration courte (2 minutes)
        }
        if ath:
            payload["ath"] = ath

        # En-tête avec les champs requis
        headers = {
            "typ": "dpop+jwt",
            "alg": "RS256",
            "jwk": self.jwk
        }

        # Signer le JWT avec la clé privée
        signed = jwt.encode(
            payload,
            self.dpop_key_pem,
            algorithm=ALGORITHMS.RS256,
            headers=headers
        )
        return signed

    def _get_access_token(self):
        """Échange les client credentials contre un access token avec DPoP."""
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()

        dpop = self._create_dpop_header('POST', self.token_endpoint)

        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DPoP': dpop,
        }
        body = 'grant_type=client_credentials&scope=webid'

        resp = self.session.post(self.token_endpoint, data=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # print(data)
        self.access_token = data['access_token']
        # Expiration : on retire 60 secondes pour avoir une marge
        self.token_expires_at = time.time() + data.get('expires_in', 3600) - 60
        #self._fetch_webid()

    def _compute_ath(self):
        """Calcule le hash SHA-256 du token d'accès (pour l'en-tête DPoP des requêtes)."""
        if not self.access_token:
            return None
        digest = hashlib.sha256(self.access_token.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    def request(self, method, url, **kwargs):
        """
        Effectue une requête HTTP authentifiée avec DPoP.
        Utilise automatiquement un token valide (renouvelé si nécessaire).
        """
        if not self.access_token or time.time() > self.token_expires_at:
            self._get_access_token()

        # Calculer l'ath (hash du token) pour cette requête
        ath = self._compute_ath()
        dpop = self._create_dpop_header(method, url, ath=ath)

        headers = kwargs.pop('headers', {})
        headers.update({
            'Authorization': f'DPoP {self.access_token}',
            'DPoP': dpop,
        })

        return self.session.request(method, url, headers=headers, **kwargs)

    def _fetch_webid(self):
        """Interroge l'endpoint userinfo pour obtenir le WebID."""
        if not self.userinfo_endpoint:
            logger.warning("Pas d'endpoint userinfo, impossible de récupérer le WebID")
            return
        # Utiliser le token courant pour une requête authentifiée
        headers = {'Authorization': f'DPoP {self.access_token}'}
        dpop = self._create_dpop_header('GET', self.userinfo_endpoint, ath=self._compute_ath())
        headers['DPoP'] = dpop
        resp = self.session.get(self.userinfo_endpoint, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # Le WebID est généralement dans le champ "sub" ou "webid"
            self.webid = data.get('webid') or data.get('sub')
            logger.info(f"WebID récupéré : {self.webid}")
        else:
            logger.error(f"Échec userinfo: {resp.status_code}")

    def get_webid(self):
        """Retourne le WebID, le récupère si nécessaire."""
        if not self.webid:
            self._fetch_webid()
        return self.webid