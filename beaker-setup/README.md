# dci-beaker-containers

## requirements

- podman
- ansible

## Edit settings.yml

Copy the default settings.yml.dist to settings.yml and Specify which dns_servers the
beaker containers should use and what data directory to use.

There are other default settings that can be changed.  If you are curious you can see
the defaults in roles/setup_beaker/defaults/main.yml

## log in registry.redhat.io

    podman login registry.redhat.io

## run services

    ansible-playbook -v -e @settings.yml deploy.yml
