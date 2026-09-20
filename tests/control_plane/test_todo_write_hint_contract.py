"""The machine's own Todo-authoring hint must teach the bindable row shape."""

from __future__ import annotations

from loopx.control_plane.todos.write_hint import build_todo_write_hint


def test_agent_template_carries_the_priority_marker_the_planner_requires() -> None:
    """A row authored from this template must be bindable in the same Turn.

    The planner offers the current priority band, so an Agent Todo whose text
    has no ``[P0]/[P1]/[P2]`` marker is written to the active state and then
    cannot be bound with ``quota should-run --todo-id``. Reproduced on the
    2026-09-17 and 2026-09-20 wakes; the hint has to name the marker instead of
    letting an agent copy a template that produces an unselectable row.
    """

    hint = build_todo_write_hint("fixture-goal")
    template = hint["agent_todo_command_template"]
    assert template.startswith(
        "loopx todo add --goal-id fixture-goal --role agent "
    ), hint
    assert "--text '[P1] " in template, hint
    # The rule sentence is unchanged: agent-facing CLI output is measured per
    # row, so the marker is taught by the template the agent copies.
    assert hint["rule"] == (
        "Write user/owner actions to User Todo, not Next Action/docs/chat."
    ), hint


def test_user_templates_are_not_repointed_at_the_agent_band_rule() -> None:
    """User rows keep their own contract; only the Agent template changes.

    The marker guidance rides in the existing ``rule`` sentence instead of a new
    field: agent-facing CLI output has its own measured budget, and a separate
    field doubled the growth of every quota should-run row.
    """

    hint = build_todo_write_hint("fixture-goal")
    assert hint["user_gate_command_template"] == (
        "loopx todo add --goal-id fixture-goal --role user "
        "--task-class user_gate --blocks-agent <agent-id> "
        "--text '<blocking user decision>'"
    ), hint
    assert hint["user_action_command_template"] == (
        "loopx todo add --goal-id fixture-goal --role user "
        "--task-class user_action --bound-agent <id> --text '<action>'"
    ), hint
    assert hint["section"] == "User Todo / Owner Review Reading Queue", hint
    assert hint["rule"] == (
        "Write user/owner actions to User Todo, not Next Action/docs/chat."
    ), hint
