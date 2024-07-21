from enum import StrEnum
from typing import Literal
import re


class Action(StrEnum):
    CLICK = "click [id]"
    TYPE = "type [id] [content] [press_enter_after=0|1]"
    HOVER = "hover [id]"
    PRESS = "press [key_comb]"
    SCROLL = "scroll [direction=down|up]"
    SELECT = "select [id] [option]"
    NEW_TAB = "new_tab"
    TAB_FOCUS = "tab_focus [tab_index]"
    CLOSE_TAB = "close_tab"
    GOTO = "goto [url]"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    STOP = "stop [answer]"

'''
1. This function takes one arguments: Action value and returns the regex corresponding to the string e.g.
The regex corresponding to CLICK value "click [id]" is click \[(\d+)\]
'''
def get_regex_str(action: Action) -> str:
    if action == Action.CLICK:
        return r"click \[(\d+)\]"
    elif action == Action.TYPE:
        return r"type \[(\d+)\] \[(.*?)\] \[(\d+)\]"
    elif action == Action.HOVER:
        return r"hover \[(\d+)\]"
    elif action == Action.PRESS:
        return r"press \[(.*?)\]"
    elif action == Action.SCROLL:
        return r"scroll \[(down|up)\]"
    elif action == Action.SELECT:
        return r"select \[(\d+)\] \[(.*?)\]"
    elif action == Action.NEW_TAB:
        return r"new_tab"
    elif action == Action.TAB_FOCUS:
        return r"tab_focus \[(\d+)\]"
    elif action == Action.CLOSE_TAB:
        return r"close_tab"
    elif action == Action.GOTO:
        return r"goto \[(.*?)\]"
    elif action == Action.GO_BACK:
        return r"go_back"
    elif action == Action.GO_FORWARD:
        return r"go_forward"
    elif action == Action.STOP:
        return r"stop \[(.*?)\]"
    else:
        raise ValueError("Invalid action")

'''
This function takes a string as an argument and returns a value of type string.
The way it does is iterates through all the Action values, calls get_regex_str function for the value and then does a regex match.
when there is first value that has a regex match with the string, the matched string is returned.
'''
def parse_action(action_str: str) -> str:
    for action in Action:
        regex_pattern = get_regex_str(action)
        regex = re.compile(regex_pattern)
        match = regex.search(action_str)
        if match:
            return match.group(0)
    raise ValueError("Invalid action string")

class ModuleAction(StrEnum):
    FIND_DIRECTIONS = "find_directions [query]"
    SEARCH_NEAREST_PLACE = "search_nearest_place [query]"


AllActions = Literal[*[action.value for action in Action]]  # type: ignore
MapActions = Literal[
    Action.CLICK.value,  # type: ignore
    Action.TYPE.value,  # type: ignore
    Action.SCROLL.value,  # type: ignore
    Action.STOP.value,  # type: ignore
    Action.SELECT.value,  # type: ignore
    ModuleAction.FIND_DIRECTIONS.value,  # type: ignore
    ModuleAction.SEARCH_NEAREST_PLACE.value,  # type: ignore
]
FindDirectionActions = Literal[Action.CLICK.value, Action.TYPE.value, Action.SCROLL.value, Action.SELECT.value, Action.STOP.value]  # type: ignore
SearchNearestPlaceActions = Literal[
    Action.CLICK.value, Action.TYPE.value, Action.SCROLL.value, Action.SELECT.value, Action.STOP.value  # type: ignore
]

DESCRIPTIONS = {
    Action.CLICK.value: "This action clicks on an element with a specific id on the webpage.",
    Action.TYPE.value: "Use this to type the content into the field with id. By default, the 'Enter' key is pressed after typing unless press_enter_after is set to 0.",
    Action.HOVER.value: "Hover over an element with id.",
    Action.PRESS.value: "Simulates the pressing of a key combination on the keyboard (e.g., Ctrl+v).",
    Action.SCROLL.value: "Scroll the page up or down.",
    Action.NEW_TAB.value: "Open a new, empty browser tab.",
    Action.TAB_FOCUS.value: "Switch the browser's focus to a specific tab using its index.",
    Action.CLOSE_TAB.value: "Close the currently active tab.",
    Action.GOTO.value: "Navigate to a specific URL.",
    Action.GO_BACK.value: "Navigate to the previously viewed page.",
    Action.GO_FORWARD.value: "Navigate to the next page (if a previous 'go_back' action was performed).",
    Action.SELECT.value: "Select an option from a dropdown menu.",
    Action.STOP.value: "Issue this action when you believe the task is complete. If the objective is to find a text-based answer, provide the answer in the bracket.",
    ModuleAction.FIND_DIRECTIONS.value: "Find directions between two locations to answer the query.",
    ModuleAction.SEARCH_NEAREST_PLACE.value: "Search for the places near the query location.",
}

EXAMPLES = {
    Action.CLICK.value: "click [7]",
    Action.TYPE.value: "type [7] [Zoe] [1]",
    Action.HOVER.value: "hover [7]",
    Action.PRESS.value: "press [Ctrl+v]",
    Action.SCROLL.value: "scroll [down]",
    Action.TAB_FOCUS.value: "tab_focus [2]",
    Action.GOTO.value: "goto [https://www.google.com]",
    Action.STOP.value: "stop [The answer is 42]",
    Action.SELECT.value: "select [7] [option_2]",
    ModuleAction.FIND_DIRECTIONS.value: "find_directions [Check if the social security administration in pittsburgh can be reached in one hour by car from Carnegie Mellon University]",
    ModuleAction.SEARCH_NEAREST_PLACE.value: "search_nearest_place [Tell me the closest cafe(s) to CMU Hunt library]",
}
