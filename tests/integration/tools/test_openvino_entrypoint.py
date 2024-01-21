"""Test OpenVINO inference entrypoint script."""

# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


import sys
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path

import pytest

from anomalib import TaskType
from anomalib.deploy import export_to_openvino
from anomalib.models import Padim

sys.path.append("tools/inference")


class TestOpenVINOInferenceEntrypoint:
    """This tests whether the entrypoints run without errors without quantitative measure of the outputs."""

    @pytest.fixture(scope="module")
    def get_functions(self) -> tuple[Callable, Callable]:
        """Get functions from openvino_inference.py."""
        if find_spec("openvino_inference") is not None:
            from tools.inference.openvino_inference import get_parser, infer
        else:
            msg = "Unable to import openvino_inference.py for testing"
            raise ImportError(msg)
        return get_parser, infer

    def test_openvino_inference(
        self,
        get_functions: tuple[Callable, Callable],
        ckpt_path: Callable[[str], Path],
        get_dummy_inference_image: str,
        transforms_config: dict,
    ) -> None:
        """Test openvino_inference.py."""
        get_parser, infer = get_functions
        _ckpt_path = ckpt_path("Padim")
        model = Padim.load_from_checkpoint(_ckpt_path)

        # export OpenVINO model
        export_to_openvino(
            export_root=_ckpt_path.parent.parent,
            model=model,
            input_size=(256, 256),
            transform=transforms_config,
            ov_args={},
            task=TaskType.SEGMENTATION,
        )

        arguments = get_parser().parse_args(
            [
                "--weights",
                str(_ckpt_path.parent) + "/openvino/model.bin",
                "--metadata",
                str(_ckpt_path.parent) + "/openvino/metadata.json",
                "--input",
                get_dummy_inference_image,
                "--output",
                str(_ckpt_path.parent) + "/output.png",
            ],
        )
        infer(arguments)
