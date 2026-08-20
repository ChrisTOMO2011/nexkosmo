import pytest

from app.infrastructure.semantic_kernel_boundary import (
    DEFERRED_SEMANTIC_KERNEL_REPOSITORY,
    SemanticKernelDeferred,
)


def test_deferred_semantic_kernel_fails_explicitly() -> None:
    with pytest.raises(SemanticKernelDeferred, match="deferred"):
        DEFERRED_SEMANTIC_KERNEL_REPOSITORY.get  # noqa: B018
