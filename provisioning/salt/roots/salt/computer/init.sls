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
      - octave

/home/vagrant/.venvs/vsq_computer:
  virtualenv.manage:
    - requirements: /vagrant/requirements.txt
    - no_site_packages: true
    - clear: false
    - require:
      - pkg: app-pkgs

oct2py:
  pip.installed:
    - name: oct2py
    - bin_env: /home/vagrant/.venvs/vsq_computer
    - require:
      - pkg: python-scipy


/vagrant/log:
  file.directory:
    - mode: 755
    - makedirs: True