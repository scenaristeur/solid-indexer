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
