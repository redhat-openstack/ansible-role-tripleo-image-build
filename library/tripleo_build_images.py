#!/usr/bin/python
# coding: utf-8 -*-

# this module is based directly on the script of the
# same name in openstack/tripleo-common/scripts

from tripleo_common.image.build import ImageBuildManager
DOCUMENTATION = '''
---
module: tripleo_build_images
version_added: "2.0"
short_description: Build a TripleO overcloud image from a list of yaml definitions
description:
   - Build a TripleO overcloud image from a list of yaml definitions.
options:
  config_files:
    description:
      - list of yaml config files to pass to the tripleo-common image library
    required: true
    default: null
  output_directory:
    description:
      - directory where the images and their logs will be created
    required: true
    default: null
  skip:
    description:
      - whether to skip building images if a copy exists in the output directory
    required: false
    default: true

requirements: ["tripleo-common"]
'''

EXAMPLES = '''
# Build the images defined in my-awesome-images.yml
# and put them in /var/lib/my-awesome-images
- tripleo_build_images:
    config_files:
      - my-awesome-images.yml
    output_directory: "/var/lib/my-awesome-images"

'''


def tripleo_build_images(config_files, output_directory, skip):

    try:
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
