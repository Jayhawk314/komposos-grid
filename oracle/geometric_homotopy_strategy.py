from ._base import OracleStrategy


HOMOTOPY_AVAILABLE = False


class GeometricHomotopyStrategy(OracleStrategy):
    strategy_name = "geometric_homotopy"

    def predict(self, source, target):
        return []

