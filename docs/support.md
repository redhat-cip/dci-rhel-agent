# RHEL support in DCI

If you are using RHEL you are probably familiar with CDN or FTP. CDN contains officially released and supported content. FTP contains pre-release content. The FTP is updated manually and on demand. DCI allows you to get access to pre-release content in an automated way.

## RHEL compose

Red Hat Enterprise Linux content is in the form of a compose. A compose is a list of RPMs grouped by variants and by architectures.

## Arches

DCI supports x86_64, aarch64 and ppc64le architectures.

## Variants

DCI supports AppStream, BaseOS, CRB, HighAvailability, NFV, RT, ResilientStorage, SAP, SAPHANA variants.

## Versions

RHEL major version corresponds to the first digit in the version number. Currently there is 2 major version of RHEL in DCI: version 8 and version 9

RHEL minor version corresponds to the second digit in the version number. E.g. `RHEL-8.8` or `RHEL-9.0`.

## Tags

Each composes is tagged. A compose can have the tag `nightly`, `candidate` or `milestone`.

- `nightly` composes are built every day, tested and imported to Beaker and Openstack. Those nightlies contain verified RPMs.

- `candidate` composes are `nightly` promoted composes. Those composes are all the very same composes with the very same content, they differ in the amount of testing they received.

- `milestone` composes are the final composes before GA (general availability). beta and release candidate are `milestone` composes.

Note: composes are tested internally. When tests failed DCI ignore those composes. So it is normal that the last nightly could be a few days old.

## Topics

A topic is an abstraction to group different composes together. The name of the topic contains the major and minor version. E.g. RHEL-8.8.

For example you can list the components for the `RHEL-9.0` topic:

- `RHEL-9.0.0-20211121.7` | tags: `nightly`, `kernel:5.14.0-17.el9`
- `RHEL-9.0.0-20211120.6` | tags: `nightly`, `kernel:5.14.0-17.el9`
- `RHEL-9.0.0-20211026.1` | tags: `nightly`, `candidate`, `kernel:5.14.0-17.el9`

If you want to access RHEL-9.0 nightlies only for example, you will have the appropriate filter in your settings file.

```
topics:
  - name: RHEL-9.0
    filters:
      - type: compose
        tag: nightly
```

Note: We recommend to use the topic name without filters. Like that you will always have the latest component available for the topic.

## Retention policies

DCI only keeps the latest 2 composes per tag. After GA we only keep the latest release candidate.

We also disable RHEL topics when the minor version reaches end of life.

## FAQ

### How can I test the latest major version ?

You can use a wildcard filter `RHEL-{8|9}.*` to download the latest available RHEL version in the topic name.

E.g. Get the latest RHEL-9 topic available in DCI:

```
topics:
  - name: RHEL-9.*
```

### I can't test all the nightlies. How can I test less composes?

You can filter components by `candidate` tag.

```
topics:
  - name: RHEL-9.2
    filters:
      - type: compose
        tag: candidate
```

### Some composes are tagged nightly and candidate, is it normal ?

Yes. `nightly`, `candidate` and `milestone` composes are all the very same composes with the very same content, they differ in the amount of testing they received.
Some nightlies are promoted `candidate`. So you will see `nightly` and `candidate` in the tags of those composes.

### Where can some documentation about the Red Hat Enterprise Linux Life Cycle?

[Red Hat Enterprise Linux Life Cycle official document](https://access.redhat.com/support/policy/updates/errata)
