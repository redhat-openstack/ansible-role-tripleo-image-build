#!/usr/bin/python
# coding: utf-8 -*-

# this module is based directly on the script of the
# same name in openstack/tripleo-common/scripts

DOCUMENTATION = '''
---
module: tripleo_build_images
version_added: "2.0.1"
short_description: Build a TripleO overcloud image from a list of yaml definitions
description:
   - Build a TripleO overcloud image from a list of yaml definitions.
'''
from tripleo_common.image.build import ImageBuildManager

def tripleo_build_images(config_files, output_directory, skip):

    try:
        # (trown) the tripleo-common dib builder spews to stdout/stderr,
        # which makes the results file not work for async.
        # We have to fix that in tripleo-common... I tried various means to use mock
        # as a hack, but no luck. The patch to tripleo-common should be pretty
        # straight-forward though.
        manager = ImageBuildManager(config_files,
                                    output_directory=output_directory,
                                    skip=skip)
        manager.build()
    except Exception as e:
        return ('Fail', e.args)

    return ('Success', '')

def main():
    module = AnsibleModule(
        argument_spec=dict(
            config_files=dict(required=True, type='list'),
            output_directory=dict(required=True),
            skip=dict(required=False, default=False, type='bool')
        )
    )
    result = tripleo_build_images(module.params["config_files"],
                                  module.params["output_directory"],
                                  module.params["skip"])

    if result[0] == 'Fail':
        module.fail_json(msg=' '.join(result[1]))
    else:
        module.exit_json(changed=True)

# see http://docs.ansible.com/developing_modules.html#common-module-boilerplate
from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()
