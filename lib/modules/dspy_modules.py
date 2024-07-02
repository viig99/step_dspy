from typing import Optional
import dspy
from pydantic import BaseModel
from lib.modules.data_models import *


class PreviousActionAndState(BaseModel):
    action: str
    response: Optional[str] = None

    def __repr__(self) -> str:
        return f'action="{self.action}", response={self.response}'

    def __str__(self) -> str:
        return f'action="{self.action}", response={self.response}'


def get_action_description(action_literal) -> str:
    valid_actions = [v for v in action_literal.__dict__["__args__"]]
    return "\n".join(
        [
            f"{action}: {DESCRIPTIONS[action]}, example: {EXAMPLES.get(action, '')}"
            for action in DESCRIPTIONS
            if action in valid_actions
        ]
    )


class PredictNextAction(dspy.Signature):
    f"""Predict the next action to be performed by the web agent performing tasks on a web browser.
    """

    objective: str = dspy.InputField(
        title="Objective",
        description="The objective of the task that the web agent is trying to accomplish.",
    )
    observation: str = dspy.InputField(
        title="Observation",
        description="A simplified text description of the current browser content, without formatting elements.",
    )
    url: str = dspy.InputField(
        title="URL",
        description="The URL of the current webpage.",
    )
    previous_actions: list[PreviousActionAndState] = dspy.InputField(
        title="Previous Actions",
        description="A list of your past actions with an optional reponse.",
    )
    next_action = dspy.OutputField(
        title="Next Action",
        description=f"""The next action to be performed by the web agent to accomplish the objective.
        The action can be one of the following:
        {get_action_description(AllActions)}
        """,
    )


class MapAction(PredictNextAction):
    f"""Predict the next action to be performed by the web agent performing tasks on a web browser.
    1. If the OBJECTIVE is about finding directions from A to B, you MUST use find_directions [] subroutine.
        e.g. find_directions [Check if the social security administration in pittsburgh can be reached in one hour by car from Carnegie Mellon University]
    2. If the OBJECTIVE is about searching nearest place to a location, you MUST use search_nearest_place [] subroutine.
        e.g. search_nearest_place [Tell me the closest restaurant(s) to Cohon University Center at Carnegie Mellon University]
    3. If the OBJECTIVE is to pull up a description, once that place appears in the sidepane, return stop [N/A]
    4. Return only one action at a time, e.g. click [7]
    5. Return exactly as specified in the examples format. 
    """
    next_action = dspy.OutputField(
        title="Next Action",
        description=f"""The next action to be performed by the web agent to accomplish the objective.
        The action can be one of the following:
        {get_action_description(MapActions)}
        """,
    )


class FindDirectionAction(PredictNextAction):
    f"""Predict the next action to be performed by the web agent performing tasks on a web browser.
    Please follow these instructions to solve the subtask:
    1. First click on "Find directions between two points", then enter From and To Fields, and click search.
    2. If you have to find directions to social security administration in Pittsburgh, search for it in a structured format like Social Security Administration, Pittsburgh.
    3. Return only one action at a time, e.g. click [7]
    4. Return exactly as specified in the examples format.
    """
    next_action = dspy.OutputField(
        title="Next Action",
        description=f"""The next action to be performed by the web agent to accomplish the objective.
        The action can be one of the following:
        {get_action_description(FindDirectionActions)}
        """,
    )


class SearchNearestPlaceAction(PredictNextAction):
    f"""Predict the next action to be performed by the web agent performing tasks on a web browser.
    Please follow these instructions to solve the subtask:
    1. For searches that refer to CMU, e.g.  "find cafes near CMU Hunt Library"
        a. You have to first center your map around a location. If you have to find cafes near CMU Hunt Library, the first step is to make sure the map is centered around Carnegie Mellon University. To do that, first search for Carnegie Mellon University and then click [] on a list of location that appears. You MUST click on the Carnegie Mellon University location to center the map. Else the map will not centered. E.g click [646]
        b. Now that your map is centered around Carnegie Mellon University, directly search for "cafes near Hunt Library". Do not include the word CMU in the search item. The word CMU cannot be parsed by maps and will result in an invalid search.
        c. When your search returns a list of elements, return them in a structured format like stop [A, B, C]
    2. For searches that don't refer to CMU
        a. No need to center the map. Directly search what is specified in OBJECTIVE, e.g. "bars near Carnegie Music Hall"
        b. When your search returns a list of elements, return them in a structured format like stop [A, B, C]
    3. Be sure to double check whether the OBJECTIVE has CMU or not and then choose between instruction 1 and 2. 
    4. Remember that the word CMU cannot be typed in the search bar as it cannot be parsed by maps. 
    5. Remember that if you want to center your map around Carnegie Mellon University, you have to click on it after you search for it. Check your PREVIOUS ACTIONS to confirm you have done so, e.g. click [646] should be in the previous actions.
    6. Return only one action at a time, e.g. click [7]
    7. Return exactly as specified in the examples format.
    """
    next_action = dspy.OutputField(
        title="Next Action",
        description=f"""The next action to be performed by the web agent to accomplish the objective.
        The action can be one of the following:
        {get_action_description(SearchNearestPlaceActions)}
        """,
    )


class MapPlanningModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.TypedChainOfThought(signature=MapAction, max_retries=5)

    def forward(
        self,
        objective: str,
        observation: str,
        url: str,
        previous_actions: list[PreviousActionAndState],
    ):
        return self.prog(
            objective=objective,
            observation=observation,
            url=url,
            previous_actions=previous_actions,
        )


class FindDirectionModule(MapPlanningModule):
    def __init__(self):
        super().__init__()
        self.prog = dspy.TypedChainOfThought(
            signature=FindDirectionAction, max_retries=5
        )


class SearchNearestPlaceModule(MapPlanningModule):
    def __init__(self):
        super().__init__()
        self.prog = dspy.TypedChainOfThought(
            signature=SearchNearestPlaceAction, max_retries=5
        )
