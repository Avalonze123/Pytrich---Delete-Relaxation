from Pytrich.Heuristics.blind_heuristic import BlindHeuristic
from Pytrich.Heuristics.tdg_heuristic import TaskDecompositionHeuristic
from Pytrich.Heuristics.lmcount_heuristic import LandmarkCountHeuristic
from Pytrich.Heuristics.novelty_heuristic import NoveltyHeuristic
from Pytrich.Heuristics.hmax_heuristic import HmaxHeuristic
from Pytrich.Heuristics.aggregation import Max, Tiebreaking
from Pytrich.Heuristics.del_relax_heuristic import DeleteRelaxationHeuristic


HEURISTICS = {
    "Blind": BlindHeuristic,
    "LMCOUNT": LandmarkCountHeuristic,
    "TDG": TaskDecompositionHeuristic,
    "NOVELTY": NoveltyHeuristic,
    "HMAX": HmaxHeuristic,
    "DELRELAX": DeleteRelaxationHeuristic,
}

AGGREGATIONS = {
    "Max": Max,
    "Tiebreaking": Tiebreaking,
}
