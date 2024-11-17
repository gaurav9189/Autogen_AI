import click
from agents import AgentSystem

@click.command()
@click.option('--prompt', '-p', required=True, help='Initial prompt to start the workflow')
def run_workflow(prompt):
    """Run the AI agents workflow with the given prompt"""
    agent_system = AgentSystem()
    agent_system.start_workflow(prompt)

if __name__ == '__main__':
    run_workflow()
