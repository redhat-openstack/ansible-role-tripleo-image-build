Role Name
=========

ansible-role-tripleo-image-build

Requirements
------------

This role requires libguestfs, virt-customize, virt-sparsify, and other dependencies via parts/kvm and parts/libvirt.

How does it work?
-----------------

tasks/main.yml After nuking the working directory:
* (repo_setup.yml)         Get the base image and setup yum repositories
* (package_install.yml)    Install packages for overcloud base image
* (convert_undercloud.yml) Use overcloud base image to create undercloud base image
* (dib_build.yml)          Use DIB to build the overlcloud-full and IPA images
* (undercloud_inject.yml)  Inject overcloud-full and IPA images into the undercloud image

Notes:
* The overcloud image is constructed by a series of calls to [virt-customize](http://libguestfs.org/virt-customize.1.html), part of [libguestfs](http://libguestfs.org/) to run scripts that call install packages directly to the qcow2.  Other utilities from this toolset are also used.
* The undercloud qcow is generated by starting with the overcloud and adding/removing a few packages.
* The overcloud image is then written --> undercloud image, so when undercloud.qcow2 is booted by [tripleo-quickstart](https://github.com/openstack/tripleo-quickstart/), the overcloud image is present and ready to be deployed.

Role Variables
--------------

The only required variable is {{ virthost }}, which is the hostname for where the images will be created.  Root access is required.

The defaults for image building are located at defaults/main.yml.  With no params specified (aside from virthost) this role will build images for:

* Mitaka (RDO, delorean, current-passed-ci)
* http://trunk.rdoproject.org/centos7-mitaka/{{ delorean_hash | default('current-passed-ci')}}/delorean.repo
* CentOS 7 base image
* Disk Image Builder (DIB) tools from liberty are used
* images are built in $virthost:/home/oooq-images

### To change or customize how images are built and what they contain, enabling scenarios such as:

* {rdo, rhos} x {centos, rhel}
* RPM's, container (future), built from source (future)
* additional test tools or configuration (be vocal, submit issues/blueprints!)

Variable                    | Description
--------                    | -----------
minimal_base_image_url      | base RHEL image for undercloud and overcloud
repo_script                 | Jinja2 template bash script used to install repositories on base image for binaries via virt-customize
dib_prepare_script          | Jinja2 template bash script used to prepare $virthost for building images with DIB
working_dir                 | All artifacts are created here.
release                     | (rdo only): mitaka, liberty
dib_elements_path           | defines ELEMENTS_PATH when calling disk-image-create
dib_workarounds             | enabled (true) by default, this causes an additional virt-customize pass specifically to massage DIB inputs for temporary workarouds
dib_workaround_script       | ^ the script for this
dib_remove_epel             | if true, removes epel from the DIB elements tree with hostility
dib_release_rpm             | where DIB itself comes from on $virthost.  Default: "http://rdoproject.org/repos/openstack-liberty/rdo-release-liberty.rpm"
dib_environment_additional  | dict() with key-value (NAME=value) settings for DIB (e.g. DIB_YUM_REPO_CONF).  These are added to the env just prior to running disk-image-create
undercloud_remove_packages  | the undercloud image is generated by starting with the overcloud, removing packages from, and adding packages to it.  This is the list of packages to remove  
undercloud_install_packages | ^ this is the list of packages to add
overcloud_package_list      | the set of packages installed (by yum) on the images.  Default: vars/default_package_list.yml
overcloud_images            | the list of artifacts that are packaged and published by invoking this role

### _Here are the full defaults contained in defaults/main.yml.  Note that most are internal and should not be modified._

```YAML
working_dir: /home/oooq-images

# repo_setup vars
minimal_base_image_url: http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2
minimal_overwrite_existing: no
base_os: centos7
release: mitaka
build_system: delorean
repo_script: "repo-{{ base_os }}-{{ release }}-{{ build_system }}.sh.j2"

# package_install vars
overcloud_base_image_url: "file:///{{ working_dir }}/minimal-base.qcow2"
overcloud_overwrite_existing: no
package_install_script: package-install-default.sh.j2
overcloud_package_list: default_package_list.yml

# convert_undercloud vars
undercloud_base_image_url: "file:///{{ working_dir }}/overcloud-base.qcow2"
undercloud_overwrite_existing: no
undercloud_convert_script: undercloud-convert-default.sh.j2
undercloud_disk_size: 40
virt_customize_ram: 28000
virt_customize_cpu: 4
undercloud_remove_packages:
  - cloud-init
  - mariadb-galera-server
  - python-manila
undercloud_install_packages:
  - mariadb-server
  - openstack-tempest
  # -tests packages which contains tempest-style tests
  - python-aodh-tests
  - python-ceilometer-tests
  - python-heat-tests
  - python-ironic-tests
  - python-neutron-tests
  - python-sahara-tests
undercloud_selinux_permissive: true

# dib_build vars
dib_workarounds:       true
dib_workaround_script: dib-workaround-default.sh.j2
dib_elements_path:     /usr/share/tripleo-image-elements:/usr/share/tripleo-puppet-elements:/usr/share/instack-undercloud/:/usr/share/openstack-heat-templates/software-config/elements/
dib_prepare_script:    dib-prepare-centos7-default.sh.j2
dib_remove_epel:       true
dib_release_rpm:       "http://rdoproject.org/repos/openstack-liberty/rdo-release-liberty.rpm"

# undercloud_inject vars
overcloud_images:
  - ironic-python-agent.initramfs
  - ironic-python-agent.kernel
  - overcloud-full.initrd
  - overcloud-full.qcow2
  - overcloud-full.vmlinuz

# fail, ignore, continue.  See http://libguestfs.org/virt-sparsify.1.html
virt_sparsify_checktmpdir_flag: fail
```

Dependencies
------------

No other galaxy roles are leveraged.  libvirt and portions of KVM are used to build images.

Consumers of this role (known)
------------------------------

Anyone who wants to build images.  Tools such as [C.A.T.](https://github.com/redhat-openstack/ci-ansible-tripleo) and [tripleo-quickstart]([tripleo-quickstart](https://github.com/openstack/tripleo-quickstart/)

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: ansible-role-tripleo-image-build, virthost: buildhost.mydomain.com }

# How to contribute

Contributions and patches are welcome!  Feel free to log issues and/or discuss here:

[https://github.com/redhat-openstack/ansible-role-tripleo-image-build/issues](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/issues)

Code reviews and patches are managed by Gerrit here:

[https://review.gerrithub.io/#/q/project:redhat-openstack/ansible-role-tripleo-image-build](https://review.gerrithub.io/#/q/project:redhat-openstack/ansible-role-tripleo-image-build)

Ideas for substantive changes and/or features/targets/requirements, reach out on IRC at #rdo or please submit a blueprint here:

[https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blueprints](https://github.com/redhat-openstack/ansible-role-tripleo-image-build/blueprints)

### How to: setup env --> propose a patch:

```bash
$ git clone ssh://github.com/redhat-openstack/ansible-role-tripleo-image-build
  ...
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

To address feedback and iterate on reviews, amend your existing commit (git commit --amend) and run "git review" again.  Be sure to leave the Change-Id alone!

License
-------

Apache2

Author Information
------------------

redhat-openstack