from typing import List


class Agent:
    def __init__(
        self,
        max_actions: int,
        verbose: bool = False,
        logging: bool = False,
        previous_actions: List[str] = [],
        previous_reasons: List[str] = [],
        previous_responses: List[str] = [],
    ):
        self.previous_actions = previous_actions
        self.previous_reasons = previous_reasons
        self.previous_responses = previous_responses
        self.max_actions = max_actions
        self.verbose = verbose
        self.logging = logging
        self.trajectory = []
        self.data_to_log = {}

    def reset(self):
        self.previous_actions = []
        self.previous_reasons = []
        self.previous_responses = []
        self.trajectory = []
        self.data_to_log = {}

    def get_trajectory(self):
        return self.trajectory

    def update_history(self, action, reason):
        if action:
            self.previous_actions += [action]
        if reason:
            self.previous_reasons += [reason]

    def predict_action(self, objective, observation, url=None):
        pass

    def receive_response(self, response):
        self.previous_responses += [response]

    def act(self, objective, env):
        while not env.done():
            observation = env.observation()
            action, reason = self.predict_action(
                objective=objective, observation=observation, url=env.get_url()
            )  # type: ignore
            status = env.step(action)

            if self.logging:
                self.log_step(
                    objective=objective,
                    url=env.get_url(),
                    observation=observation,
                    action=action,
                    reason=reason,
                    status=status,
                )

            if len(self.previous_actions) >= self.max_actions:
                print(f"Agent exceeded max actions: {self.max_actions}")
                break

        return status

    def log_step(self, objective, url, observation, action, reason, status):
        self.data_to_log["objective"] = objective
        self.data_to_log["url"] = url
        self.data_to_log["observation"] = observation
        self.data_to_log["previous_actions"] = self.previous_actions[:-1]
        self.data_to_log["previous_responses"] = self.previous_responses[:-1]
        self.data_to_log["previous_reasons"] = self.previous_reasons[:-1]
        self.data_to_log["action"] = action
        self.data_to_log["reason"] = reason
        for k, v in status.items():
            self.data_to_log[k] = v
        self.trajectory.append(self.data_to_log)
        self.data_to_log = {}
