"""aivcs — an AI-native version control system.

Core objects (see Core Specifications):
  Specification        -> aivcs.spec.SpecStore
  Primitive agent spec  -> aivcs.agents.PrimitiveAgentSpec
  Compounded agent      -> aivcs.agents.CompoundedAgentSpec
  Session               -> aivcs.session.SessionRunner / SessionRecord
  Contract              -> aivcs.models.Contract
  Test suite            -> external; invoked by aivcs.bisect and the CLI's `check` command
"""

__version__ = "0.1.0"
