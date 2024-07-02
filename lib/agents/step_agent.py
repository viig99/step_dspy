from lib.agents.agent import Agent
from lib.utils.stack import Stack
from lib.agents.dspy_agent import PromptAgent
from lib.modules.dspy_modules import (
    MapPlanningModule,
    FindDirectionModule,
    SearchNearestPlaceModule,
)

from typing import List, Dict
import re


class StepAgent(Agent):
    def __init__(
        self,
        max_actions: int = 50,
        verbose: bool = False,
        logging: bool = False,
        previous_actions: List[str] = [],
        debug: bool = False,
        root_action: str = "map_planner",
        action_to_prompt_dict: Dict = {
            "map_planner": MapPlanningModule(),
            "find_directions": FindDirectionModule(),
            "search_nearest_place": SearchNearestPlaceModule(),
        },
    ):
        super().__init__(
            max_actions=max_actions,
            verbose=verbose,
            logging=logging,
            previous_actions=previous_actions,
        )
        self.debug = debug
        self.root_action = root_action
        self.action_to_prompt_dict = action_to_prompt_dict
        self.stack = Stack()

    def is_done(self, action):
        return "stop" in action.lower()

    def is_high_level_action(self, action):
        return any(filter(lambda x: x in action, self.action_to_prompt_dict.keys()))

    def is_low_level_action(self, action):
        return not self.is_high_level_action(action)

    def init_root_agent(self, objective):
        dspy_prog = self.action_to_prompt_dict[self.root_action]
        agent = PromptAgent(
            dspy_prog=dspy_prog,
            max_actions=self.max_actions,
            verbose=self.verbose,
            logging=self.logging,
            debug=self.debug,
            previous_actions=[],
            previous_reasons=[],
            previous_responses=[],
        )
        return {"agent": agent, "objective": objective}

    def init_agent(self, action):
        pattern = r"(\w+)\s+\[(.*?)\]"
        matches = re.findall(pattern, action)
        action_type, _ = matches[0]
        objective = action
        dspy_prog = self.action_to_prompt_dict[action_type]
        agent = PromptAgent(
            dspy_prog=dspy_prog,
            max_actions=self.max_actions,
            verbose=self.verbose,
            logging=self.logging,
            debug=self.debug,
            previous_actions=[],
            previous_reasons=[],
            previous_responses=[],
        )
        return {"agent": agent, "objective": objective}

    def predict_action(self, objective, observation, url=None):
        if self.stack.is_empty():
            new_element = self.init_root_agent(objective=objective)
            self.stack.push(new_element)

        action, reason = None, None
        while not self.stack.is_empty():
            element = self.stack.peek()
            action, reason = element["agent"].predict_action(
                objective=element["objective"], observation=observation, url=url
            )
            if (not self.is_done(action)) and self.is_low_level_action(action):
                element["agent"].receive_response("")
                return action, reason
            if (not self.is_done(action)) and self.is_high_level_action(action):
                new_element = self.init_agent(action)
                self.stack.push(new_element)
                if self.logging:
                    self.log_step(
                        objective=element["objective"],
                        url=url,
                        observation=observation,
                        action=action,
                        reason=reason,
                        status={},
                    )
                continue
            if self.is_done(action):
                self.stack.pop()
                if not self.stack.is_empty():
                    self.stack.peek()["agent"].receive_response(
                        re.search(r"\[(.*?)\]", action).group(1)  # type: ignore
                    )
                if self.logging:
                    self.log_step(
                        objective=element["objective"],
                        url=url,
                        observation=observation,
                        action=action,
                        reason=reason,
                        status={},
                    )
                continue
        return action, reason
