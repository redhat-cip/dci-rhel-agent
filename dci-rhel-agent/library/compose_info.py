#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os

from sys import stderr
from ansible.module_utils.basic import AnsibleModule
from productmd import compose
from productmd import treeinfo

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files or name in dirs:
            return os.path.join(root, name)

class ComposeInfo(object):
    def __init__(self, params):
        # params from AnsibleModule argument_spec below
        self.compose_path = params['compose_path']
        self.arch = params['arch']
        self.variant = params['variant']

        self.compose_info = compose.Compose(self.compose_path)

        name = self.compose_info.info.release.name.replace(' ','')

        version = self.compose_info.info.release.version
        version_major = version.split('.')[0]
        version_minor = version.split('.')[1]
        self.osmajor = "%s%s" % (name, version_major)
        self.osminor = version_minor
        self.compose_id = self.compose_info.info.create_compose_id()

    def find_image(self, os_path):
        image = None
        arch_images = dict( x86_64='grubx64.efi',
                            aarch64='grubaa64.efi',
                            ppc64le='core.elf')

        if self.arch in arch_images:
            arch_image = arch_images[self.arch]
            image_path = find(arch_image, os_path)

        if image_path:
            image = image_path.split(os_path)[1].strip('/')

        return image


    def get_pxe_images(self, variant):
        pxe_images = dict()

        compose_path = self.compose_info.compose_path
        variant_info = self.compose_info.info.variants.variants[variant]
        os_path = variant_info.paths.os_tree[self.arch]
        tree_info_path = os.path.join(compose_path, os_path, ".treeinfo")

        try:
            tree_info = treeinfo.TreeInfo()
            tree_info.load(tree_info_path)

            pxe_images['kernel'] = tree_info.images.images[self.arch]['kernel']
            pxe_images['initrd'] = tree_info.images.images[self.arch]['initrd']
            pxe_images['image'] = self.find_image(os.path.join(compose_path, os_path))
        except (IOError, OSError):
            pass

        return pxe_images

    def get_repos(self):
        repos = dict()

        compose_path = self.compose_info.compose_path
        variants = self.compose_info.info.variants.variants
        for variant in variants:
            if self.arch in variants[variant].paths.os_tree:
                try:
                    repo_path = os.path.join(compose_path,
                            variants[variant].paths.os_tree[self.arch])
                    os.stat(repo_path)
                    repos[variant] = repo_path
                except (IOError, OSError):
                    pass

        return repos

    def get_variant_path(self, variant):
        compose_path = self.compose_info.compose_path
        variant = self.compose_info.info.variants.variants[variant]
        variant_path = variant.paths.os_tree[self.arch]
        return os.path.join(compose_path, variant_path, '')

    def get_boot_variants(self):
        # find bootable variants
        variants = set()
        images = self.compose_info.images.images
        for variant in images:
            if self.arch in images[variant]:
                for image in images[variant][self.arch]:
                    if image.bootable:
                        variants.add(variant)
        return list(variants)


    def results(self):
        # return data in nice format
       results = dict(boot_variants=dict())
       results['compose_id'] = self.compose_id
       results['osmajor'] = self.osmajor
       results['osminor'] = self.osminor
       results['repos'] = self.get_repos()
       variants = self.get_boot_variants()
       for variant in variants:
           pxe_images = self.get_pxe_images(variant)
           if pxe_images:
               results['boot_variants'][variant] = dict(
                       os_tree = self.get_variant_path(variant),
                       pxe_images = pxe_images)

       return results

def main():

    module_args = dict(
        compose_path=dict(type='str', required=True),
        arch=dict(type='str', required=True),
        variant=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        compose_info={},
    )

    module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    compose_info = ComposeInfo(module.params)
    result['compose_info'] = compose_info.results()
    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
