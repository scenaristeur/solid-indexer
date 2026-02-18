npm install -g @solid/community-server
community-solid-server -c @css:config/file.json -f data/ --baseUrl http://192.168.1.107:3000

```
python -m venv .venv
. .venv/bin/activate
python install -r requirements.txt

```

# solid token generation& AUTH

- https://communitysolidserver.github.io/CommunitySolidServer/5.x/usage/client-credentials/

```
~/dev/solid-indexer$ python solid_indexer.py http://localhost:3000/david/
2026-02-18 13:20:28,002 - INFO - Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2026-02-18 13:20:28,193 - INFO - Démarrage de l'indexation depuis http://localhost:3000/david/
2026-02-18 13:20:28,193 - INFO - Traitement de http://localhost:3000/david/ (profondeur 0)
2026-02-18 13:20:28,193 - INFO - Traitement de http://localhost:3000/david/ (profondeur 0)
2026-02-18 13:20:28,437 - INFO - Listage du conteneur http://localhost:3000/david/

```

# query

## sans llm

`python solid_rag_query.py`

## avec llm

dans .env

```
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=votre_clé
CHAT_MODEL=gpt-3.5-turbo
`python solid_rag_query.py`

```

# log

avec log.txt

`python solid_indexer.py http://localhost:3000/david/ > log.txt 2>&1`

python solid_indexer.py http://localhost:3000/david/ > output.txt 2> error.txt

# discussion

- https://chat.deepseek.com/a/chat/s/5ef0514f-a99e-4f72-882c-4160a4a8dd75
