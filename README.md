Role Name
=========

ansible-role-tripleo-image-build

This is a standard Ansible role, and can be installed as a dependency via ansible-galaxy, pip, or your own mechanism(s)

Consumers of this role (known)
------------------------------

Anyone who wants to build images. Tools such as:
* [ci.centos.org](https://ci.centos.org) image building jobs that create images used by [tripleo-quickstart](https://github.com/openstack/tripleo-quickstart)
* [Self Test (tests/build.sh)](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/tests/build.sh)
* [C.A.T.](https://github.com/redhat-openstack/ci-ansible-tripleo)
* other folks building images for various test and CI purposes

via Ansible Galaxy
------------------
```bash
ansible-galaxy -v install -p roles-from-galaxy -r requirements-build.yml

- extracting ansible-role-tripleo-image-build to roles-from-galaxy/ansible-role-tripleo-image-build
- ansible-role-tripleo-image-build was installed successfully
```

[requirements-build.yml](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blob/master/tests/galaxy/requirements-build.yml)
```YAML
# from GitHub
   - sec: git+ssh://github.com/redhat-openstack/ansible-role-tripleo-parts
   - src: git+ssh://github.com/redhat-openstack/ansible-role-tripleo-image-build

# local files
#  - src: file:///home/me/ci/ansible-role-tripleo-image-build
```

via Python Setup Tools (virtualenv, pip) [C.A.T.](https://github.com/redhat-openstack/ci-ansible-tripleo)
---------------------------------------------------------------------------------------------------------
In addition to supporting Galaxy, this role allows for being installed via pip.  A file is provided in the root of this repo ([setup.cfg](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blob/master/setup.cfg)) that will install the necessary files in egg form.

```bash
pip install -r requirements-build.txt
```

That file might look like this

[requirements-build.txt](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blob/master/tests/pip/requirements-build.txt)
```bash
pbr>=1.6
ansible==2.0.1

git+https://github.com/redhat-openstack/ansible-role-tripleo-parts.git#egg=ansible-role-tripleo-parts
git+https://github.com/redhat-openstack/ansible-role-tripleo-image-build.git#egg=ansible-role-tripleo-image-build

# to pull in local development changes
#file:///home/me/ci/ansible-role-tripleo-image-build/#egg=ansible-role-tripleo-image-build
```

via ARTIB test script (tests/build.sh)
--------------------------------------

In addition to the methods described above to reference and/or import this role into your own project, a sample script
provided that allows for creating images directly from a clone of this git repository.  If you have ideas on how to make
this role better (and want to contribute) please see below for details on how to submit a patch.  build.sh is likely the
easiest way to iterate on this role locally.

[build.sh](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blob/master/tests/pip/build.sh)
```bash
cd tests/pip
./build.sh $VIRTHOST
```

Full options for build.sh

```bash
./build.sh [options] virthost

   -i, --install-deps            Install C.A.T. dependencies (git, virtualenv, gcc, libyaml)

 * Basic options w/ defaults
   -p, --playbook <playbook>     default: 'build_default_images.yml', Specify playbook to be executed.
   -z, --requirements <file>     default: 'requirements-build.txt', Specify the python setup tools requirements file.
   -r, --release <release>       default: 'mitaka',  { kilo | liberty | mitaka }
   -o, --base_os <os>            default: 'centos7', { centos7 | rhel }
   -e, --extra-vars <file>       Additional Ansible variables.  Supports multiple ('-e f1 -e f2')

 * Advanced options
   -w, --working-dir <directory> Location of ci-ansible-tripleo sources and virtual env
   -c, --clean                   Clean the virtualenv before running a deployment
   -g, --git-clone               Git clone --> ssh://github.com/redhat-openstack/ansible-role-tripleo-image-build
   -s, --system-site-packages    Create virtual env with access to local site packages
   -v, --ansible-debug           Invoke ansible-playbook with -vvvv
   -h, -?, --help                Display this help and exit
```

Example Playbook
----------------

Note: this sample playbook leverages [a simple role](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/tree/master/tests/pip/roles/add-inventory-virthost) that dynamically adds $VIRTHOST (via 'virthost') to the Ansible inventory.

```YAML
  hosts: localhost
  roles:
    - { role: add-inventory-virthost, virthost: "$VIRTHOST" }

    - name: Build images using defaults (rdo, mitaka, centos7)
      hosts: virthost
      remote_user: root
      roles:
        - parts/kvm
        - parts/libvirt
        - ansible-role-tripleo-image-build
```


Requirements
------------

This role requires libguestfs, virt-customize, virt-sparsify, and other dependencies installed and configured via parts/kvm and parts/libvirt.

How does it work?
-----------------

meta/main.yml pulls in the following dependencies that setup KVM, libvirt, and libguestfs.  These are provided by [ansible-role-tripleo-parts](http://github.com/redhat-openstack/ansible-role-tripleo-parts)
* parts/kvm
* parts/libvirt

tasks/main.yml After nuking the working directory:
* (repo_setup.yml)         Get the base image and setup yum repositories
* (package_install.yml)    Install packages for overcloud base image
* (convert_undercloud.yml) Use overcloud base image to create undercloud base image
* (dib_build.yml)          Use DIB to build the overlcloud-full and IPA images, leveraging support from [tripleo-common](https://github.com/openstack/tripleo-common)
* (undercloud_inject.yml)  Inject overcloud-full and IPA images into the undercloud image

Notes:
* The overcloud image is constructed by a series of calls to [virt-customize](http://libguestfs.org/virt-customize.1.html), part of [libguestfs](http://libguestfs.org/) to run scripts that 'yum install' directly to the qcow2. Other utilities from this toolset are also used to grow/shrink/sparsify/manipulate the image(s).
* The undercloud qcow is generated by starting with the overcloud and adding/removing a few packages.
* The overcloud and IPA images are then written --> undercloud image, so when undercloud.qcow2 is booted by [tripleo-quickstart](https://github.com/openstack/tripleo-quickstart/), the overcloud image is present and ready to be deployed.

Logs
----
All land in working_dir.

The builder logs are a canonical log of how the qcow2's are created, and is the best, first place to look/explore.
* builder-undercloud.log
* builder-overcloud.log

Content Manifests (every file, size, mode, etc)
* content-undercloud.csv
* content-overcloud.csv

Additional per-phase (potentially verbose) logs are found in working directory

Role Variables
--------------

The defaults for image building are located at defaults/main.yml. With no params specified this role will build images for:

* Mitaka (RDO, delorean, current-passed-ci)
* http://trunk.rdoproject.org/centos7-mitaka/{{ artib_delorean_hash | default('current-passed-ci')}}/delorean.repo
* CentOS 7 base image
* Disk Image Builder (DIB) tools from liberty are used
* images are built in $virthost:/home/oooq-images

To change or customize how images are built and what they contain, enabling scenarios such as:

* {rdo, rhos} x {centos, rhel}
* RPM's, container (future), built from source (future)
* additional test tools or configuration (be vocal, submit issues/blueprints!)

Variable                          | Description
--------                          | -----------
artib_working_dir                 | All artifacts are created here.
artib_minimal_base_image_url      | base image for undercloud and overcloud
artib_repo_script                 | Jinja2 template bash script used to install repositories on base image for binaries via virt-customize
artib_dib_prepare_script          | Jinja2 template bash script used to prepare host for building images with DIB
artib_release                     | (rdo only): mitaka, liberty
artib_dib_workarounds             | enabled (true) by default, this causes an additional virt-customize pass specifically to massage DIB inputs for temporary workarouds
artib_dib_workaround_script       | ^ the script for this
artib_dib_remove_epel             | if true, removes epel from the DIB elements tree with hostility
artib_dib_release_rpm             | where DIB itself comes from. Default: "http://rdoproject.org/repos/openstack-liberty/rdo-release-liberty.rpm"
artib_undercloud_remove_packages  | the undercloud image is generated by starting with the overcloud, removing packages from, and adding packages to it. This is the list of packages to remove
artib_undercloud_install_packages | ^ this is the list of packages to add
artib_overcloud_package_list      | the set of packages installed (by yum) on the images. Default: vars/default_package_list.yml
artib_overcloud_images            | the list of artifacts that are packaged and published by invoking this role
artib_vc_verbose                  | (default: false) set to true for verbose   virt-customize output
artib_vc_trace                    | (default: false) set to true for trace/dbg virt-customize output

Here are the full defaults contained in defaults/main.yml.  Note that most are internal and should not be modified.

```YAML
# defaults file for ansible-role-tripleo-image-build

# global build vars
artib_working_dir: /var/lib/oooq-images
# Whether or not to delete the working directory before starting.
artib_start_over: true

# repo_setup vars
artib_minimal_base_image_url:
  http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2
artib_minimal_overwrite_existing: no
artib_base_os: centos7
artib_release: mitaka
artib_build_system: delorean
artib_repo_script: "repo-{{ artib_base_os }}-{{ artib_build_system }}.sh.j2"

# package_install vars
artib_overcloud_base_image_url:
  "file:///{{ artib_working_dir }}/minimal-base.qcow2"
artib_overcloud_overwrite_existing: no
artib_package_install_script: package-install-default.sh.j2
artib_overcloud_package_list: default_package_list.yml

# convert_undercloud vars
artib_undercloud_base_image_url:
  "file:///{{ artib_working_dir }}/overcloud-base.qcow2"
artib_undercloud_overwrite_existing: no
artib_undercloud_convert_script: undercloud-convert-default.sh.j2
artib_undercloud_disk_size: 40

artib_vc_ram: 8192
artib_vc_cpu: 4
artib_vc_verbose: false
artib_vc_trace: false

artib_undercloud_remove_packages:
  - cloud-init
  - mariadb-galera-server
artib_undercloud_install_packages:
  - mariadb-server
  - openstack-tempest
  # -tests packages which contains tempest-style tests
  - python-aodh-tests
  - python-ceilometer-tests
  - python-heat-tests
  - python-ironic-tests
  - python-keystone-tests
  - python-manila-tests
  - python-mistral-tests
  - python-neutron-tests
  - python-sahara-tests
  - python-zaqar-tests
artib_undercloud_selinux_permissive: true

##################
# dib_build vars #
##################

# default templates to use to create the yaml files
# passed to the tripleo-common image building library
artib_agent_ramdisk_yaml_template:    "ironic-python-agent.yaml.j2"
artib_overcloud_full_yaml_template:   "overcloud-full.yaml.j2"

# elements key takes a space-seperated list, while packages key
# takes a YAML list.
# (trown) might be something to fix in tripleo-common
artib_agent_ramdisk_elements: >
  dhcp-all-interfaces
  dynamic-login
  element-manifest
  ironic-agent
  network-gateway
  pip-and-virtualenv-override
  selinux-permissive
artib_overcloud_full_elements: >
  baremetal
  dhcp-all-interfaces
  dynamic-login
  element-manifest
  grub2
  hiera
  heat-config-puppet
  heat-config-script
  hosts
  network-gateway
  os-net-config
  pip-and-virtualenv-override
  selinux-permissive
  stable-interface-names
  sysctl

artib_agent_ramdisk_packages:
  - python-hardware-detect
artib_overcloud_full_packages: []

artib_agent_ramdisk_options:
  - "--min-tmpfs=5"
artib_overcloud_full_options:
  - "--min-tmpfs=5"

artib_dib_workarounds: true
artib_dib_workaround_script: dib-workaround-default.sh.j2
artib_dib_elements_path:
  - /usr/share/tripleo-image-elements
  - /usr/share/tripleo-puppet-elements
  - /usr/share/instack-undercloud/
  - /usr/share/openstack-heat-templates/software-config/elements/
artib_dib_prepare_script: dib-prepare-centos7-default.sh.j2
artib_dib_remove_epel: true
artib_dib_release_rpm:
  "http://rdoproject.org/repos/openstack-mitaka/rdo-release-mitaka.rpm"

# undercloud_inject vars
artib_overcloud_images:
  - ironic-python-agent.initramfs
  - ironic-python-agent.kernel
  - overcloud-full.initrd
  - overcloud-full.qcow2
  - overcloud-full.vmlinuz

# fail, ignore, continue.  See http://libguestfs.org/virt-sparsify.1.html
artib_virt_sparsify_checktmpdir_flag: fail
```

Dependencies
------------

No other galaxy roles are leveraged. libvirt and portions of KVM are used to build images via parts/kvm, and parts/libvirt

# How to contribute

Contributions and patches are welcome!  Feel free to log issues and/or discuss here:

[https://github.com/redhat-openstack/ansible-role-tripleo-image-build/issues](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/issues)

Code reviews and patches are managed by Gerrit here:

[https://review.gerrithub.io/#/q/project:redhat-openstack/ansible-role-tripleo-image-build](https://review.gerrithub.io/#/q/project:redhat-openstack/ansible-role-tripleo-image-build)

Ideas for substantive changes and/or features/targets/requirements are heartily welcomed.  Please do reach out on IRC (freenode) at #rdo or #tripleo, or please submit a blueprint here:

[https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blueprints](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blueprints)

### How to: setup env --> propose a patch:

```bash
$ git clone ssh://github.com/redhat-openstack/ansible-role-tripleo-image-build
$ cd ansible-role-tripleo-image-build/
$ git review -s
Creating a git remote called "gerrit" that maps to:
	ssh://github-username@review.gerrithub.io:29418/redhat-openstack/ansible-role-tripleo-image-build.git

$ git remote -v
gerrit	ssh://github-username@review.gerrithub.io:29418/redhat-openstack/ansible-role-tripleo-image-build.git (fetch)
gerrit	ssh://github-username@review.gerrithub.io:29418/redhat-openstack/ansible-role-tripleo-image-build.git (push)
origin	ssh://github.com/redhat-openstack/ansible-role-tripleo-image-build (fetch)
origin	ssh://github.com/redhat-openstack/ansible-role-tripleo-image-build (push)
```
* create a branch (git checkout -b my-groovy-idea)
* add files and commit
* Post review (git review)

The commit message should be of the form:

```bash
A single line description of the change

A multi-line description of the change, ideally with
context and/or URL to github issue.
```

To address feedback and iterate on reviews, amend your existing commit (git commit --amend) and run "git review" again. Be sure to leave the Change-Id alone!

License
-------

Apache2

Author Information
------------------

redhat-openstack

