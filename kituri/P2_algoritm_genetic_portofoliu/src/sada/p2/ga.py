"""Algoritmul genetic pentru portofoliu, cu cârlige pentru bucla MAPE-K.

Bucla principală (`run`) e scrisă: aplică schimbările programate, evaluează
populația, lasă controllerul să intervină, înregistrează statisticile și trece
la generația următoare. Voi completați operatorii (TODO), GHID.md pașii 1 și 4.

Puteți folosi DEAP pentru operatori (deap.tools.selTournament, cxUniform,
mutFlipBit) sau îi puteți scrie direct cu NumPy; pentru vectori binari, varianta
NumPy e scurtă și rapidă.

Parametrii pe care controllerul îi poate modifica în timpul rulării sunt
atribute ale obiectului: self.p_mut, self.immigrant_frac etc.
"""
from __future__ import annotations

import numpy as np

from .problem import Problem


class DynamicGA:
    def __init__(self, problem: Problem, cfg: dict, rng: np.random.Generator):
        self.problem = problem
        self.rng = rng
        self.pop_size = int(cfg["pop_size"])
        self.k = int(cfg["tournament_k"])
        self.p_cx = float(cfg["p_crossover"])
        self.base_p_mut = float(cfg["p_mut"]) if cfg.get("p_mut") else 1.0 / problem.n
        self.p_mut = self.base_p_mut
        self.elitism = int(cfg["elitism"])
        self.pop: np.ndarray | None = None        # matrice pop_size × n
        self.fit: np.ndarray | None = None
        self.evaluations = 0
        self.generation = 0
        self.history: list[dict] = []

    # ------------------------------------------------------------ TODO
    def fitness(self, x: np.ndarray) -> float:
        """Valoarea unui individ, ținând cont de buget.

        TODO (GHID.md, pasul 1): alegeți una dintre variante și justificați-o în raport:
          - penalizare: problem.objective(x) - λ * depășirea bugetului (problem.violations(x));
          - reparare: scoateți elemente (de ex. cele cu cel mai mic raport valoare/cost)
            până când x devine fezabil, apoi problem.objective(x). Dacă reparați,
            scrieți individul reparat înapoi în populație (Lamarck) sau nu (Baldwin);
            spuneți ce ați ales.
        """
        raise NotImplementedError("DynamicGA.fitness (GHID.md, pasul 1)")

    def init_population(self) -> None:
        """TODO: populația inițială, de exemplu biți aleatori cu probabilitatea buget/cost total."""
        raise NotImplementedError("DynamicGA.init_population (GHID.md, pasul 4)")

    def next_generation(self) -> None:
        """TODO: elitism + (selecție turnir, încrucișare, mutație) până la pop_size.
        Folosiți self.p_mut (controllerul îl poate schimba) și self.rng."""
        raise NotImplementedError("DynamicGA.next_generation (GHID.md, pasul 4)")

    # ------------------------------------------------------------ gata
    def evaluate_population(self) -> None:
        self.fit = np.array([self.fitness(ind) for ind in self.pop])
        self.evaluations += len(self.pop)

    def best(self) -> tuple[np.ndarray, float]:
        i = int(np.argmax(self.fit))
        return self.pop[i].copy(), float(self.fit[i])

    def diversity(self) -> float:
        """Distanța Hamming medie normalizată față de individul mediu (0 = populație identică)."""
        return float(np.abs(self.pop - self.pop.mean(axis=0)).mean())

    def replace_random(self, frac: float) -> None:
        """Înlocuiește o fracțiune din cei mai slabi indivizi cu indivizi aleatori (imigranți)."""
        m = int(round(frac * self.pop_size))
        if m <= 0:
            return
        worst = np.argsort(self.fit)[:m]
        saved_pop = self.pop
        self.init_population()                      # refolosește generatorul vostru
        fresh = self.pop[:m].copy()
        self.pop = saved_pop
        self.pop[worst] = fresh
        self.fit[worst] = [self.fitness(ind) for ind in fresh]
        self.evaluations += m

    def record(self, events=()) -> None:
        x, f = self.best()
        self.history.append({
            "generation": self.generation, "evaluations": self.evaluations,
            "best_fitness": f, "best_objective": self.problem.objective(x),
            "best_feasible": self.problem.is_feasible(x), "mean_fitness": float(self.fit.mean()),
            "diversity": self.diversity(), "p_mut": self.p_mut, "events": list(events)})

    def run(self, n_generations: int, schedule=None, controller=None) -> list[dict]:
        self.init_population()
        for g in range(n_generations):
            self.generation = g
            changes = schedule.apply(self.problem, g) if schedule else []
            self.evaluate_population()
            if controller is not None:
                controller.step(self, g)
            self.record(events=[c["type"] for c in changes])
            self.next_generation()
        return self.history
