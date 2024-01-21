"""Test torch inference entrypoint script."""

# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


import sys
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path

import pytest

from anomalib import TaskType
from anomalib.deploy import export_to_torch
from anomalib.models import Padim

sys.path.append("tools/inference")


class TestTorchInferenceEntrypoint:
    """This tests whether the entrypoints run without errors without quantitative measure of the outputs."""

    @pytest.fixture()
    def get_functions(self) -> tuple[Callable, Callable]:
        """Get functions from torch_inference.py."""
        if find_spec("torch_inference") is not None:
            from tools.inference.torch_inference import get_parser, infer
        else:
            msg = "Unable to import torch_inference.py for testing"
            raise ImportError(msg)
        return get_parser, infer

    def test_torch_inference(
        self,
        get_functions: tuple[Callable, Callable],
        project_path: Path,
        ckpt_path: Callable[[str], Path],
        get_dummy_inference_image: str,
        transforms_config: dict,
    ) -> None:
        """Test torch_inference.py."""
        _ckpt_path = ckpt_path("Padim")
        get_parser, infer = get_functions
        model = Padim.load_from_checkpoint(_ckpt_path)
        export_to_torch(
            model=model,
            export_root=_ckpt_path.parent.parent,
            transform=transforms_config,
            task=TaskType.SEGMENTATION,
        )
        arguments = get_parser().parse_args(
            [
                "--weights",
                str(_ckpt_path.parent) + "/torch/model.pt",
                "--input",
                get_dummy_inference_image,
                "--output",
                str(project_path) + "/output.png",
            ],
        )
        infer(arguments)
