app-pkgs:
  pkg.installed:
    - names:
      - python-virtualenv
      - python-dev
      - python-pip
      - libblas-dev
      - liblapack-dev
      - libatlas-base-dev
      - libxml2-dev

/home/vagrant/.venvs/vsq_computer:
  virtualenv.manage:
    - requirements: /vagrant/requirements.txt
    - no_site_packages: true
    - clear: false
    - require:
      - pkg: app-pkgs


numpy:
  pip.installed:
    - bin_env: /home/vagrant/.venvs/vsq_computer
    - require:
      - pkg: app-pkgs

scipy:
  pip.installed:
    - bin_env: /home/vagrant/.venvs/vsq_computer
    - require:
      - pip: numpy

/vagrant/log:
  file.directory:
    - mode: 755
    - makedirs: True
