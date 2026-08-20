class SemanticKernelDeferred(RuntimeError):
    pass


class DeferredSemanticKernelRepository:
    """Explicit boundary for ports that are intentionally unavailable in Phase 2C."""

    def __getattr__(self, operation: str) -> object:
        raise SemanticKernelDeferred(
            f"Semantic-kernel repository operation {operation!r} is deferred."
        )


DEFERRED_SEMANTIC_KERNEL_REPOSITORY = DeferredSemanticKernelRepository()
