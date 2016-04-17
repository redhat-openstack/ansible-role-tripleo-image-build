export ANSIBLE_GATHERING=smart
export ANSIBLE_COMMAND_WARNINGS=False
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_FORCE_COLOR=1
export ANSIBLE_INVENTORY=$OPT_WORKDIR/hosts
export SSH_CONFIG=$OPT_WORKDIR/ssh.config.ansible
export ANSIBLE_SSH_ARGS="-F ${SSH_CONFIG}"

# to find add-inventory.virthost
export ANSIBLE_ROLES_PATH=$(pwd)

# to find role: parts/kvm, parts/libvirt.  for some reason when pulled in directly by build_default_images.yml they need to be found this way
export ANSIBLE_ROLES_PATH=$ANSIBLE_ROLES_PATH:$(pwd)/..

# to find role: ansible-role-tripleo-image-build itself
export ANSIBLE_ROLES_PATH=$ANSIBLE_ROLES_PATH:$(pwd)/../..

export ANSIBLE_CALLBACK_PLUGINS=test_plugins/callback/profile_tasks
export ANSIBLE_CALLBACK_WHITELIST=profile_tasks
export PROFILE_TASKS_TIMELINE_SUMMARY=1


