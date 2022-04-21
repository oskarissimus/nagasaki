from typing import List

from nagasaki.models.bitclude import Action as BitcludeAction
from nagasaki.database.database import SessionLocal
from nagasaki.database.models import Action


def dump_actions_to_db(actions: List[BitcludeAction]):
    actions = [Action.from_action(action) for action in actions]
    with SessionLocal() as session:
        for action in actions:
            session.add(action)
        session.commit()
