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

from pathlib import Path
from typing import Dict, Optional, Union

from compressed_tensors.base import CONFIG_NAME
from compressed_tensors.compressors import ModelCompressor
from compressed_tensors.config import CompressionConfig
from safetensors.torch import save_file
from torch import Tensor
from transformers import AutoConfig


__all__ = ["infer_compressor_from_model_config", "load_compressed", "save_compressed"]


def infer_compressor_from_model_config(
    pretrained_model_name_or_path: str,
) -> Optional[ModelCompressor]:
    """
    Given a path to a model config, extract a sparsity config if it exists and return
    the associated ModelCompressor

    :param pretrained_model_name_or_path: path to model config on disk or HF hub
    :return: matching compressor if config contains a sparsity config
    """
    config = AutoConfig.from_pretrained(pretrained_model_name_or_path)
    sparsity_config = getattr(config, CONFIG_NAME, None)
    if sparsity_config is None:
        return None

    format = sparsity_config.get("format")
    sparsity_config = CompressionConfig.load_from_registry(format, **sparsity_config)
    compressor = ModelCompressor.load_from_registry(format, config=sparsity_config)
    return compressor


def save_compressed(
    tensors: Dict[str, Tensor],
    save_path: Union[str, Path],
    compression_config: Optional[CompressionConfig] = None,
) -> Optional[CompressionConfig]:
    """
    Save compressed tensors to disk. If tensors are not compressed,
    save them as is.

    :param tensors: dictionary of tensors to compress
    :param save_path: path to save compressed tensors
    :param compression_config: compression config to use for compressing tensors.
        Can be either inferred from tensors or provided explicitly
    :return: compression config, if tensors were compressed - None otherwise
    """
    if tensors is None or len(tensors) == 0:
        raise ValueError("No tensors or empty tensors provided to compress")

    # create compression config if not provided
    # TODO: Not implemented, need to get this in ASAP
    # compression_config = compression_config or infer_compression_config(tensors)

    if compression_config is None:
        # no compression applied
        save_file(tensors, save_path)
        return None

    # compress
    compression_format = compression_config.format
    compressor = ModelCompressor.load_from_registry(
        compression_format, config=compression_config
    )
    # save compressed tensors
    compressed_tensors = compressor.compress(tensors)
    save_file(compressed_tensors, save_path)

    # return compression_config as dict
    return {CONFIG_NAME: compression_config.model_dump(exclude_unset=True)}


def load_compressed(compressed_tensors: Union[str, Path], device: str):
    pass
