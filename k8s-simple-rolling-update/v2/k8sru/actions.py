import logging

logger = logging.getLogger("k8sru.actions")

import yaml

from k8sru.utils import (
    get_containers,
    get_labels_dict,
    get_labels,
    start_new_container,
)


import docker


def synced(context):
    client = docker.from_env()

    # Get no. of 'current' containers
    current_config = context["releases"][context["current"]]
    current_containers_labels = get_labels(current_config)
    current_containers = get_containers(client, current_containers_labels)

    # Get no. of 'current' containers
    other_containers = get_containers(client, ["k8sru=True"])
    for container in current_containers:
        other_containers.remove(container)

    return len(other_containers) == 0 and len(current_containers) == current_config["replicas"]



def load_config(context):
    with open(context["config_path"]) as fh:
        config = yaml.safe_load(fh)
    context["releases"].append(config)
    release_id = len(context["releases"]) - 1
    context["current"] = context["last"] = release_id


def rename(context, event):
    context["last"] = context["current"]


def revert(context, event):
    context["current"] = context["last"]


def rollout(context):
    logger.debug("Started Rollout")
    client = docker.from_env()

    # Get no. of 'current' containers
    current_config = context["releases"][context["current"]]
    current_containers_labels = get_labels(current_config)
    current_containers = get_containers(client, current_containers_labels)
    current_containers_count = len(current_containers)
    logger.debug(f"current_containers #: {current_containers_count}")

    # Add a new one if needed
    if current_containers_count < current_config["replicas"]:
        start_new_container(client, current_config)
    # Remove one if needed
    elif current_containers_count > current_config["replicas"]:
        container = current_containers.pop()
        container.remove(force=True)

    # Refresh list
    current_containers = get_containers(client, current_containers_labels)

    # Get no. of 'other' containers
    other_containers = get_containers(client, ["k8sru=True"])
    for container in current_containers:
        other_containers.remove(container)
    logger.debug(f"other_containers #: {len(other_containers)}")


    # Remove one if any available
    if len(other_containers) > 0:
        other_containers[0].remove(force=True)

    # Refresh list
    other_containers = get_containers(client, ["k8sru=True"])
    for container in current_containers:
        other_containers.remove(container)

    logger.debug(f"current_containers #: {current_containers_count}")
    logger.debug(f"other_containers #: {len(other_containers)}")
    if (len(other_containers) == 0
           and len(current_containers) == current_config["replicas"]):
        context["rollout_finished"] = True


def set_next(context, event):
    context["releases"].append(event.config)
    release_id = len(context["releases"]) - 1
    context["last"] = context["current"]
    context["current"] = release_id

    logger.debug(f"Next release id: {release_id}")
