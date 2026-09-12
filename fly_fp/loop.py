"""Closed loop: observe terminal → encode → reservoir → readout → allowlisted fp."""

from __future__ import annotations

from dataclasses import dataclass, field

from fly_fp.allowlist import Action, command_for
from fly_fp.brain import ReservoirBrain, make_brain
from fly_fp.curriculum import training_pairs
from fly_fp.decoder import LinearReadout
from fly_fp.encoder import N_CHANNELS, TerminalObs, encode
from fly_fp.executor import ExecResult, SafeExecutor


@dataclass
class StepLog:
    obs: TerminalObs
    sensory: list[float]
    action: Action
    result: ExecResult
    reward: float


@dataclass
class FlyOperator:
    brain_kind: str = "stub"
    dry_run: bool = True
    steps_per_obs: int = 12
    brain: object = field(init=False)
    readout: LinearReadout = field(init=False)
    executor: SafeExecutor = field(init=False)

    def __post_init__(self) -> None:
        self.brain = make_brain(self.brain_kind)
        n = getattr(self.brain, "n", 64)
        self.readout = LinearReadout(n_features=n)
        self.executor = SafeExecutor(dry_run=self.dry_run)
        self.fit_from_curriculum()

    def _features(self, obs: TerminalObs) -> list[float]:
        sensory = encode(obs)
        if hasattr(self.brain, "rollout"):
            return self.brain.rollout(sensory, steps=self.steps_per_obs)
        feat = sensory[:]
        while len(feat) < self.readout.n_features:
            feat.append(0.0)
        return feat[: self.readout.n_features]

    def fit_from_curriculum(self) -> None:
        xs: list[list[float]] = []
        ys: list[Action] = []
        for obs, action in training_pairs():
            if hasattr(self.brain, "reset"):
                self.brain.reset()
            xs.append(self._features(obs))
            ys.append(action)
        self.readout.fit(xs, ys)

    def _goal_prior(self, obs: TerminalObs) -> Action:
        g = " ".join(obs.goal_tokens).lower()
        if "mulai-jualan" in g or "mulai jualan" in g:
            return Action.SKILLS_INSTALL_MULAI_JUALAN
        if "marketing" in g:
            return Action.SKILLS_SEARCH
        if "tutorial" in g:
            return Action.GUIDANCE_TUTORIALS
        if "guidance" in g:
            return Action.GUIDANCE
        if "catalog" in g:
            return Action.CATALOG
        if "product" in g:
            return Action.PRODUCTS_LIST
        if "template" in g:
            return Action.NEW_LIST
        if "skill" in g:
            return Action.SKILLS_LIST
        if "usage" in g or "help" in g or not g:
            return Action.HELP
        return Action.HELP

    def choose(self, obs: TerminalObs) -> Action:
        sensory = encode(obs)
        if sensory[2] >= 0.5:
            return Action.IDLE
        if sensory[6] >= 0.8:
            return Action.IDLE
        if sensory[4] >= 0.5 and sensory[5] >= 0.5:
            return self._goal_prior(obs)
        feat = self._features(obs)
        return self.readout.predict(feat)

    def reward(self, obs: TerminalObs, action: Action, result: ExecResult) -> float:
        if result.blocked:
            return -2.0
        if action is Action.IDLE:
            return 0.2 if encode(obs)[2] >= 0.5 or encode(obs)[6] >= 0.8 else -0.1
        if result.exit_code != 0:
            return -0.5
        expect = command_for(action).expect_tokens
        text = (result.stdout + "\n" + result.stderr).lower()
        hits = sum(1 for t in expect if t.lower() in text)
        if result.dry_run:
            return 0.4
        return 0.3 + 0.2 * hits

    def step(self, obs: TerminalObs) -> StepLog:
        action = self.choose(obs)
        result = self.executor.run(action)
        r = self.reward(obs, action, result)
        return StepLog(obs, encode(obs), action, result, r)

    def run_goal(self, goal_tokens: tuple[str, ...], seed_obs: TerminalObs | None = None) -> list[StepLog]:
        logs: list[StepLog] = []
        obs = seed_obs or TerminalObs(goal_tokens=goal_tokens)
        obs.goal_tokens = goal_tokens
        for _ in range(6):
            if hasattr(self.brain, "reset"):
                self.brain.reset()
            log = self.step(obs)
            logs.append(log)
            if log.result.blocked:
                break
            if log.action is Action.IDLE and logs:
                break
            obs = TerminalObs(
                stdout=log.result.stdout,
                stderr=log.result.stderr,
                exit_code=log.result.exit_code,
                goal_tokens=goal_tokens,
                last_action=log.action.value,
            )
            if goal_tokens and all(t.lower() in (obs.stdout + obs.stderr).lower() for t in goal_tokens):
                break
        return logs
