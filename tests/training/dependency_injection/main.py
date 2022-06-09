from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel


class SubState(BaseModel):
    cipa: str = "def-1"


class State(BaseModel):
    sub_state: SubState


class States(containers.DeclarativeContainer):
    sub_state = providers.Singleton(SubState)
    state = providers.Singleton(State, sub_state=sub_state)


class Strategy:
    def __init__(self, state: State):
        self.state = state

    def read_state(self):
        print(self.state)


@inject
def modify_state(sub_state: State = Provide[States.sub_state]):
    sub_state.cipa = "mod-1"


@inject
def main(state: State = Provide[States.state]):
    st = Strategy(state=state)
    modify_state()
    st.read_state()


if __name__ == '__main__':
    states = States()
    states.wire(modules=[__name__])
    main()