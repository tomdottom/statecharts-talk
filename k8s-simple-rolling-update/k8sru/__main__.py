import time
import logging
import os
from pprint import pprint

logging.basicConfig()
logger = logging.getLogger("k8sru")
# logger.setLevel(logging.DEBUG)

from sismic.io import import_from_yaml
from sismic.interpreter import Interpreter, Event
from sismic.clock import SimulatedClock as Clock
from sismic.helpers import run_in_background
import yaml

from k8sru import (
    context,
    utils,
    watch,
)


# Create the interpreter clock
clock = Clock()
clock.start()

# Load statechart from yaml file
sc_config_path = "./k8sru.yaml"
if not os.path.isabs(sc_config_path):
    sc_config_path = os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            sc_config_path,
        )
    )
k8sru = import_from_yaml(filepath=sc_config_path)

# Create an interpreter for this statechart
interpreter = Interpreter(
    k8sru,
    initial_context=context.initial_context,
    clock=clock
)


def _log_interpreter(step):
    pprint("-----------------------------------")
    pprint(interpreter.configuration)
    # print(interpreter.context)
    ctx = dict(
        # Context variables
        releases=interpreter.context["releases"],
        current=interpreter.context["current"],
        next=interpreter.context["next"],
    )
    pprint(ctx)



# Run the interpreter in its own thread
interpreter_thread = run_in_background(
    interpreter,
    delay=1,
    callback=_log_interpreter,
)


def new_config(filepath):
    with open(filepath) as fh:
        config = yaml.safe_load(fh)

    interpreter.queue(
        Event("new_config", config=config)
    )

config_path = "./config.yaml"
observer = watch.filepath(
    filepath=config_path,
    callback=new_config,
)

new_config(config_path)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    interpreter_thread.stop()
    observer.stop()

interpreter_thread.join()
observer.join()
