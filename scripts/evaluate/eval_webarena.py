import os

os.environ["DSP_CACHEDIR"] = "local_cache"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAPI_PERSONAL", "")

import glob
import json
import re
import pandas as pd
from lib.agents.step_agent import StepAgent
from lib.environments.webarena import WebArenaEnvironmentWrapper


def log_run(
    log_file, log_data, summary_file=None, summary_data=None, json_indent=4, verbose=1
):
    """
    Logs demo data to a JSON file and optionally updates a summary CSV file.
    """
    # Write log data to JSON file
    with open(log_file, "w") as json_file:
        json.dump(log_data, json_file, indent=json_indent)
    if verbose:
        print(f"Saved log to {log_file}")

    # If summary data and file path are provided, update the summary
    if summary_data and summary_file:
        if os.path.exists(summary_file):
            df_summary = pd.read_csv(summary_file)
        else:
            df_summary = pd.DataFrame()
        df_summary = pd.concat(
            [df_summary, pd.DataFrame([summary_data])], ignore_index=True
        )
        df_summary.to_csv(summary_file, index=False)
        if verbose:
            print(f"Updated summary: {df_summary}")

        return df_summary


def run():
    config_file_list = glob.glob("config_data/*.json")

    dstdir = "output_data"

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
            slow_mo=0,
            observation_type="accessibility_tree",
            current_viewport_only=False,
            viewport_size={"width": 1920, "height": 1080},
            headless=True,
        )

        agent = agent_init()
        objective = env.get_objective()
        status = agent.act(objective=objective, env=env)
        env.close()

        with open(config_file, "r") as f:
            task_config = json.load(f)
        log_file = os.path.join(dstdir, f"{task_config['task_id']}.json")
        log_data = {
            "task": config_file,
            "id": task_config["task_id"],
            "model": "gpt_4o",
            "type": "step_agent",
            "trajectory": agent.get_trajectory(),
        }
        summary_file = os.path.join(dstdir, "summary.csv")
        summary_data = {
            "task": config_file,
            "task_id": task_config["task_id"],
            "model": "gpt_4o",
            "type": "step_agent",
            "logfile": log_file,
        }
        summary_data.update(status)
        log_run(
            log_file=log_file,
            log_data=log_data,
            summary_file=summary_file,
            summary_data=summary_data,
        )


if __name__ == "__main__":
    run()
