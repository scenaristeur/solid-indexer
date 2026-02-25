# n8n pour lecture/ecriture de fichier, avec volume shared

```
docker run -it --rm \
    --name n8n \
    -p 5678:5678 \
    -e GENERIC_TIMEZONE="Europe/Paris" \
    -e TZ="Europe/Paris" \
    -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
    -e WEBHOOK_TUNNEL_URL=https://endamoebic-ardell-tonetically.ngrok-free.dev \
    -e N8N_RUNNERS_ENABLED=true \
    -e NODES_EXCLUDE=[] \
    -v n8n_data:/home/node/.n8n \
    -v $HOME/shared:/home/node/.n8n-files \
    docker.n8n.io/n8nio/n8n
```

dossier partagé dans le container : -v $HOME/shared:/home/node/.n8n-files
