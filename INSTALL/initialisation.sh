#!/usr/bin/env bash

ROOT_FOLDER=$HOME/.solid-indexer
DATA_FOLDER=$ROOT_FOLDER/data
ENV_FILE=${ROOT_FOLDER}/.env

echo "Starting Solid community Server in another terminal window (if not see INSTALL.md)"
# community-solid-server -c @css:config/file.json -f ${DATA_FOLDER}
# run command in another terminal https://askubuntu.com/questions/484993/run-command-on-anothernew-terminal-window
gnome-terminal -- sh -c "bash -c \"community-solid-server -c @css:config/file.json -f ${DATA_FOLDER}; exec bash\""


echo "Solid community Server is running in another terminal window"
echo "Wait for Solid Community Server to be ready, when it says 'Listening to server at http://localhost:3000/'"
echo -e "\nIn the next step, you will register a ACCOUNT, create a POD to store your data, and create a TOKEN to allow apps to act on your POD and store it in ${ENV_FILE}"
echo -e "Two new html pages ansd a new terminal will open :\n\t- http://localhost:3000/.account/login/password/register/ to register your account.\n\t- ./INSTALLATION/initialisation.html to guide you through the process"
echo "copy TOKEN_IDENTIFIER and TOKEN_SECRET and past them in ${ENV_FILE}/"


read -p "Press enter to continue"
open "http://localhost:3000/.account/login/password/register/" &
open ./INSTALL/initialisation.html &

gnome-terminal -- sh -c "bash -c \"\"${EDITOR:-vi}\" ${ENV_FILE}; exec bash\""
