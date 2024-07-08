import json
import re

# Init an environment
from browser_env import (
    create_id_based_action,
    create_playwright_action,
    StateInfo,
    Trajectory,
    ActionTypes,
    ScriptBrowserEnv,
)
from evaluation_harness.evaluators import evaluator_router


class WebArenaEnvironmentWrapper:
    def __init__(
        self,
        config_file,
        max_browser_rows=300,
        max_steps=50,
        slow_mo=1,
        observation_type="accessibility_tree",
        current_viewport_only=False,
        viewport_size={"width": 1280, "height": 720},
        headless=False,
    ):
        self.webarena_env = ScriptBrowserEnv(
            headless=headless,
            slow_mo=slow_mo,
            observation_type=observation_type,
            current_viewport_only=current_viewport_only,
            viewport_size=viewport_size,
        )
        self.config_file = config_file
        with open(self.config_file, "r") as f:
            self.config = json.load(f)

        self.obs, self.info = self.webarena_env.reset(
            options={"config_file": self.config_file}
        )
        self.terminated = False
        self.objective = self.config["intent"]
        self.url = self.config["start_url"]
        self.max_browser_rows = max_browser_rows
        self.max_steps = max_steps
        self.steps = 0
        self.is_done = False
        self.reward = 0.0
        self.action_limit_exceeded = False

        self.trajectory: Trajectory = []
        self.update_webarena_metrics()

    def reset(self):
        self.obs, self.info = self.webarena_env.reset(
            options={"config_file": self.config_file}
        )

    def close(self):
        self.webarena_env.close()

    def get_url(self):
        return self.url

    def get_objective(self):
        return self.objective

    def observation(self):
        self.obs = self.webarena_env._get_obs()
        self.url = self.webarena_env.page.url
        browser_content = self.obs["text"]
        browser_content = browser_content.split("\n")[: self.max_browser_rows]  # type: ignore
        browser_content = "\n".join(browser_content)
        return browser_content

    def done(self):
        if self.is_done:
            return True
        return False

    def status(self):
        return {
            "done": self.is_done,
            "reward": self.reward,
            "success": float(self.reward > 0),
            "num_actions": self.steps,
            "action_limit_exceeded": self.action_limit_exceeded,
        }

    def step(self, action):
        self.steps = self.steps + 1
        print(f"[Step {self.steps}] {action}")

        self.webarena_env.page.screenshot(path=f"Step {self.steps - 1}.png")

        if self.steps > self.max_steps:
            print(f"Steps {self.steps} exceeded maximum {self.max_steps}")
            self.action_limit_exceeded = True
            self.is_done = True
            action_cmd = self.call_right_action("stop [N/A]")
            self.update_webarena_metrics(action_cmd)
            return self.status()

        if "stop [" in action:
            action = action.replace("\\", "")

        if action is None or action is "" or ("note [" in action):
            action_cmd = None
        else:
            action_cmd = self.call_right_action(action)

        if action_cmd:
            try:
                self.obs, _, self.terminated, _, self.info = self.webarena_env.step(
                    action_cmd
                )
                self.update_webarena_metrics(action_cmd)
            except Exception as e:
                print(f"Error occurred while taking step: {e}")

        self.webarena_env.page.screenshot(path=f"Step {self.steps}.png")

        return self.status()

    def update_webarena_metrics(self, action_cmd=None):
        # Append action (if any) and resulting sate
        if action_cmd:
            self.trajectory.append(action_cmd)
            if action_cmd["action_type"] == ActionTypes.STOP:
                self.is_done = True

        if not self.is_done:  # If we are done, no need to append state
            state_info: StateInfo = {"observation": self.obs, "info": self.info}
            self.trajectory.append(state_info)

        if self.is_done:
            try:
                evaluator = evaluator_router(self.config_file)
                self.reward = evaluator(
                    trajectory=self.trajectory,
                    config_file=self.config_file,
                    page=self.webarena_env.page,
                    client=self.webarena_env.get_page_client(self.webarena_env.page),
                )
            except Exception as e:
                print(f"Got excepetion: {e}")
                self.reward = 0

    def call_right_action(self, action_str):
        if "select" in action_str:
            pattern = r"select \[(\d+)\] \[(.+)\]"
            match = re.search(pattern, action_str)
            if match:
                option = match.group(2)
                output_string = (
                    f'page.get_by_role("combobox").select_option("{option}")'
                )
                return create_playwright_action(output_string)
            else:
                return create_id_based_action(action_str)
        else:
            return create_id_based_action(action_str)
