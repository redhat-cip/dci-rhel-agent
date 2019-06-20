SHELL := '/bin/bash'
build:
	podman build -f Dockerfile -t dci-rhel-agent --no-cache

run:
	podman pull quay.io/distributedci/dci-rhel-agent:stable && source /etc/dci-rhel-agent/dcirc.sh && podman run --rm -ti --network host \
	-e DCI_CLIENT_ID \
	-e DCI_API_SECRET \
	-e DCI_CS_URL \
	-e DCI_LOCAL_REPO \
	-e DCI_BEAKER_CONFIG \
	-e PS1='\[\e[32m\][container]#\[\e[m\] ' \
	-v /etc/dci-rhel-agent/hooks/:/etc/dci-rhel-agent/hooks/ \
	-v /etc/dci-rhel-agent/settings.yml:/etc/dci-rhel-agent/settings.yml \
	-v /etc/dci-rhel-agent/hosts:/etc/dci-rhel-agent/hosts  \
	-v $$DCI_LOCAL_REPO:/var/www/html \
	-v $$DCI_BEAKER_CONFIG:/etc/beaker/ \
	quay.io/distributedci/dci-rhel-agent:stable

stop:
	podman stop $$(podman ps -a -q  --filter ancestor=dci-rhel-agent)

kill:
	podman kill $$(podman ps -a -q  --filter ancestor=dci-rhel-agent)

clean:
	podman rmi quay.io/distributedci/dci-rhel-agent:stable

shell:
	podman pull quay.io/distributedci/dci-rhel-agent:stable && source /etc/dci-rhel-agent/dcirc.sh && podman run --rm -ti --network host \
	-e DCI_CLIENT_ID \
	-e DCI_API_SECRET \
	-e DCI_CS_URL \
	-e DCI_LOCAL_REPO \
	-e DCI_BEAKER_CONFIG \
	-e PS1='\[\e[32m\][container]#\[\e[m\] ' \
	-v /etc/dci-rhel-agent/hooks/:/etc/dci-rhel-agent/hooks/ \
	-v /etc/dci-rhel-agent/settings.yml:/etc/dci-rhel-agent/settings.yml \
	-v /etc/dci-rhel-agent/hosts:/etc/dci-rhel-agent/hosts  \
	-v $$DCI_LOCAL_REPO:/var/www/html \
	-v $$DCI_BEAKER_CONFIG:/etc/beaker/ \
	quay.io/distributedci/dci-rhel-agent:stable bash