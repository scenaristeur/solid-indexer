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

Token identifier: dummy_token_71f3105e-8a1a-4018-bea6-4fb251720ecd
Token secret: 07d04c47e2d0c2619aac30b80383cc7dbd5fc5eb9f1c184b87ae7f7cecddd2908a77e93d6514181767ab9d2fbfc4b175e09109a150cc2e615a26dd53c81578ff

- create a Solid Account, create a Solid Pod, create a TOKEN_IDENTIFIER and a TOKEN_SECRET and paste them in DATA_FOLDER=$HOME/.solid-indexer
- [initialisation-walkthrough](INSTALL/initialisation.html)

# Start and enjoy !

```
./start.sh
```
