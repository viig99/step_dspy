import os

os.environ["DSP_CACHEDIR"] = "local_cache"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAPI_PERSONAL", "")

import glob
from lib.agents.step_agent import StepAgent
from lib.environments.webarena import WebArenaEnvironmentWrapper


def run():
    config_file_list = glob.glob("config_data/*.json")

    agent_init = lambda: StepAgent(
        max_actions=50,
        verbose=True,
        logging=True,
        debug=False,
    )

    #####
    # Evaluate
    #####

    for config_file in config_file_list:
        env = WebArenaEnvironmentWrapper(
            config_file=config_file,
            max_steps=50,
            slow_mo=1,
            observation_type="accessibility_tree",
            current_viewport_only=True,
            viewport_size={"width": 1920, "height": 1080},
            headless=False,
        )

        agent = agent_init()
        objective = env.get_objective()
        status = agent.act(objective=objective, env=env)
        env.close()


if __name__ == "__main__":
    run()
