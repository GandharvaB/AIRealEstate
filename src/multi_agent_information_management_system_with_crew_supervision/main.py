#!/usr/bin/env python
import sys
from multi_agent_information_management_system_with_crew_supervision.crew import MultiAgentInformationManagementSystemWithCrewSupervisionCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'search_radius_miles': 'sample_value',
        'target_location': 'sample_value',
        'source_agents': 'sample_value',
        'client_type': 'sample_value',
        'min_price': 'sample_value',
        'max_price': 'sample_value',
        'zoning_type': 'sample_value',
        'minimum_acres': 'sample_value'
    }
    MultiAgentInformationManagementSystemWithCrewSupervisionCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'search_radius_miles': 'sample_value',
        'target_location': 'sample_value',
        'source_agents': 'sample_value',
        'client_type': 'sample_value',
        'min_price': 'sample_value',
        'max_price': 'sample_value',
        'zoning_type': 'sample_value',
        'minimum_acres': 'sample_value'
    }
    try:
        MultiAgentInformationManagementSystemWithCrewSupervisionCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MultiAgentInformationManagementSystemWithCrewSupervisionCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'search_radius_miles': 'sample_value',
        'target_location': 'sample_value',
        'source_agents': 'sample_value',
        'client_type': 'sample_value',
        'min_price': 'sample_value',
        'max_price': 'sample_value',
        'zoning_type': 'sample_value',
        'minimum_acres': 'sample_value'
    }
    try:
        MultiAgentInformationManagementSystemWithCrewSupervisionCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
