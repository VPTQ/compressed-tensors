import pytest
import torch
from compressed_tensors.quantization.observers import RoundToNearestObserver
from compressed_tensors.quantization.quant_args import QuantizationArgs


@pytest.mark.parametrize(
    "symmetric,expected_scale,expected_zero_point",
    [
        (True, 0.0078, 0),
        (False, 0.0039, -128),
    ],
)
def test_rtn_observer(symmetric, expected_scale, expected_zero_point):
    tensor = torch.tensor([[1, 1, 1, 1, 1]])
    num_bits = 8
    weights = QuantizationArgs(num_bits=num_bits, symmetric=symmetric, observer="round_to_nearest", group_size=1)

    observer = weights.get_observer()
    scale, zero_point = observer(tensor)

    assert isinstance(observer, RoundToNearestObserver)
    assert round(scale.item(), 4) == expected_scale
    assert round(zero_point.item(), 4) == expected_zero_point


def test_rtn_observer_symmetric_scale_range():
    tensor = torch.rand(4, 4)
    tensor *= 127

    num_bits = 8
    weights = QuantizationArgs(num_bits=num_bits, symmetric=True)

    observer = weights.get_observer()
    scale, zero_point = observer(tensor)

    # if symmetric, max symmetric_range = abs(-128) / 255
    assert round(scale.item(), 4) <= 1.0039
    assert round(zero_point.item(), 4) == 0
