# Assistant Solid

- lancement d'un serveur Solid Community Serveur servant de base de connaissance où sont stockées les données.

```
npm install -g @solid/community-server
community-solid-server -c @css:config/file.json -f data/
```

- login : http://localhost:3000/.account/login/password/
- Pod : create Pod
- Credential Token : create token, creation d'un token et enregistrement dans .env
- noter SOLID_CLIENT_ID et SOLID_CLIENT_SECRET dans .env avec les Token_identifier et Token_secret fournis

.env

```

# SOLID
SOLID_CLIENT_ID=my_token_d8575642-25b7-4386-9695-d6c08a9de45e
SOLID_CLIENT_SECRET=f73fc9db8b2649f75fe814beb60a378c8g6d5bbdd515b4d7153cc21c0eb7dfc703ebd38c2ad333d82985b964087276d2f2a3b6c92b08e1b83210160a9c1a8d6c
#SOLID_EMAIL="user@mymail.com"
#SOLID_PASSWORD="mypassword"
#SOLID_ENDPOINT="http://localhost:3000"
SOLID_IDP_URL=http://localhost:3000

# LLM
OPENAI_API_KEY=sk-my_api_key
OPENAI_BASE_URL="https://my_llm_provider/v1"
CHAT_MODEL=provider/MyModel-3-8B-Instruct-2512

```

```

python -m venv .venv
. .venv/bin/activate
python install -r requirements.txt
python solid_rag_query_crud_function_calling.py

```

# utilisation

- avec llm (OPENAI_API_KEY décommenté dans .env)

```

:~/dev/solid-indexer$ python solid_rag_query_crud_function_calling.py
2026-02-19 06:53:58,879 - INFO - CRUD Store initialisé avec base: http://localhost:3000/david/notes/
Assistant prêt. Tapez votre question (ou 'quit' pour quitter).

Vous: créons une note Todo1 , avec 1 Appeler Paul, 2 Sortir le chien, 3 acheter des fruits
2026-02-19 06:54:39,096 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 06:54:39,254 - INFO - Création du conteneur http://localhost:3000/david/notes/
2026-02-19 06:54:39,316 - INFO - ✅ Conteneur http://localhost:3000/david/notes/ créé
2026-02-19 06:54:39,387 - INFO - ✅ ACL créé pour http://localhost:3000/david/notes/
2026-02-19 06:54:40,450 - INFO - ✅ Note créée : http://localhost:3000/david/notes/todo1.ttl
2026-02-19 06:54:40,450 - INFO - result Note créée : http://localhost:3000/david/notes/todo1.ttl

Assistant: La note **Todo1** a été créée avec succès :
🔗 [http://localhost:3000/david/notes/todo1.ttl](http://localhost:3000/david/notes/todo1.ttl)

Vous:

```

-> note consultable sur http://localhost:3000/david/notes/todo1.ttl avec le contenu :

```
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ns1: <http://example.org/ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://localhost:3000/david/notes/todo1.ttl> a ns1:Note ;
    ns1:content """1. Appeler Paul
2. Sortir le chien
3. Acheter des fruits""" ;
    ns1:tags "" ;
    dcterms:created "2026-02-19T05:54:40.389634+00:00"^^xsd:dateTime .

```

## fonctionnalité CRUD :

- [exemple d'utilisation (EXEMPLE.md)](EXEMPLE.md)

# solid token generation& AUTH

- https://communitysolidserver.github.io/CommunitySolidServer/5.x/usage/client-credentials/

```

~/dev/solid-indexer$ python solid_indexer.py http://localhost:3000/david/
2026-02-18 13:20:28,002 - INFO - Anonymized telemetry enabled. See https://docs.trychroma.com/telemetry for more information.
2026-02-18 13:20:28,193 - INFO - Démarrage de l'indexation depuis http://localhost:3000/david/
2026-02-18 13:20:28,193 - INFO - Traitement de http://localhost:3000/david/ (profondeur 0)
2026-02-18 13:20:28,193 - INFO - Traitement de http://localhost:3000/david/ (profondeur 0)
2026-02-18 13:20:28,437 - INFO - Listage du conteneur http://localhost:3000/david/

```

# test retrieve / query

> sans llm : commenter la ligne OPENAI_API_KEY dans .env
> commenter la ligne OPENAI_API_KEY dans .env
> avec llm : décommenter la ligne OPENAI_API_KEY dans .env

- indexer : `python solid_indexer.py http://localhost:3000`
- retriever : `python solid_rag_query.py`

# log

avec log.txt

`python solid_indexer.py http://localhost:3000/david/ > log.txt 2>&1`

python solid_indexer.py http://localhost:3000/david/ > output.txt 2> error.txt

# discussion

- https://chat.deepseek.com/a/chat/s/5ef0514f-a99e-4f72-882c-4160a4a8dd75

# FUNCTION CALLING

[

](test_function_calling_model.py)

- mistralai/Ministral-3-8B-Instruct-2512 ok
- openai/gpt-oss-120b : ok
- mistralai/Mistral-Small-3.2-24B-Instruct-2506 : Extra inputs are not permitted

# solid-client-credential-py

- https://github.com/Otto-AA/solid-client-credentials-py/
- https://github.com/Otto-AA/solid-oidc-py

# test index/retrieve
