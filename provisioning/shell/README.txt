# install everything with these commands

# initial provision, from s3, since nothing is on the machine
#  debian and pip packages
#  ssh key, comfortable profile, locale adjustments, ...
wget -O - http://s3.amazonaws.com/depp_appoggio/vsq_provisioning/init-vsqcomputer.sh | bash

# logout/login

. /home/vsqcomputer/provisioning/shell/uwsgi.sh
