from lib.agents.agent import Agent
from lib.modules.dspy_modules import *
from typing import List
import dspy


class PromptAgent(Agent):
    def __init__(
        self,
        dspy_prog: dspy.Module,
        max_actions: int = 50,
        verbose: bool = False,
        logging: bool = False,
        previous_actions: List = [],
        previous_reasons: List = [],
        previous_responses: List = [],
        debug: bool = False,
    ):
        super().__init__(
            max_actions=max_actions,
            verbose=verbose,
            logging=logging,
            previous_actions=previous_actions,
            previous_reasons=previous_reasons,
            previous_responses=previous_responses,
        )
        self.debug = debug
        self.turbo = dspy.OpenAI(
            model="gpt-3.5-turbo",
            model_type="chat",
            temperature=1.0,
        )
        dspy.settings.configure(lm=self.turbo)
        self.dspy_prog = dspy_prog

    def previous_history(self):
        previous_history = []

        if len(self.previous_actions) == len(self.previous_responses):
            previous_history.extend(
                [
                    PreviousActionAndState(action=action, response=response)
                    for action, response in zip(
                        self.previous_actions, self.previous_responses
                    )
                ]
            )
        else:
            previous_history = [
                PreviousActionAndState(action=action, response=None)
                for action in self.previous_actions
            ]

        return previous_history

    def predict_action(self, objective, observation, url=None):
        dspy_response = self.dspy_prog(
            objective=objective,
            observation=observation,
            url=url,
            previous_actions=self.previous_history(),
        )

        self.turbo.inspect_history(1)

        action = dspy_response.next_action
        # reason = dspy_response.reasoning
        reason = "None"

        if self.verbose > 0:
            if self.verbose > 1:
                print(f"\n OBSERVATION: {observation}")
            print(f"\n OBJECTIVE: {objective}")
            print(f"\n URL: {url}")
            print(f"\n PREVIOUS HISTORY: {self.previous_history()}")
            # print(f"\n REASON: {reason}")
            print(f"\n ACTION: {action}")

        if self.debug:
            human_input = input()
            if human_input != "c":
                action = human_input
                reason = "None"

        self.update_history(action=action, reason=reason)
        return action, reason
