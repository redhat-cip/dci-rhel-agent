build:
	podman build -f Dockerfile -t dci-rhel-agent

run:
	podman run --rm -ti --network host\
	-v /etc/dci-rhel-agent/hooks/user-tests.yml:/etc/dci-rhel-agent/hooks/user-tests.yml \
	-v /etc/dci-rhel-agent/settings.yml:/etc/dci-rhel-agent/settings.yml \
	-v /etc/dci-rhel-agent/hosts:/etc/dci-rhel-agent/hosts	\
	-v /var/www:/var/www/ \
        -v /etc/beaker/:/etc/beaker/ \
	localhost/dci-rhel-agent

clean:
	podman rmi localhost/dci-rhel-agent

shell:
	podman run --rm -ti --network host\
	-v /etc/dci-rhel-agent/hooks/user-tests.yml:/etc/dci-rhel-agent/hooks/user-tests.yml \
	-v /etc/dci-rhel-agent/settings.yml:/etc/dci-rhel-agent/settings.yml \
	-v /etc/dci-rhel-agent/hosts:/etc/dci-rhel-agent/hosts	\
	-v /var/www:/var/www/ \
        -v /etc/beaker/:/etc/beaker/ \
	localhost/dci-rhel-agent bash