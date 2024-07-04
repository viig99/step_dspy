import os

os.environ["DSP_CACHEDIR"] = "local_cache"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAPI_PERSONAL", "")

from lib.agents.step_agent import StepAgent
from lib.environments.webarena import WebArenaEnvironmentWrapper


def run():
    agent_init = lambda: StepAgent(
        max_actions=50,
        verbose=True,
        logging=True,
        debug=False,
    )

    #####
    # Evaluate
    #####

    config_file = "config_data/366.json"

    # config_file = "config_data/379.json"

    env = WebArenaEnvironmentWrapper(
        config_file=config_file,
        max_steps=50,
        max_browser_rows=500,
        slow_mo=0,
        observation_type="accessibility_tree",
        current_viewport_only=False,
        viewport_size={"width": 1280, "height": 720},
        headless=False,
    )

    agent = agent_init()
    objective = env.get_objective()
    status = agent.act(objective=objective, env=env)
    env.close()


if __name__ == "__main__":
    run()
