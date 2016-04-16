Role Name
=========

ansible-role-tripleo-image-build

Requirements
------------

This role requires libguestfs, virt-customize, virt-sparsify, and other dependencies via parts/kvm and parts/libvirt.

Role Variables
--------------

The only required variable is {{ virthost }}, which is the hostname for where the images will be created.  Root access is required.

The defaults for image building are located at defaults/main.yml.  With no params specified (aside from virthost) this role will build images for:

* Mitaka (RDO, delorean, current-passed-ci)
* http://trunk.rdoproject.org/centos7-mitaka/{{ delorean_hash | default('current-passed-ci')}}/delorean.repo
* CentOS 7 base image
* Disk Image Builder (DIB) tools from liberty are used
* images are built in $virthost:/home/oooq-images

### _The variables that need to be overridden to use this mechanism to build images containing RHOS (vs. RDO) binaries and using RHEL (vs. CentOS7) base images are the following:_

Setting | Description
------- | -----------
artib_minimal_base_image_url | base RHEL image for undercloud and overcloud
artib_repo_script | Jinja2 template bash script used to install repositories on base image for binaries via virt-customize
artib_dib_prepare_script | Jinja2 template bash script used to prepare $virthost for building images.  

### _Here are the full defaults contained in defaults/main.yml.  Note that most are internal and should not be modified._

```YAML
artib_working_dir: /home/oooq-images

# repo_setup vars
artib_minimal_base_image_url: http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2
artib_minimal_overwrite_existing: no
artib_base_os: centos7
artib_release: mitaka
artib_build_system: delorean
artib_repo_script: "repo-{{ artib_base_os }}-{{ artib_release }}-{{ artib_build_system }}.sh.j2"

# package_install vars
artib_overcloud_base_image_url: "file:///{{ artib_working_dir }}/minimal-base.qcow2"
artib_overcloud_overwrite_existing: no
artib_package_install_script: package-install-default.sh.j2
artib_overcloud_package_list: default_package_list.yml

# convert_undercloud vars
artib_undercloud_base_image_url: "file:///{{ artib_working_dir }}/overcloud-base.qcow2"
artib_undercloud_overwrite_existing: no
artib_undercloud_convert_script: undercloud-convert-default.sh.j2
artib_undercloud_disk_size: 40
artib_virt_customize_ram: 28000
artib_virt_customize_cpu: 4
artib_undercloud_remove_packages:
  - cloud-init
  - mariadb-galera-server
  - python-manila
artib_undercloud_install_packages:
  - mariadb-server
  - openstack-tempest
  # -tests packages which contains tempest-style tests
  - python-aodh-tests
  - python-ceilometer-tests
  - python-heat-tests
  - python-ironic-tests
  - python-neutron-tests
  - python-sahara-tests
artib_undercloud_selinux_permissive: true

# dib_build vars
artib_dib_workarounds:       true
artib_dib_workaround_script: dib-workaround-default.sh.j2
artib_dib_elements_path:     /usr/share/tripleo-image-elements:/usr/share/tripleo-puppet-elements:/usr/share/instack-undercloud/:/usr/share/openstack-heat-templates/software-config/elements/
artib_dib_prepare_script:    dib-prepare-centos7-default.sh.j2
artib_dib_remove_epel:       true
artib_dib_release_rpm:       "http://rdoproject.org/repos/openstack-liberty/rdo-release-liberty.rpm"

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

No other galaxy roles are leveraged.  libvirt and portions of KVM are used to build images.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: ansible-role-tripleo-image-build, virthost: buildhost.mydomain.com }

License
-------

Apache2

Author Information
------------------

redhat-openstack