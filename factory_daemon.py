import click
import sys
import os.path

from daemons import WorkerDaemon, MasterDaemon


@click.command()
@click.option("--operator", "-o", required=True, prompt="Which Operator type?", type=click.Choice(["master", "worker"]),
              help="MASTER or WORKER")
@click.option("--configuration_location", "-c", default="../", prompt="Conf.yaml location",
              help="The conf.yaml is used the instantiate workers and operators.")
def start(operator, configuration_location):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo(f"Instantiating new operator {operator} with settings {configuration_location}!")
    operator = operator.upper()
    active_operator = None
    if operator == "WORKER":
        return WorkerDaemon(config_path=configuration_location)
    if operator == "MASTER":
        return MasterDaemon(config_path=configuration_location)

    return active_operator


if __name__ == '__main__':
    op = None
    while True:
        opt = start()
        if opt is not None:
            op = opt
            break
    op.boot()
    op.main()
