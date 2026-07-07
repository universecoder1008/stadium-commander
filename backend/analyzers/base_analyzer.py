"""Base Analyzer for Stadium Commander.

This module defines the abstract base class for all operational telemetry analyzers.

Purpose:
    Enforce architectural consistency, reduce code duplication for telemetry confidence
    calculations, and define standard interfaces for analytical components.

Inputs:
    - Lists of telemetry inputs to assess confidence, and analytical implementations.

Outputs:
    - Float confidence values and abstract definitions.

Deterministic Guarantees:
    - Enforces standard, predictable confidence calculations across all child modules.

AI Usage:
    - This code is 100% deterministic and runs entirely locally. It does not use Gemini or
      any other LLMs.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class BaseAnalyzer(ABC):
    """Abstract base class for all stadium operations analyzers."""

    @abstractmethod
    def analyze(self, input_data: Any) -> Any:
        """Analyzes operational telemetry to determine risk levels and predictions.

        Args:
            input_data: The input telemetry Pydantic model.

        Returns:
            The structured response Pydantic model.
        """
        pass

    def calculate_confidence(
        self,
        fields: List[Any],
        total_fields: int,
        reasoning: List[str]
    ) -> float:
        """Calculates telemetry analysis confidence based on data completeness.

        Args:
            fields: A list of telemetry field values to evaluate.
            total_fields: The total expected number of fields.
            reasoning: The reasoning output list to append traces to.

        Returns:
            A float confidence score between 0.0 and 1.0.
        """
        non_null_count = sum(1 for field in fields if field is not None)
        confidence = round(non_null_count / total_fields, 2)
        
        reasoning.append(
            f"Confidence calculated at {confidence} based on "
            f"completeness of input telemetry ({non_null_count} of "
            f"{total_fields} fields provided)."
        )
        return confidence
