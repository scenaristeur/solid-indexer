# automated install with ansible

- install ansible https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html

```
# python3 -m pip install --user ansible
python3 -m pip install ansible
```

## run installer

```
ansible-playbook ./INSTALL/0-install-prereq.yml -v
ansible-playbook ./INSTALL/1-install.yml --ask-become-pass -v

```

# Initialisation

```
./INSTALL/initialisation.sh
```

- create a Solid Account, create a Solid Pod, create a TOKEN_IDENTIFIER and a TOKEN_SECRET and paste them in DATA_FOLDER=$HOME/.solid-indexer
- [initialisation-walkthrough](INSTALL/initialisation.html)
- [register](http://localhost:3000/.account/login/password/register/)
- copy & paste TOKEN_IDENTIFIER & TOKEN_SECRET in $HOME/.solid-indexer/.env

# Start and enjoy !

```
cd /opt/solid-indexer
. .venv/bin/activate
./assistant.sh

```

<!-- ./start.sh -->
