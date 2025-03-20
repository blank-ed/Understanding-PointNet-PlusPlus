# Understanding PointNet++: A Intuitive & Visual Guide

## Summary
I recently came across a paper, [PointNet++](https://arxiv.org/abs/1706.02413), that trains a deep learning model from Point Cloud Data (PCD) to classify or to segment 3D geometric data. The model bypasses the need to preprocess the data into image grids or 3D voxels, which can result in a loss of detail and added complexity. As someone new to this field, I found this paper challenging. Aside from the paper and a few vague blog posts, there wasn’t many resources to learn from. Either way, the explanations in various sections were either filled with unnecessarily complex language or simply reiterated content from the original paper, which did not help much. This has led me document my understanding of this paper in terms of a blog post, where I will try to provide examples and visuals for a better understanding. This led me to write a [blog post](https://blank-ed.github.io/ilyas_dawoodjee/#/blogpage/understanding_pointnet++:_aintuitive) which is about providing readers, from beginners to experts, an intuitive and visual way of understanding PointNet++ by comparing different algorithms and explaining the rationale behind selecting specific approaches.

[PointNet++](https://arxiv.org/abs/1706.02413) can be seen as an extension of [PointNet](https://arxiv.org/abs/1612.00593), but with an added hierarchical structure. The drawback pointed out for PointNet is that it does not capture local features effectively, rather processes global features unlike that of convolutional architectures that capture local patterns through kernels. Capturing local features means that for each point, we look at its neighbouring points and determine the relationship through hierarchical layers that process local regions at increasing scales. This approach allows us to better generalize to unseen shapes. Looking at global features misses out on the fine-grained details of the Point Cloud Data (PCD). Figure 1 shows PointNet++ architecture diagram. Let us first look at a basic explanation of PointNet. In the following sections, we will explore an extension of PointNet with a hierarchical structure and finally discuss PointNet++.

## Using this codebase
To help visualize some of the concepts in the [blog post](https://blank-ed.github.io/ilyas_dawoodjee/#/blogpage/understanding_pointnet++:_aintuitive), I have created visualizer classes. To setup the visualizers, firstly download the GitHub repository and install the necessary libraries needed by running the shell commands below:

```sh
git clone https://github.com/blank-ed/Understanding-PointNet-PlusPlus.git
cd Understanding-PointNet-PlusPlus && pip install -r requirements.txt
```

If you want to stick with the versions that I used, run:

```sh
pip install open3d==0.19.0 PySide6==6.8.2.1 fpsample==0.3.3
```

To download the dataset, you can git clone from [this repository](https://github.com/madlabub/Machining-feature-dataset.git), extract the `dataset.rar`, and copy all 24 folders inside `dataset/stl/` into `MFD_dataset` directory. The visualizer classes allow you to select a random STL file or a specific STL file from the dataset folder MFD_dataset and convert them into a user specified number of points PCD by using a slider between the range of user specified minimum and maximum number of points. Depending on the type of visualization, the settings/parameters and the visualization window will be different. This visualizer is created using `PySide6` with `open3d` embedded inside for PCD processing. The available visualizer classes and their settings/parameters will be explained in the sections below. You can run each of the visualizers by running the following script:

```python
"""Visualizers for PCD Data"""

from visualizers import (
    VisualizerPCD_FPS_vs_RandomSampling,
    VisualizePCD_BallQuery_vs_kNN,
)

if __name__ == '__main__'
    # Run the desired visualizer by uncommenting its line.
    VisualizePCD_FPS_vs_RandomSampling.run()  # FPS vs Random Sampling Visualizer
    # VisualizePCD_BallQuery_vs_kNN.run()     # Ball Query vs kNN Visualizer
```
