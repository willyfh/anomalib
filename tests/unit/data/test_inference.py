"""Unit tests - Predict Dataset Tests."""

# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path

import albumentations as A  # noqa: N812
import pytest

from anomalib.data import PredictDataset


@pytest.fixture(scope="module")
def predict_dataset_path(dataset_path: Path) -> Path:
    """Fixture that returns the path to the bad test samples of the dummy MVTec AD dataset."""
    return dataset_path / "mvtec" / "dummy" / "test" / "bad"


class TestPredictDataset:
    """Test PredictDataset class."""

    def test_inference_dataset(self, predict_dataset_path: Path) -> None:
        """Test the PredictDataset class."""
        # Use the bad images from the dummy MVTec AD dataset.
        dataset = PredictDataset(path=predict_dataset_path, image_size=(256, 256))

        # Dummy MVtec AD dataset has 5 abnormal images in the test set.
        assert len(dataset) == 5

        # Check the first sample.
        sample = dataset[0]
        assert isinstance(sample, dict)
        assert "image" in sample
        assert "image_path" in sample
        assert sample["image"].shape == (3, 256, 256)
        assert Path(sample["image_path"]).suffix == ".png"

    def test_transforms_applied(self, predict_dataset_path: Path) -> None:
        """Test whether the transforms are applied to the images."""
        # Create a transform that resizes the image to 512x512.
        transform = A.Compose([A.Resize(512, 512)])
        dataset = PredictDataset(path=predict_dataset_path, transform=transform)

        # Check the first sample.
        sample = dataset[0]

        # Check that the image is resized to 512x512.
        assert sample["image"].shape == (512, 512, 3)
