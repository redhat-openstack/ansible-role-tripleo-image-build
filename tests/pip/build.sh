#!/bin/bash
: ${OPT_SYSTEM_PACKAGES:=0}
: ${OPT_WORKDIR:=$PWD/.artib}
: ${OPT_CLEANUP:=0}
: ${REQUIREMENTS:=requirements-build.txt}
: ${RELEASE:=mitaka}
: ${BASE_OS:=centos7}
: ${PLAYBOOK:=build_default_images.yml}

: ${OPT_ARTNAME:=ansible-role-tripleo-image-build}
: ${OPT_ARTGITURL:=ssh://github.com/redhat-openstack/$OPT_ARTNAME}

clean_virtualenv() {
    if [ -d $OPT_WORKDIR ]; then
        echo "rm -rf $OPT_WORKDIR"
        rm -rf $OPT_WORKDIR
    fi
}

install_deps () {
    yum -y install git python-virtualenv gcc libyaml
}

setup() {

    if [ "$OPT_CLEANUP" = 1 ]; then
        clean_virtualenv
    fi
    virtualenv $( [ "$OPT_SYSTEM_PACKAGES" = 1 ] && printf -- "--system-site-packages\n" ) $OPT_WORKDIR
    . $OPT_WORKDIR/bin/activate

    if [ "$OPT_CLONE" == 1 ]; then
        if ! [ -d "$OPT_WORKDIR/$OPT_ARTNAME" ]; then
            echo "Cloning $OPT_ARTNAME repository..."
            git clone $OPT_ARTGITURL\
                $OPT_WORKDIR/OPT_$ARTNAME
        fi

        cd $OPT_WORKDIR/OPT_ARTNAME
        git remote update
        git checkout --quiet origin/master
    fi

    pip install -r $REQUIREMENTS
}

# TODO: add flag for OPT_ARTNAME and/or OPT_ARTGITURL
usage() {
    echo "$0 [options] virthost"
    echo ""
    echo "   -i, --install-deps            Install C.A.T. dependencies (git, virtualenv, gcc, libyaml)"
    echo ""
    echo " * Basic options w/ defaults"
    echo "   -p, --playbook <playbook>     default: '$PLAYBOOK', Specify playbook to be executed."
    echo "   -z, --requirements <file>     default: '$REQUIREMENTS', Specify the python setup tools requirements file."
    echo "   -r, --release <release>       default: 'mitaka',  { kilo | liberty | mitaka } "
    echo "   -b, --base_os <os>            default: 'centos7', { centos7 | rhel }"
    echo "   -e, --extra-vars <file>       Additional Ansible variables.  Supports multiple ('-e f1 -e f2')"
    echo "   -o, --output <logfile>        tee output to file"
    echo ""
    echo " * Advanced options"
    echo "   -w, --working-dir <directory> Location of ci-ansible-tripleo sources and virtual env"
    echo "   -c, --clean                   Clean the virtualenv before running a deployment"
    echo "   -g, --git-clone               Git clone --> $OPT_ARTGITURL"
    echo "   -s, --system-site-packages    Create virtual env with access to local site packages"
    echo "   -v, --ansible-debug           Invoke ansible-playbook with -vvvv "
    echo "   -h, -?, --help                Display this help and exit"
}

while [ "x$1" != "x" ]; do
    case "$1" in
        --install-deps|-i)
            OPT_INSTALL_DEPS=1
            ;;

        --playbook|-p)
            PLAYBOOK=$2
            shift
            ;;

        --requirements|-z)
            REQUIREMENTS=$2
            shift
            ;;

        --release|-r)
            RELEASE=$2
            shift
            ;;

        --base_os|-b)
            BASE_OS=$2
            shift
            ;;

        --base_url|-u)
            OPT_BASE_URL=$2
            shift
            ;;

        --extra-vars|-e)
            EXTRA_VARS_FILE="$EXTRA_VARS_FILE -e @$2 "
            shift
            ;;

        --output|-o)
            OPT_OUTPUT_FILE=$2
            shift
            ;;

        # Advanced Options
        --working-dir|-w)
            OPT_WORKDIR=$2
            shift
            ;;

        --clean|-c)
            OPT_CLEANUP=1
            ;;

        --git-clone|-g)
            OPT_CLONE=1
            ;;

        --system-site-packages|-s)
            OPT_SYSTEM_PACKAGES=1
            ;;

        --ansible-debug|-v)
            OPT_DEBUG_ANSIBLE=1
            ;;

        --help|-h|-?)
            usage
            exit
            ;;

        --) shift
            break
            ;;

        -*) echo "ERROR: unknown option: $1" >&2
            usage >&2
            exit 2
            ;;

        *)  break
            ;;
    esac

    shift
done

set -x

if [ "$OPT_CLONE" != 1 ]; then
    CAT_DIR=$(pwd)
else
    CAT_DIR=$OPT_WORKDIR/$OPT_ARTNAME/tests
fi

if [ "$OPT_INSTALL_DEPS" = 1 ]; then
    echo "NOTICE: installing dependencies (git, virtualenv, gcc, libyaml)"
    install_deps
    exit $?
fi

if [ "$#" -lt 1 ]; then
    echo "ERROR: You must specify a target machine." >&2
    usage >&2
    exit 2
fi

VIRTHOST=$1

echo "Setup $OPT_ARTNAME virtualenv and install dependencies"
setup
echo "Activate virtualenv"
. $OPT_WORKDIR/bin/activate

# use exported ansible variables
source pip-ansible-env.sh
env | grep ANSIBLE
echo " "; echo " "

# add the virthost to the ssh config

if [ ! -f $OPT_WORKDIR/ssh.config.ansible ] || [ `grep --quiet "Host $VIRTHOST" $OPT_WORKDIR/ssh.config.ansible` ]; then
cat <<EOF >> $OPT_WORKDIR/ssh.config.ansible
Host $VIRTHOST
    User root
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
EOF
fi

set -x

if [ "$OPT_DEBUG_ANSIBLE" = 1 ]; then
    VERBOSITY=vvvv
else
    VERBOSITY=vv
fi

if [ -n "$OPT_OUTPUT_FILE" ]; then
    OUTFILE=" | tee $OPT_OUTPUT_FILE"
else
    OUTFILE=""
fi

if [ -n "$OPT_BASE_URL" ]; then
    BASE_URL=" -e artib_minimal_base_image_url=$OPT_BASE_URL"
else
    BASE_URL=""
fi

echo "Building images for ${RELEASE:+"$RELEASE "}on host $VIRTHOST"
echo "Executing Ansible..."

ansible-playbook -$VERBOSITY $PLAYBOOK \
    -e ansible_python_interpreter=/usr/bin/python \
    -e local_working_dir=$OPT_WORKDIR \
    -e virthost=$VIRTHOST \
    -e artib_base_os=$BASE_OS \
    -e artib_release=$RELEASE \
    $EXTRA_VARS_FILE \
    $BASE_URL \
    $OUTFILE

