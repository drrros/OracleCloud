import datetime
import sys
from time import sleep
from typing import Tuple

import oci
from oci import Response
from oci.core.models import Image


def find_image(list_images_response: Response) -> Image:
    cloud_dev_images = []
    for i in list_images_response.data:
        if 'Oracle Linux Cloud Developer' in i.operating_system:
            cloud_dev_images.append(i)
    sorted_images = sorted(cloud_dev_images, key=lambda x: x.time_created)
    return sorted_images[-1]


def launch(config: dict, ssh_authorized_keys: str):
    comp_id = {'compartment_id': config['tenancy']}
    core_client = oci.core.ComputeClient(config)
    list_images_response = core_client.list_images(**comp_id)
    image = find_image(list_images_response)
    identity_client = oci.identity.IdentityClient(config)
    domains = identity_client.list_availability_domains(**comp_id)
    vnet_client = oci.core.VirtualNetworkClient(config)
    vnet_list = vnet_client.list_subnets(**comp_id)
    while True:
        try:
            launch_instance_details = oci.core.models.LaunchInstanceDetails(
                availability_domain=domains.data[0].name,
                compartment_id=comp_id['compartment_id'],
                shape='VM.Standard.A1.Flex',
                create_vnic_details=oci.core.models.CreateVnicDetails(
                    assign_public_ip=True,
                    assign_private_dns_record=True,
                    subnet_id=vnet_list.data[0].id,
                ),
                display_name="VM.Standard.A1.Flex",
                hostname_label="a1standard",
                image_id=image.id,
                launch_options=oci.core.models.LaunchOptions(
                    boot_volume_type='PARAVIRTUALIZED',
                    firmware="UEFI_64",
                    network_type='PARAVIRTUALIZED',
                    remote_data_volume_type='PARAVIRTUALIZED',
                    is_pv_encryption_in_transit_enabled=True,
                    is_consistent_volume_naming_enabled=True),
                instance_options=oci.core.models.InstanceOptions(
                    are_legacy_imds_endpoints_disabled=False),
                availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
                    recovery_action="RESTORE_INSTANCE"),
                metadata={
                    'ssh_authorized_keys': ssh_authorized_keys},
                agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
                    is_monitoring_disabled=False,
                    is_management_disabled=False,
                    are_all_plugins_disabled=False,
                    plugins_config=[
                        oci.core.models.InstanceAgentPluginConfigDetails(
                            name='Compute Instance Monitoring',
                            desired_state='ENABLED'),
                        oci.core.models.InstanceAgentPluginConfigDetails(
                            name='Compute Instance Run Command',
                            desired_state='ENABLED'),
                    ]),
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                    ocpus=4,
                    memory_in_gbs=24,
                ),
                source_details=oci.core.models.InstanceSourceViaImageDetails(
                    source_type="image",
                    image_id=image.id,
                    boot_volume_size_in_gbs=50
                ),
                subnet_id=vnet_list.data[0].id,
                is_pv_encryption_in_transit_enabled=True,
            )
            launch_instance_response = core_client.launch_instance(
                launch_instance_details=launch_instance_details)
            print(launch_instance_response)
            break
        except oci.exceptions.ServiceError as e:
            print(datetime.datetime.now().strftime('%d %b %Y %H:%M:%S'), e)
            sleep(300)
            continue


def get_config() -> Tuple[dict, str]:
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python generate_a1_instance config_filename key_filename")
    else:
        ssh_authorized_keys = input('Enter authorized_keys content: ')
        cfg_content = []
        with open(sys.argv[1], 'r+') as f:
            for line in f:
                if 'key_file' in line:
                    line = f'key_file=./{sys.argv[2]}'
                cfg_content.append(line)
            f.seek(0)
            for line in cfg_content:
                f.write(line)

    return oci.config.from_file(file_location=f"./{sys.argv[1]}"), ssh_authorized_keys


def main():
    launch(*get_config())


if __name__ == '__main__':
    main()
