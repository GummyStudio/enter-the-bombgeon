import bascenev1
from .characters import (
    internal as _,
    _loader as _,
)
from .characters.internal import apply_bombgeon_roster

# FIXME: we shouldnt be doing this...
bascenev1.apptimer(1, apply_bombgeon_roster)

print("Enter the Bombgeon module loaded.")
