set -x

export ANSIBLE_GATHERING=smart
export ANSIBLE_COMMAND_WARNINGS=False
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_FORCE_COLOR=1
export ANSIBLE_INVENTORY=$OPT_WORKDIR/hosts
export SSH_CONFIG=$OPT_WORKDIR/ssh.config.ansible
export ANSIBLE_SSH_ARGS="-F ${SSH_CONFIG}"

# to find roles/add-inventory-virthost
export ANSIBLE_ROLES_PATH=$(pwd)

# to find parts/kvm, parts/libvirt.
export ANSIBLE_ROLES_PATH=$ANSIBLE_ROLES_PATH:$(pwd)/../..

# to find the artib itself: ansible-role-tripleo-image-build itself
export ANSIBLE_ROLES_PATH=$ANSIBLE_ROLES_PATH:$(pwd)/../../..

export ANSIBLE_CALLBACK_PLUGINS=test_plugins/callback/profile_tasks
export ANSIBLE_CALLBACK_WHITELIST=profile_tasks
export PROFILE_TASKS_TIMELINE_SUMMARY=1


