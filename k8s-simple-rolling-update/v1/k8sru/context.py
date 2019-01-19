import logging

logger = logging.getLogger("k8sru.context")

from k8sru.actions import (
    rename,
    rollout,
    set_next,
)


initial_context = dict(
    # functions exposed in StateChart
    set_next=set_next,
    rollout=rollout,
    rename=rename,

    # Context variables
    releases=[],
    current=None,
    next=None,
)
