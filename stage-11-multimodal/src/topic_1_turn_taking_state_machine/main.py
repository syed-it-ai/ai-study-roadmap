"""
Confirmed as current practice for realtime voice: modern turn-taking
uses semantic voice activity detection, judging whether a speaker has
actually finished a thought rather than waiting on a fixed silence
timer, so the agent interrupts less and replies sooner. Barge-in, a
caller interrupting the agent mid-response, is handled as its own
explicit state transition, not an edge case bolted on afterward.

This is a real state machine, not a description of one. Every
transition is a method call with a visible before-and-after state.
"""

from enum import Enum, auto


class State(Enum):
    LISTENING = auto()        # waiting for the user to speak
    USER_SPEAKING = auto()    # user is mid-utterance
    PROCESSING = auto()       # user finished, agent is generating a response
    AGENT_SPEAKING = auto()   # agent's response is playing back


class TurnTakingMachine:
    """
    Models the actual state transitions a realtime voice pipeline has
    to manage. Confirmed current practice: end-of-turn is a semantic
    judgment (did they finish a thought), not a fixed silence timer,
    modeled here as an explicit signal rather than a timeout.
    """

    def __init__(self):
        self.state = State.LISTENING
        self.transition_log = []

    def _transition(self, new_state: State, reason: str):
        old_state = self.state
        self.state = new_state
        self.transition_log.append((old_state, new_state, reason))

    def user_starts_speaking(self):
        if self.state == State.LISTENING:
            self._transition(State.USER_SPEAKING, "user started speaking")
        elif self.state == State.AGENT_SPEAKING:
            # This is barge-in: the user interrupts the agent mid-response.
            self._transition(State.USER_SPEAKING, "BARGE-IN: user interrupted agent mid-response")

    def semantic_end_of_turn_detected(self):
        """
        The key current-practice detail: this fires when the model
        judges the user has finished a complete thought, not merely
        when they've paused. A fixed silence timer would fire on any
        brief pause, including mid-sentence ones, cutting users off.
        """
        if self.state == State.USER_SPEAKING:
            self._transition(State.PROCESSING, "semantic end-of-turn: user finished a complete thought")

    def agent_starts_responding(self):
        if self.state == State.PROCESSING:
            self._transition(State.AGENT_SPEAKING, "agent began speaking its response")

    def agent_finishes_responding(self):
        if self.state == State.AGENT_SPEAKING:
            self._transition(State.LISTENING, "agent finished, back to listening")


def main() -> None:
    machine = TurnTakingMachine()

    print("=== Normal turn, no interruption ===\n")
    machine.user_starts_speaking()
    machine.semantic_end_of_turn_detected()
    machine.agent_starts_responding()
    machine.agent_finishes_responding()
    for old, new, reason in machine.transition_log:
        print(f"  {old.name:15s} -> {new.name:15s} | {reason}")

    print("\n=== A second conversation turn, this time with barge-in ===\n")
    machine2 = TurnTakingMachine()
    machine2.user_starts_speaking()
    machine2.semantic_end_of_turn_detected()
    machine2.agent_starts_responding()
    # The user interrupts while the agent is still mid-response.
    machine2.user_starts_speaking()
    for old, new, reason in machine2.transition_log:
        print(f"  {old.name:15s} -> {new.name:15s} | {reason}")

    print(
        "\nThe barge-in transition goes directly from AGENT_SPEAKING to "
        "USER_SPEAKING, skipping LISTENING entirely. The caller loses the "
        "turn that was in flight, confirmed as how current providers handle "
        "this: barge-in is decided by the provider's own voice activity "
        "detection, and the agent's in-progress response is simply cut off, "
        "not queued or resumed."
    )
    print(
        "\nThe semantic end-of-turn check is the detail that actually "
        "matters for how natural the conversation feels. A fixed silence "
        "timer fires on any pause, including the kind a person makes "
        "mid-sentence while thinking. Judging whether a complete thought "
        "was finished is what lets the agent reply at a natural moment "
        "instead of either cutting the user off or leaving an awkward gap."
    )


if __name__ == "__main__":
    main()
