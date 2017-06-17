def create_instance(client, name, image_name, flavor_name, network_name, key_name):
    """ An instance of Cloud OS is made. 

    Args:
        client: Cloud OS client.
        name: Instance name.
        image_name: Instance image name.
        flavor_name: Instance flavor_name.
        network_name: Instance attach network_name.
        key_name: Security key name.
    Returns:
        client.servers.server: instance
    """
    image = client.images.find(name=image_name)
    flavor = client.flavors.find(name=flavor_name)
    net = client.networks.find(label=network_name)
    nics = [{'net-id': net.id}]
    instance = client.servers.create(
        name=name, image=image, flavor=flavor, key_name=key_name, nics=nics)
    return instance
