#!/bin/bash

# see README.txt for instructions

# get rsa public key for my laptop
mkdir -p ~/.ssh/
wget -O - http://s3.amazonaws.com/depp_appoggio/vsq_provisioning/id_rsa_lapgu.pub > ~/.ssh/authorized_keys


# get comfortable env (aliases)
wget -O - http://s3.amazonaws.com/depp_appoggio/vsq_provisioning/_bashrc > /root/.bashrc

# backports package repository
cat <<EOF | tee /etc/apt/sources.list.d/backports.list
  deb http://backports.debian.org/debian-backports squeeze-backports main
EOF

# fix locales
touch /etc/locale.gen && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && /usr/sbin/locale-gen
echo export LANG=en_US.utf8 >> /etc/.bashrc
export LANG=en_US.utf8

# update packages, get some basic stuff
apt-get -y update
apt-get -y install python-virtualenv python-dev python-pip libblas-dev liblapack-dev libatlas-base-dev libxml2-dev
apt-get -y install vim
apt-get -y install git

# set vi as default editor
update-alternatives --set editor /usr/bin/vim.basic



# install uwsgi
/usr/bin/pip install uwsgi
/usr/bin/pip install virtualenvwrapper


# virtaulenvwrapper setup
export PROJECT_HOME=/home
export WORKON_HOME=/home/virtualenvs
. /usr/local/bin/virtualenvwrapper.sh


# clone vsq repo from github (html, no ssh keys exchange)
pushd /home
git clone https://github.com/openpolis/voisietequi.git vsq13

mkvirtualenv vsq_computer

pushd /home/vsq_computer
setvirtualenvproject

pip install --upgrade pip
pip install numpy --use-mirrors
pip install scipy --use-mirrors
pip install --use-mirrors -r requirements.txt

mkdir log
chown uwsgi log
chown uwsgi -R public/media/

popd

popd