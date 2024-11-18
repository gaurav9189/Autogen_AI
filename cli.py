import click
from agents import AgentSystem

@click.command()
@click.option('--prompt', '-p', help='Initial prompt to start the workflow')
@click.option('--file', '-f', type=click.File('r'), help='File containing the initial prompt')
@click.option('--use-snowflake', is_flag=True, help='Use Snowflake agent for code execution')
def run_workflow(prompt, file, use_snowflake):
    if file:
        # Read the prompt from the file
        prompt = file.read()
    elif not prompt:
        # If neither prompt nor file is provided, raise an error
        raise click.UsageError("You must provide either a prompt or a file containing the prompt.")
    """Run the AI agents workflow with the given prompt and optional Snowflake support"""
    agent_system = AgentSystem()
    agent_system.start_workflow(prompt, use_snowflake)

if __name__ == '__main__':
    run_workflow()
