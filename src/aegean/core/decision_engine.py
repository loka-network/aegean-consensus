"""
Decision engine for evaluating consensus conditions.

Based on paper Section 5.2: Refinement Decision Engine
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
from collections import Counter
from aegean.core.models import Solution


class DecisionEngine(ABC):
    """
    Abstract base class for consensus decision engines.
    
    The decision engine evaluates whether consensus has been reached
    and determines when to terminate the protocol.
    """

    @abstractmethod
    def evaluate(
        self,
        solutions: List[Solution],
        round_num: int,
        previous_candidate: Optional[Solution] = None
    ) -> Tuple[Optional[Solution], bool]:
        """
        Evaluate solutions and determine if consensus is reached.
        
        Args:
            solutions: List of solutions from current round
            round_num: Current round number
            previous_candidate: Candidate solution from previous round
            
        Returns:
            Tuple of (candidate_solution, should_terminate)
            - candidate_solution: The current candidate (or None)
            - should_terminate: Whether to terminate the protocol
        """
        pass


class DefaultDecisionEngine(DecisionEngine):
    """
    Default decision engine implementing the Aegean protocol.
    
    Based on paper Algorithm 1 and Section 5.2:
    - Quorum detection: α = ⌈N/2⌉ agents must agree
    - Stability horizon: Candidate must be stable for β rounds
    """

    def __init__(
        self,
        quorum_size: int,
        stability_horizon: int,
        similarity_threshold: float = 0.9
    ):
        """
        Initialize decision engine.
        
        Args:
            quorum_size: Minimum agents needed for quorum (α)
            stability_horizon: Rounds to maintain stability (β)
            similarity_threshold: Threshold for considering answers similar
        """
        self.quorum_size = quorum_size
        self.stability_horizon = stability_horizon
        self.similarity_threshold = similarity_threshold
        self.stability_counter = 0
        self.previous_candidate: Optional[Solution] = None

    def evaluate(
        self,
        solutions: List[Solution],
        round_num: int,
        previous_candidate: Optional[Solution] = None
    ) -> Tuple[Optional[Solution], bool]:
        """
        Evaluate solutions using quorum detection and stability tracking.
        
        Algorithm:
        1. Count votes for each unique answer
        2. Find answer with most votes
        3. Check if it reaches quorum (≥ α votes)
        4. If yes, check stability:
           - If same as previous candidate: stability_counter++
           - If different: reset stability_counter = 1
        5. Terminate if stability_counter ≥ β
        """
        if not solutions:
            return None, False

        # Step 1: Count votes for each answer
        answer_votes = self._count_votes(solutions)
        
        # Step 2: Find candidate with most votes
        candidate_answer, vote_count = max(
            answer_votes.items(),
            key=lambda x: x[1]
        )
        
        # Step 3: Check quorum
        if vote_count < self.quorum_size:
            # No quorum reached
            self.stability_counter = 0
            self.previous_candidate = None
            return None, False
        
        # Find the solution object for the candidate answer
        candidate_solution = next(
            s for s in solutions if s.answer == candidate_answer
        )
        
        # Step 4: Check stability
        if self._is_same_candidate(candidate_solution, self.previous_candidate):
            # Same candidate as previous round
            self.stability_counter += 1
        else:
            # New candidate
            self.stability_counter = 1
            self.previous_candidate = candidate_solution
        
        # Step 5: Check termination condition
        should_terminate = self.stability_counter >= self.stability_horizon
        
        return candidate_solution, should_terminate

    def _count_votes(self, solutions: List[Solution]) -> Dict[str, int]:
        """
        Count votes for each unique answer.
        
        Returns:
            Dictionary mapping answer -> vote count
        """
        answers = [s.answer for s in solutions]
        return dict(Counter(answers))

    def _is_same_candidate(
        self,
        current: Optional[Solution],
        previous: Optional[Solution]
    ) -> bool:
        """
        Check if two candidates are the same.
        
        Uses exact string matching for simplicity.
        Can be extended to use similarity metrics.
        """
        if current is None or previous is None:
            return False
        
        return current.answer == previous.answer

    def reset(self) -> None:
        """Reset the decision engine state."""
        self.stability_counter = 0
        self.previous_candidate = None

    def get_state(self) -> Dict:
        """Get current state for debugging."""
        return {
            "stability_counter": self.stability_counter,
            "previous_candidate": (
                self.previous_candidate.answer 
                if self.previous_candidate else None
            ),
            "quorum_size": self.quorum_size,
            "stability_horizon": self.stability_horizon,
        }


class CustomDecisionEngine(DecisionEngine):
    """
    Example of a custom decision engine.
    
    Users can extend this to implement custom consensus logic,
    such as:
    - Weighted voting based on agent confidence
    - Semantic similarity for answer comparison
    - Dynamic quorum size adjustment
    """

    def __init__(self, quorum_size: int, stability_horizon: int):
        self.quorum_size = quorum_size
        self.stability_horizon = stability_horizon
        # Add your custom state here

    def evaluate(
        self,
        solutions: List[Solution],
        round_num: int,
        previous_candidate: Optional[Solution] = None
    ) -> Tuple[Optional[Solution], bool]:
        """
        Implement your custom consensus logic here.
        
        Example ideas:
        - Use solution.confidence for weighted voting
        - Use NLP similarity for answer comparison
        - Adjust quorum_size based on round_num
        """
        # Your implementation here
        raise NotImplementedError("Implement your custom logic")

