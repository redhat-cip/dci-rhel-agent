SHELL := '/bin/bash'
build:
	podman build -f Dockerfile -t dci-rhel-agent --no-cache

run:
	echo "[DEPRECATION WARNING]: Make support in dci-rhel-agent will be removed in the next version. Please use dci-rhel-agent-ctl." &&  \
	source /etc/dci-rhel-agent/dcirc.sh &&  \
	/bin/dci-downloader --settings "/etc/dci-rhel-agent/settings.yml" && \
	podman pull quay.io/distributedci/dci-rhel-agent:stable && \
	podman run --rm -ti --network host \
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
	echo "[DEPRECATION WARNING]: Make support in dci-rhel-agent will be removed in the next version. Please use dci-rhel-agent-ctl." &&  \
	podman stop $$(podman ps -a -q  --filter ancestor=dci-rhel-agent)

kill:
	echo "[DEPRECATION WARNING]: Make support in dci-rhel-agent will be removed in the next version. Please use dci-rhel-agent-ctl." &&  \
	podman kill $$(podman ps -a -q  --filter ancestor=dci-rhel-agent)

clean:
	echo "[DEPRECATION WARNING]: Make support in dci-rhel-agent will be removed in the next version. Please use dci-rhel-agent-ctl." &&  \
	podman rmi quay.io/distributedci/dci-rhel-agent:stable

shell:
	echo "[DEPRECATION WARNING]: Make support in `dci-rhel-agent` will be removed in the next version. Please use `dci-rhel-agent-ctl`.\n" &&  \
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