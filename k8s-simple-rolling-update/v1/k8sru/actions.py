import logging

logger = logging.getLogger("k8sru.actions")

from k8sru.utils import (
    get_containers,
    get_labels_dict,
    get_labels,
    start_new_container,
)


import docker


def rename(context, event):
    context["current"] = context["next"]
    context["next"] = None


def rollout(context):
    logger.debug("Started Rollout")
    client = docker.from_env()

    # Get no. of 'next' containers
    next_config = context["releases"][context["next"]]
    next_containers_labels = get_labels(next_config)
    next_containers = get_containers(client, next_containers_labels)
    next_containers_count = len(next_containers)
    logger.debug(f"next_containers #: {next_containers_count}")

    # Add a new one if needed
    if next_containers_count < next_config["replicas"]:
        start_new_container(client, next_config)
    # Remove one if needed
    elif next_containers_count > next_config["replicas"]:
        container = next_containers.pop()
        container.remove(force=True)

    # Refresh list
    next_containers = get_containers(client, next_containers_labels)

    # Get no. of 'current' containers
    other_containers = get_containers(client, ["k8sru=True"])
    for container in next_containers:
        other_containers.remove(container)
    logger.debug(f"other_containers #: {len(other_containers)}")


    # Remove one if any available
    if len(other_containers) > 0:
        other_containers[0].remove(force=True)

    # Refresh list
    other_containers = get_containers(client, ["k8sru=True"])
    for container in next_containers:
        other_containers.remove(container)

    logger.debug(f"next_containers #: {next_containers_count}")
    logger.debug(f"other_containers #: {len(other_containers)}")
    if (len(other_containers) == 0
           and len(next_containers) == next_config["replicas"]):
        context["rollout_finished"] = True


def set_next(context, event):
    context["releases"].append(event.config)
    release_id = len(context["releases"]) - 1
    context["next"] = release_id

    logger.debug(f"Next release id: {release_id}")
