# graph/workflow.py

from agents.supervisor import SupervisorAgent
from models.state import AgentState


class OpenSourceContributionWorkflow:
    """
    Compatibility launcher.

    It does NOT control tool order.
    It does NOT contain a pipeline.
    It does NOT execute tools.

    The SupervisorAgent owns:
    think → choose tool → execute → observe → reflect → finish
    """

    def __init__(self):
        self.agent = SupervisorAgent()

    def run(self, initial_state: AgentState) -> AgentState:
        """
        Start one autonomous agent run.
        """

        return self.agent.run(initial_state)