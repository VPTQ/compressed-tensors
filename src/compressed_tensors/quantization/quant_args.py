# Copyright (c) 2021 - present / Neuralmagic, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


__all__ = ["QuantizationType", "QuantizationStrategy", "QuantizationArgs"]


class QuantizationType(str, Enum):
    """
    Enum storing quantization type options
    """

    INT = "int"
    FLOAT = "float"


class QuantizationStrategy(str, Enum):
    """
    Enum storing quantization strategy options
    """

    TENSOR = "tensor"
    CHANNEL = "channel"
    GROUP = "group"
    BLOCK = "block"
    TOKEN = "token"


class QuantizationArgs(BaseModel):
    """
    User facing arguments used to define a quantization config for weights or
    activations

    :param num_bits: quantization bit depth
    :param type: dtype to quantized to, either int or float
    :param symmetric: whether or not quantization scale is symmetric about zero-point
    :param strategy: string id determining the scope of scale/zero-point to apply
    :param group_size: group length to use for the group strategy
    :param block_structure: 2d block structure to use for the block strategy, must be
    of the format "2x4", "8x16", etc.
    """

    num_bits: int = 8
    type: QuantizationType = QuantizationType.INT
    symmetric: bool = True
    strategy: QuantizationStrategy = QuantizationStrategy.TENSOR
    group_size: Optional[int] = None
    block_structure: Optional[str] = None
    observer: str = Field(
        default="minmax",
        description=(
            "The class to use to compute the quantization param - "
            "scale and zero-point'"
        ),
    )
    observer_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "optional dict of kwargs to be passed directly to torch quantization "
            "Observers constructor excluding quantization range or symmetry"
        ),
    )

    def get_observer(self):
        """
        :return: torch quantization FakeQuantize built based on these QuantizationArgs
        """
        from compressed_tensors.quantization.observers.base import Observer

        return Observer.load_from_registry(self.observer, quantization_args=self)
