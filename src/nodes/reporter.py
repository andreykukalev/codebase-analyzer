from state import State

class ReporterNode:
    """A node that builds the report by documenting all extracted business requirements"""

    def __init__(self) -> None:
        return None
    
    def __call__(self, state: State):
        return {"messages": [""]}
    

