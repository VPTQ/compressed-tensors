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

from typing import List, Optional

import pytest
from sparsetensors.quantization.lifecycle.forward import wrap_module_forward_quantized
from sparsetensors.quantization.lifecycle.initialize import (
    initialize_module_for_quantization,
)
from sparsetensors.quantization.lifecycle.status import QuantizationStatus
from sparsetensors.quantization.quant_args import QuantizationArgs
from sparsetensors.quantization.quant_scheme import QuantizationScheme
from torch.nn import Linear


@pytest.fixture(scope="module")
def create_quantization_scheme():
    def quantization_scheme(
        targets: List[str],
        weights: Optional[QuantizationArgs] = None,
        input_activations: Optional[QuantizationArgs] = None,
        output_activations: Optional[QuantizationArgs] = None,
    ):
        return QuantizationScheme(
            targets=targets,
            weights=weights,
            input_activations=input_activations,
            output_activations=output_activations,
        )

    return quantization_scheme


def test_wrap_module_forward_quantized__forward_overwrite(create_quantization_scheme):
    num_bits = 8
    quantization_scheme = create_quantization_scheme(
        targets=["*"],
        weights=QuantizationArgs(num_bits=num_bits, symmetric=True),
        input_activations=QuantizationArgs(num_bits=num_bits, symmetric=False),
    )
    layer = Linear(4, 4)

    func_forward = layer.forward.__func__

    # check that the forward call is overwritten
    wrap_module_forward_quantized(layer, quantization_scheme)

    assert not func_forward == layer.forward.__func__


def test_wrap_module_forward_quantized__forward_overwrite(create_quantization_scheme):
    num_bits = 8
    quantization_scheme = create_quantization_scheme(
        targets=["*"],
        weights=QuantizationArgs(num_bits=num_bits, symmetric=True),
        input_activations=QuantizationArgs(num_bits=num_bits, symmetric=False),
    )
    layer = Linear(4, 4)
    layer.weight.data *= 100

    data = layer.weight.data

    wrap_module_forward_quantized(layer, quantization_scheme)
