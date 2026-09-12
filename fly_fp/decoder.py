"""Linear readout over reservoir spikes → Action.

Training is ordinary least squares on one-hot labels. Wiring of the brain
never changes.
"""

from __future__ import annotations

from fly_fp.allowlist import Action


ACTIONS = list(Action)


class LinearReadout:
    def __init__(self, n_features: int, n_actions: int | None = None):
        self.n_features = n_features
        self.n_actions = n_actions or len(ACTIONS)
        self.w = [[0.0] * n_features for _ in range(self.n_actions)]
        self.b = [0.0] * self.n_actions
        self._fitted = False

    def logits(self, feat: list[float]) -> list[float]:
        out = []
        for a in range(self.n_actions):
            s = self.b[a]
            for i, x in enumerate(feat):
                if i >= self.n_features:
                    break
                s += self.w[a][i] * x
            out.append(s)
        return out

    def predict(self, feat: list[float]) -> Action:
        scores = self.logits(feat)
        idx = max(range(len(scores)), key=lambda i: scores[i])
        return ACTIONS[idx]

    def fit(self, xs: list[list[float]], ys: list[Action], l2: float = 1e-2) -> None:
        k = self.n_features + 1
        xtx = [[0.0] * k for _ in range(k)]
        xty = [[0.0] * self.n_actions for _ in range(k)]
        for x, y in zip(xs, ys):
            row = list(x[: self.n_features]) + [1.0]
            while len(row) < k:
                row.append(0.0)
            yi = [0.0] * self.n_actions
            yi[ACTIONS.index(y)] = 1.0
            for i in range(k):
                for j in range(k):
                    xtx[i][j] += row[i] * row[j]
                for a in range(self.n_actions):
                    xty[i][a] += row[i] * yi[a]
        for i in range(k - 1):
            xtx[i][i] += l2
        beta = _solve(xtx, xty)
        for a in range(self.n_actions):
            self.w[a] = [beta[i][a] for i in range(self.n_features)]
            self.b[a] = beta[self.n_features][a]
        self._fitted = True


def _solve(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    n = len(a)
    m = len(b[0])
    aug = [a[i][:] + b[i][:] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        diag = aug[col][col]
        if abs(diag) < 1e-12:
            aug[col][col] = 1e-12
            diag = 1e-12
        inv = 1.0 / diag
        for j in range(col, n + m):
            aug[col][j] *= inv
        for r in range(n):
            if r == col:
                continue
            fac = aug[r][col]
            if fac == 0:
                continue
            for j in range(col, n + m):
                aug[r][j] -= fac * aug[col][j]
    return [row[n:] for row in aug]
