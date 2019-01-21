import logging

logger = logging.getLogger("k8sru.context")

from k8sru import actions
from k8sru import utils


initial_context = dict(
    # functions exposed in StateChart
    synced=actions.synced,
    load_config=actions.load_config,
    set_next=actions.set_next,
    rollout=actions.rollout,
    rename=actions.rename,
    revert=actions.revert,

    # Context variables
    config_path=utils.get_full_filepath(__file__, "../config.yaml"),
    releases=[],
    current=None,
    last=None,
)
