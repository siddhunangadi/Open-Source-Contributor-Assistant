# scratch/run_agent_cli.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agents.supervisor import SupervisorAgent
from models.initial_state import create_initial_state

def main():
    goal = "Investigate the issue 'Python classes not found' #47 in osslab-pku/gfi-bot. Retrieve actual relevant source files, analyze dependency impact, and write an evidence-backed contribution plan with GitHub links for every verified claim."
    print("Initializing Agent State...")
    state = create_initial_state(goal)
    
    agent = SupervisorAgent()
    print("Running autonomous agent loop...")
    final_state = agent.run(state)
    
    print("\n" + "="*80)
    print("FINAL RECOMMENDATION RESULT")
    print("="*80)
    print(final_state.get("final_answer"))
    print("="*80)

if __name__ == "__main__":
    main()
