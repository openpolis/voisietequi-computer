# install everything with these commands

# initial provision, from s3, since nothing is on the machine
#  debian and pip packages
#  ssh key, comfortable profile, locale adjustments, ...
wget -O - http://s3.amazonaws.com/depp_appoggio/vsq_provisioning/init-vsqcomputer.sh | bash

# logout/login

. /home/vsqcomputer/provisioning/shell/uwsgi.sh
cp /home/vsqcomputer/provision/uwsgi80*.ini /etc/uwsgi/vassals/

#per testare, da una macchina locale:
curl -X POST -d @request.json http://server.staging.voisietequi.it:8010/computation/