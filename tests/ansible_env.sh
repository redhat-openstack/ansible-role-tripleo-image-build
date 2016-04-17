export ANSIBLE_GATHERING=smart
export ANSIBLE_COMMAND_WARNINGS=False
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_FORCE_COLOR=1
export ANSIBLE_INVENTORY=$OPT_WORKDIR/hosts
export SSH_CONFIG=$OPT_WORKDIR/ssh.config.ansible
export ANSIBLE_SSH_ARGS="-F ${SSH_CONFIG}"

# to find role: ansible-role-tripleo-image-build
export ANSIBLE_ROLES_PATH=$(pwd)/../..

# to find role: add-inventory-virthost
export ANSIBLE_ROLES_PATH=$ANSIBLE_ROLES_PATH:$(pwd)/.




