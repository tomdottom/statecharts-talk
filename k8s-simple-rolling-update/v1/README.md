# K8s Simple Rolling Update


## Setup

    pipenv shell
    pipenv sync --dev


## Running the example

*Terminal 1*

    watch -n1 docker ps

*Terminal 2*

    python -m k8sru

*Editor*

    Update and save config.yaml

What you will see:
- Upon saving config.yaml a new_config event will be sent to the k8sru interpreter.
- The interpreter will proceed through the states/steps to ensure the running containers match the config.
- The watch on the docker container list will show the new containers starting/stopping.
