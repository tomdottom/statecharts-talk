import time
import logging
import os
from pprint import pprint
import signal

logging.basicConfig()
logger = logging.getLogger("k8sru")
if os.environ.get("DEBUG"):
    logger.setLevel(logging.DEBUG)

from sismic.io import import_from_yaml
from sismic.interpreter import Interpreter, Event
from sismic.clock import SimulatedClock as Clock
from sismic.runner import AsyncRunner
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
statechart_path = utils.get_full_filepath(__file__, "./statechart.yaml")
statechart = import_from_yaml(filepath=statechart_path)

# Create an interpreter for this statechart
interpreter = Interpreter(
    statechart,
    initial_context=context.initial_context,
    clock=clock
)

class Runner(AsyncRunner):

    def after_execute(self, step):
        pprint("-----------------------------------")
        events = [
            s.event.name
            for s in step
            if s is not None and s.event is not None
        ]

        print("Events:     ", end="")
        pprint(events)
        print("States:     ", end="")
        pprint(interpreter.configuration[-2:])
        # print(interpreter.context)
        ctx = dict(
            # Context variables
            releases=interpreter.context["releases"],
            current=interpreter.context["current"],
            last=interpreter.context["last"],
        )
        print("Context:")
        pprint(ctx, indent=12)



# Run the interpreter in its own thread
interpreter_thread = Runner(
    interpreter,
    interval=0.5,
)
interpreter_thread.start()


def new_config(filepath):
    logger.debug("Reading config and generating event")
    with open(filepath) as fh:
        config = yaml.safe_load(fh)

    interpreter.queue(
        Event("new config", config=config)
    )


# Watch the config file in a background thread
print(context.initial_context["config_path"])
observer = watch.filepath(
    filepath=context.initial_context["config_path"],
    callback=new_config,
)


# Capture ctrl+\ keypress
def abort_event(signum, frame):
    interpreter.queue(
        Event("abort")
    )
signal.signal(signal.SIGQUIT, abort_event)


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    interpreter_thread.stop()
    observer.stop()
    observer.join()
