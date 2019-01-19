from copy import deepcopy
from time import sleep
import logging

logger = logging.getLogger("k8sru.utils")


def get_containers(client, labels=None):
    labels = labels or []
    return client.containers.list(
        filters=dict(label=labels))


def get_labels_dict(config):
    label_dict = dict(
        (f"k", f"v")
        for (k, v) in config.items()
    )
    label_dict.update({"k8sru": "True"})
    return label_dict


def get_labels(config):
    label_dict = get_labels_dict(config)
    return [f"{k}={v}" for (k, v) in label_dict.items()]


def start_new_container(client, config):
    logger.debug("Starting new container")
    client.containers.run(
        image=config["image"],
        entrypoint=["sh", "-c", "tail -f /dev/null"],
        detach=True,
        labels=get_labels_dict(config),
    )
