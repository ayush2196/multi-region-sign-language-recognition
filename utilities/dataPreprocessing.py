import tensorflow_datasets as tfds
import sign_language_datasets.datasets

# Loading a dataset with custom configuration
from sign_language_datasets.datasets.config import SignDatasetConfig

config = SignDatasetConfig(
    name="videos_and_poses256x256:12",
    # Specific version
    version="3.0.0",
    # Download, and load dataset videos
    include_video=True,
    # Load videos at constant, 12 fps
    #fps=12,
    # Convert videos to a constant resolution, 256x256
    resolution=(256, 256),
    # Download and load Holistic pose estimation
    include_pose="holistic")

rwth_phoenix2014_t = tfds.load(
    name='rwth_phoenix2014_t',
    builder_kwargs=dict(config=config))
