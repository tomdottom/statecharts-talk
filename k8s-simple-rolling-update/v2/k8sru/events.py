import yaml


def new_config(filepath):
    with open(filepath) as fh:
        config = yaml.safe_load(fh)

    interpreter.queue(
        Event("new_config", config=config)
    )
