#!/usr/bin/env bash

if [ -z "$VIRTHOST" ]; then
    echo "ERROR: You must export VIRTHOST"
fi

set -x

ansible-playbook -vv test.yml -e virthost=$VIRTHOST \
    -e ansible_python_interpreter=/usr/bin/python \
    -e virt_sparsify_checktmpdir_flag=continue



