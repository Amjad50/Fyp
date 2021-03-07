from typing import Tuple, List

Box = Tuple[int, int, int, int]
LabeledCrops = List[Tuple[str, Box]]
LabelCrop = Tuple[str, Box]
