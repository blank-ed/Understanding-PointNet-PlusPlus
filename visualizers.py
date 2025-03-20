from pathlib import Path
import open3d as o3d
import sys
from PySide6 import QtWidgets, QtGui, QtCore
import win32gui
import fpsample
import numpy as np
import random


class VisualizerClass:
    """
    Visualizer class containing common utility functions for UI and visualization setup.

    This class provides methods for creating UI elements (e.g., labels, buttons, sliders),
    setting up Open3D visualizers, embedding Open3D windows into Qt, and handling file operations.
    """

    # ========================== UI Element Creation ==========================
    def create_container(self, geometry: list[int], vertical: bool = False) -> QtWidgets.QLayout:
        """
        Create a container widget with a layout.

        :param geometry: A list of integers defining the container's geometry [x, y, width, height].
        :param vertical: If True, use a vertical layout; otherwise, use a horizontal layout.
        :return: The layout of the container.
        """
        container = QtWidgets.QWidget(self.central_widget)
        container.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        layout = QtWidgets.QVBoxLayout(container) if vertical else QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def create_label(self, label_name: str, position: list[int], font_size: int) -> QtWidgets.QLabel:
        """
        Create a QLabel with specified text, position, and font size.

        :param label_name: The text to display on the label.
        :param position: A list of integers defining the label's position [x, y].
        :param font_size: The font size of the label text.
        :return: The created QLabel.
        """
        label = QtWidgets.QLabel(label_name, self.central_widget)
        label.move(position[0], position[1])
        label.setStyleSheet(f"font-weight: bold; font-size: {font_size}px;")
        label.adjustSize()
        return label

    def create_slider(self, geometry: list[int], slider_range: list[int], initial_value: int, connector) -> QtWidgets.QSlider:
        """
        Create a horizontal QSlider with specified geometry, range, and connector function.

        :param geometry: A list of integers defining the slider's geometry [x, y, width, height].
        :param slider_range: A list of integers defining the slider's minimum and maximum values [min, max].
        :param initial_value: The initial value of the slider.
        :param connector: The function to connect to the slider's valueChanged signal.
        :return: The created QSlider.
        """
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self.central_widget)
        slider.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        slider.setMinimum(slider_range[0])
        slider.setMaximum(slider_range[1])
        slider.setValue(initial_value)
        slider.valueChanged.connect(connector)
        return slider

    def create_button(self, label_name: str, geometry: list[int], connector) -> QtWidgets.QPushButton:
        """
        Create a button with specified geometry and connector function.

        :param label_name: The text to display on the button.
        :param geometry: A list of integers defining the button's geometry [x, y, width, height].
        :param connector: The function to connect to the button's clicked signal.
        :return: The created QPushButton.
        """
        button = QtWidgets.QPushButton(label_name, self.central_widget)
        button.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        button.clicked.connect(connector)
        return button

    def create_label_and_checkbox(self, label_name: str, enabled: bool, connector) -> tuple[QtWidgets.QLabel, QtWidgets.QCheckBox]:
        """
        Create a QLabel and QCheckBox pair with specified properties.

        :param label_name: The text to display on the label.
        :param enabled: Whether the label and checkbox should be enabled.
        :param connector: The function to connect to the checkbox's stateChanged signal.
        :return: A tuple containing the created QLabel and QCheckBox.
        """
        label = QtWidgets.QLabel(label_name)
        label.setEnabled(enabled)

        checkbox = QtWidgets.QCheckBox()
        checkbox.stateChanged.connect(connector)
        checkbox.setEnabled(enabled)

        return label, checkbox

    def create_label_and_input_field(self, label_name: str, enabled: bool, initial_value: str, connector) -> tuple[QtWidgets.QLabel, QtWidgets.QLineEdit]:
        """
        Create a QLabel and QLineEdit pair with specified properties.

        :param label_name: The text to display on the label.
        :param enabled: Whether the label and input field should be enabled.
        :param initial_value: The initial text in the input field.
        :param connector: The function to connect to the input field's textChanged signal.
        :return: A tuple containing the created QLabel and QLineEdit.
        """
        label = QtWidgets.QLabel(label_name)
        label.setEnabled(enabled)

        input_field = QtWidgets.QLineEdit()
        input_field.setText(initial_value)
        input_field.textChanged.connect(connector)
        input_field.setEnabled(enabled)

        return label, input_field

    # ====================== Visualization Handling ===========================
    def setup_visualizers(self, window_name: str, pcd: o3d.geometry.PointCloud) -> tuple[o3d.visualization.Visualizer, o3d.visualization.ViewControl]:
        """
        Initialize an Open3D visualizer with a point cloud.

        :param window_name: The name of the Open3D visualization window.
        :param pcd: The point cloud to visualize.
        :return: A tuple containing the Open3D visualizer and its view control.
        """
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=window_name, width=400, height=400, visible=False)
        vis.add_geometry(pcd)
        if hasattr(self, "coordinate_frame") and self.coordinate_frame is not None:
            vis.add_geometry(self.coordinate_frame)
        view_control = vis.get_view_control()
        view_control.set_zoom(1)
        return vis, view_control

    def embed_open3d_window(self, window_name: str, x: int, y: int, w: int, h: int) -> QtWidgets.QWidget:
        """
        Embed an Open3D window into the Qt application.

        :param window_name: The name of the Open3D window to embed.
        :param x: The x-coordinate of the embedded window.
        :param y: The y-coordinate of the embedded window.
        :param w: The width of the embedded window
        :param h: The height of the embedded window
        :return: The container widget holding the embedded Open3D window.
        """
        hwnd = win32gui.FindWindow(None, window_name)
        window = QtGui.QWindow.fromWinId(hwnd)
        container = self.createWindowContainer(window, self.central_widget)
        container.setGeometry(x, y, w, h)
        return container

    def update_vis(self) -> None:
        """Update all Open3D visualizers found in the instance."""
        for attr_name in dir(self):
            # Check if the attribute name starts with "vis_"
            if attr_name.startswith("vis_"):
                vis_obj = getattr(self, attr_name)
                # Check if the object has the required methods (i.e. is an Open3D visualizer)
                if callable(getattr(vis_obj, "poll_events", None)) and callable(getattr(vis_obj, "update_renderer", None)):
                    vis_obj.poll_events()
                    vis_obj.update_renderer()

    def set_enabled(self, widgets: tuple, enabled: bool) -> None:
        """
        Helper function to enable or disable a list of UI widgets.

        :param widgets: List of UI elements to enable or disable.
        :param enabled: Boolean value indicating whether to enable or disable the widgets.
        :return: None
        """
        for widget in widgets:
            widget.setEnabled(enabled)

    # ========================== File Handling ================================
    def get_random_stl_file(self) -> Path:
        """
        Randomly select an STL file from the dataset directory.

        :return: The path to the selected STL file.
        """
        subfolders = [f for f in self.base_path.iterdir() if f.is_dir()]
        selected_subfolder = random.choice(subfolders)
        stl_files = list(selected_subfolder.glob('*.STL'))
        return random.choice(stl_files)

    def select_file(self) -> None:
        """Open a file dialog to select a file."""
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", str(self.base_path), "Supported Files (*.stl)")
        if file_name:
            self.update_file(file_name)

    def randomize_file(self) -> None:
        """Randomly select a new STL file from the dataset."""
        random_file = self.get_random_stl_file()
        self.update_file(random_file)

    def update_file(self, file_path: str) -> None:
        """
        Updates the application state to load and display a new STL file.

        :param file_path: The path to the file to update.
        """
        self.selected_stl_file = Path(file_path)
        self.manufacturing_file_path.setText(f"Manufacturing Feature: {' '.join(self.selected_stl_file.parent.stem.split('_')[1:]).title()}")
        self.manufacturing_file_path.adjustSize()
        self.file_file_path.setText(f"File Name: {self.selected_stl_file.stem}.STL")
        self.file_file_path.adjustSize()

        # Read the STL file and sample it into a point cloud.
        self.mesh = o3d.io.read_triangle_mesh(self.selected_stl_file)
        num_points = self.num_points_slider.value()
        self.pcd = self.mesh.sample_points_poisson_disk(num_points)

        self.update_STL_file()

    def update_STL_file(self) -> None:
        """
        Hook method that subclasses can override to update selected/randomize file.
        The default implementation does nothing.
        """
        pass

    # ===================== Slider Range Update =============================
    def update_slider_range(self) -> None:
        """
        Update the sampling points slider range based on the minimum and maximum values set by users.
        Performs basic error checking and common slider updates. Subclasses can customize additional behavior via
        the update_custom_slider hook.

        :returns: None
        """
        try:
            # Get minimum and maximum values from input fields
            min_val = int(self.min_input.text())
            max_val = int(self.max_input.text())

            # Ensure min_val is less than max_val and within a reasonable range
            if min_val >= max_val:
                min_val = max_val - 1
                self.min_input.setText(str(min_val))
            if min_val < 1:
                min_val = 1
                self.min_input.setText(str(min_val))

            # Update the main slider's range
            self.num_points_slider.setMinimum(min_val)
            self.num_points_slider.setMaximum(max_val)

            # Ensure the current slider value is within the new range
            current_value = self.num_points_slider.value()
            if current_value < min_val:
                self.num_points_slider.setValue(min_val)
            elif current_value > max_val:
                self.num_points_slider.setValue(max_val)

            # Call the hook for additional slider updates (e.g., updating another slider)
            self.update_custom_slider()

        except ValueError:
            # If conversion to int fails, reset the input fields to the slider's current valid range
            self.min_input.setText(str(self.num_points_slider.minimum()))
            self.max_input.setText(str(self.num_points_slider.maximum()))

    def update_custom_slider(self) -> None:
        """
        Hook method that subclasses can override to update an additional slider.
        For example, one subclass might update an FPS slider, while another updates a sampling slider.
        The default implementation does nothing.
        """
        pass

    @classmethod
    def run(cls) -> None:
        """
        Entry point for running the application.

        This method initializes the Qt application, creates an instance of the main window,
        and starts the application event loop.
        """
        app = QtWidgets.QApplication(sys.argv)
        window = cls()
        sys.exit(app.exec())


class VisualizePCD_FPS_vs_RandomSampling(QtWidgets.QMainWindow, VisualizerClass):
    def __init__(self, *args, **kwargs):
        """
        Initializes the main application window for visualizing FPS vs randomly sampled PCD.

        This method initializes and configures the following:
            - Selects and loads STL file from path and samples it into a PCD
            - Applies initial sampling for FPS and random sampling with half the current number of points
            - Configures visualizers for the original, FPS, and randomly sampled PCD

        :param args: Positional arguments passed to the parent class.
        :param kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(*args, **kwargs)

        # Set up the base path
        self.base_path = Path().cwd() / 'MFD_dataset'

        # Initially, load a random STL file
        self.selected_stl_file = self.get_random_stl_file()
        print(f"Visualizing random STL file: {self.selected_stl_file}")

        # Load mesh and sample points
        self.mesh = o3d.io.read_triangle_mesh(self.selected_stl_file)
        self.initial_num_pcd_points = 5000
        self.pcd = self.mesh.sample_points_poisson_disk(self.initial_num_pcd_points)

        # Define initial sampling point count
        self.initial_num_sampling_points = self.initial_num_pcd_points // 2

        # Create an empty placeholder for FPS and randomly sampled PCD; it will be updated later
        self.fps = o3d.geometry.PointCloud()
        self.random = o3d.geometry.PointCloud()

        # Setup the main Qt window with a central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # Buttons to select a file or to randomize the STL file from the base path
        self.btn_select_file = self.create_button(label_name="Select File", geometry=[50, 65, 150, 30], connector=self.select_file)
        self.btn_randomize = self.create_button(label_name="Randomize STL", geometry=[50 + 155, 65, 150, 30], connector=self.randomize_file)

        # Label to show the current machining feature and selected file path
        manufacturing_name = f"Manufacturing Feature: {' '.join(self.selected_stl_file.parent.stem.split('_')[1:]).title()}"
        self.manufacturing_file_path = self.create_label(label_name=manufacturing_name, position=[50, 110], font_size=12)
        file_name = f"File Name: {self.selected_stl_file.stem}.STL"
        self.file_file_path = self.create_label(label_name=file_name, position=[50, 135], font_size=12)

        # Setup visualizers for original PCD, FPS PCD, and randomly sampled PCD (also labels for them)
        self.vis_original, self.view_control_original = self.setup_visualizers(window_name="Original PCD", pcd=self.pcd)
        self.vis_fps, self.view_control_fps = self.setup_visualizers(window_name="Farthest Point Sampled PCD", pcd=self.fps)
        self.vis_random, self.view_control_random = self.setup_visualizers(window_name="Random Sampled PCD", pcd=self.random)
        self.label_original = self.create_label(label_name="Original PCD", position=[400, 10], font_size=20)
        self.label_fps = self.create_label(label_name="Farthest Point Sampled PCD", position=[50, 360], font_size=20)
        self.label_random = self.create_label(label_name="Random Sampled PCD", position=[400, 360], font_size=20)

        # Setup controllers for sampling pcd and original PCD
        self.sampling_pcd_controller()
        self.original_pcd_controller()

        # Perform initial sampling.
        self.update_sampling(self.initial_num_sampling_points)

        # Embed the Open3D windows
        self.container_original = self.embed_open3d_window(window_name="Original PCD", x=400, y=50, w=300, h=300)
        self.container_fps = self.embed_open3d_window(window_name="Farthest Point Sampled PCD", x=50, y=400, w=300, h=300)
        self.container_random = self.embed_open3d_window(window_name="Random Sampled PCD", x=400, y=400, w=300, h=300)

        # Create update timer
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_vis)
        timer.start(1)

        # Window setup
        self.setWindowTitle('Visualize PCD FPS vs Random Sampling')
        self.setFixedSize(750, 750)
        self.show()

    def sampling_pcd_controller(self) -> None:
        """
        Sets up the UI controls for FPS and randomly sampling PCD

        This method creates a label and a slider to control the number of points to be sampled.
        The slider allows the user to adjust the number of points dynamically, and the label displays
        the current number of sampling points.

        :return: None
        """
        # Create sampling controls (label and a slider)
        self.sampling_slider_label = self.create_label(label_name=f"Sampling Points ({self.initial_num_sampling_points} points)", position=[50, 270], font_size=12)
        self.sampling_slider = self.create_slider(geometry=[50, 295, 300, 20], slider_range=[100, self.initial_num_pcd_points], initial_value=self.initial_num_sampling_points, connector=self.update_sampling)

    def original_pcd_controller(self) -> None:
        """
        Sets up the UI controls for managing the original PCD and its properties.

        This method initializes and configures the following UI elements:
            1. A slider for selecting the number of points in the point cloud.
            2. Input fields for setting the minimum and maximum range of the slider.

        The controls are connected to their respective callback methods.
        """
        # Create sampling controls (label and a slider)
        self.num_points_slider_label = self.create_label(label_name=f"Sample Points ({self.initial_num_pcd_points} points)", position=[50, 180], font_size=12)
        self.num_points_slider = self.create_slider(geometry=[50, 205, 300, 20], slider_range=[100, 10000], initial_value=self.initial_num_pcd_points, connector=self.update_point_cloud)

        # Link the FPS slider's maximum to the original slider's current value
        self.num_points_slider.valueChanged.connect(self.sampling_slider.setMaximum)

        # Create container for min/max input fields
        self.sample_range_layout = self.create_container(geometry=[50, 230, 300, 20])  # Position below the slider

        # Min input field
        self.min_label, self.min_input = self.create_label_and_input_field(label_name="Min:", enabled=True, initial_value="100", connector=self.update_slider_range)
        self.sample_range_layout.addWidget(self.min_label)
        self.sample_range_layout.addWidget(self.min_input)

        # Max input field
        self.max_label, self.max_input = self.create_label_and_input_field(label_name="Max:", enabled=True, initial_value="10000", connector=self.update_slider_range)
        self.sample_range_layout.addWidget(self.max_label)
        self.sample_range_layout.addWidget(self.max_input)

    def update_custom_slider(self) -> None:
        """Update the sampling points slider range based on the maximum and minimum values set by users."""
        self.sampling_slider.setMaximum(self.num_points_slider.value())

    def update_point_cloud(self, num_pcd_points: int) -> None:
        """
        Updates the point cloud visualization based on the current settings.

        :param num_pcd_points: The number of points to sample from the mesh.
        :return: None
        """
        if num_pcd_points != len(self.pcd.points):
            self.pcd = self.mesh.sample_points_poisson_disk(num_pcd_points)
        self.num_points_slider_label.setText(f"Sample Points ({num_pcd_points} points)")

        # Update the sampling slider maximum based on the current number of points
        self.sampling_slider.setMaximum(len(self.pcd.points))

        # Use the current sampling slider value, ensuring it doesn't exceed the number of points
        current_sampling_value = min(self.sampling_slider.value(), len(self.pcd.points))

        # Resample using FPS and random sampling and update the visualizers
        self.update_sampling(current_sampling_value)

        # Update the visualizer for the original PCD
        self.vis_original.clear_geometries()
        self.vis_original.add_geometry(self.pcd)
        self.view_control_original.set_zoom(1)

    def update_sampling(self, num_sampling_points: int) -> None:
        """
        Updates the FPS and randomly sampling PCD and its visualization.

        :param num_sampling_points: The number of points to sample using FPS and random sampling.
        :return: None
        """
        # Update the sampling slider label to reflect the current number of sampling points
        self.sampling_slider_label.setText(f"Sampling Points ({num_sampling_points} points)")

        pcd_array = np.asarray(self.pcd.points)

        # Apply FPS sampling
        fps_indices = fpsample.fps_sampling(pc=pcd_array[:, :3], n_samples=num_sampling_points)
        fps_array = pcd_array[fps_indices]
        self.fps = o3d.geometry.PointCloud()
        self.fps.points = o3d.utility.Vector3dVector(fps_array)

        # Apply random sampling
        randomly_sampled_points = pcd_array[np.random.choice(len(pcd_array), num_sampling_points, replace=False)]
        self.random = o3d.geometry.PointCloud()
        self.random.points = o3d.utility.Vector3dVector(randomly_sampled_points)

        # Update the FPS visualizer with the new FPS point cloud
        self.vis_fps.clear_geometries()
        self.vis_fps.add_geometry(self.fps)
        self.view_control_fps.set_zoom(1)

        # Update the random sampling visualizer with the new random sampled point cloud
        self.vis_random.clear_geometries()
        self.vis_random.add_geometry(self.random)
        self.view_control_random.set_zoom(1)

    def update_STL_file(self) -> None:
        """Updates the application state to load and display a new STL file"""
        self.update_point_cloud(self.num_points_slider.value())  # Update the original point cloud visualizer


class VisualizePCD_BallQuery_vs_kNN(QtWidgets.QMainWindow, VisualizerClass):
    def __init__(self, *args, **kwargs):
        """
        Initializes the main application window for visualizing ball query vs kNN

        This method initializes and configures the following:
            - Selects and loads STL file from path and samples it into a PCD
            - Sets the color to gray and normalizes it to be in a unit circle
            - Applies initial sampling for FPS with half the current number of points
            - Applies initial ball query and kNN algorithms
            - Configures visualizers for the original, FPS, and ball query vs kNN PCD

        :param args: Positional arguments passed to the parent class.
        :param kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(*args, **kwargs)

        # Set up the base path
        self.base_path = Path().cwd() / 'MFD_dataset'

        # Initially, load a random STL file
        self.selected_stl_file = self.get_random_stl_file()
        print(f"Visualizing random STL file: {self.selected_stl_file}")

        # Load mesh, sample points, set color to gray, and normalize PCD
        self.mesh = o3d.io.read_triangle_mesh(self.selected_stl_file)
        self.initial_num_pcd_points = 1000
        self.pcd = self.mesh.sample_points_poisson_disk(self.initial_num_pcd_points)
        self.set_pcd_colors(pcd=self.pcd, colors=[[0.5, 0.5, 0.5] for _ in range(len(self.pcd.points))])
        self.normalize_pcd(pcd=self.pcd)

        # Define initial sampling point count
        self.initial_num_sampling_points = self.initial_num_pcd_points // 2

        # Create an empty placeholder for FPS and ball query vs kNN PCD; it will be updated later
        self.fps = o3d.geometry.PointCloud()
        self.bq_vs_kNN = o3d.geometry.PointCloud()

        # Setup the main Qt window with a central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # Buttons to select a file or to randomize the STL file from the base path
        self.btn_select_file = self.create_button(label_name="Select File", geometry=[50, 40, 150, 30], connector=self.select_file)
        self.btn_randomize = self.create_button(label_name="Randomize STL", geometry=[50 + 155, 40, 150, 30], connector=self.randomize_file)

        # Label to show the current machining feature and selected file path
        manufacturing_name = f"Manufacturing Feature: {' '.join(self.selected_stl_file.parent.stem.split('_')[1:]).title()}"
        self.manufacturing_file_path = self.create_label(label_name=manufacturing_name, position=[50, 85], font_size=12)
        file_name = f"File Name: {self.selected_stl_file.stem}.STL"
        self.file_file_path = self.create_label(label_name=file_name, position=[50, 110], font_size=12)

        # Setup visualizers for original PCD, FPS PCD, and ball query vs kNN PCD (also labels for them)
        self.vis_original, self.view_control_original = self.setup_visualizers(window_name="Original PCD", pcd=self.pcd)
        self.vis_fps, self.view_control_fps = self.setup_visualizers(window_name="Farthest Point Sampled PCD", pcd=self.fps)
        self.vis_bq_vs_kNN, self.view_control_bq_vs_kNN = self.setup_visualizers(window_name="Ball Query vs kNN PCD", pcd=self.bq_vs_kNN)
        self.label_original = self.create_label(label_name="Original PCD", position=[400, 10], font_size=20)
        self.label_fps = self.create_label(label_name="Farthest Point Sampled PCD", position=[50, 360], font_size=20)
        self.label_bq_vs_kNN = self.create_label(label_name="Ball Query vs kNN PCD", position=[400, 360], font_size=20)

        # Setup controllers for ball query vs kNN pcd and original PCD
        self.bq_vs_kNN_pcd_controller()
        self.original_pcd_controller()

        # Perform initial FPS sampling, ball query algorithm, and kNN algorithm
        self.update_bq_vs_kNN(self.initial_num_sampling_points)

        # Embed the Open3D windows
        self.container_original = self.embed_open3d_window(window_name="Original PCD", x=400, y=50, w=300, h=300)
        self.container_fps = self.embed_open3d_window(window_name="Farthest Point Sampled PCD", x=50, y=400, w=300, h=300)
        self.container_bq_vs_kNN = self.embed_open3d_window(window_name="Ball Query vs kNN PCD", x=400, y=400, w=300, h=300)

        # Create update timer
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_vis)
        timer.start(1)

        # Window setup
        self.setWindowTitle('Visualize PCD Ball Query vs kNN')
        self.setFixedSize(750, 750)
        self.show()

    def bq_vs_kNN_pcd_controller(self) -> None:
        """
        Sets up the UI controls for FPS and ball query vs kNN

        This method initializes and configures UI elements consisting of labels, input fields, amd checkboxes, for
        controlling the following functions:
            - Label and a slider to control the number of points to be sampled using FPS
            - Label and input field for the size of radius of ball query algorithm
            - Label and input field for the k nearest neighbours to choose from for ball query and kNN algorithms

        :return: None
        """
        # Create sampling controls (label and a slider)
        self.sampling_slider_label = self.create_label(label_name=f"Sampling Points ({self.initial_num_sampling_points} points)", position=[50, 245], font_size=12)
        self.sampling_slider = self.create_slider(geometry=[50, 270, 300, 20], slider_range=[100, self.initial_num_pcd_points], initial_value=self.initial_num_sampling_points, connector=self.update_bq_vs_kNN)

        # Ball query vs kNN parameters - radius and k (label and input field's)
        self.bq_vs_kNN_params = self.create_container(geometry=[50, 295, 300, 40], vertical=False)

        self.radius_layout = self.create_container(geometry=[50, 295, 140, 20], vertical=False)
        self.radius_label, self.radius_value = self.create_label_and_input_field(label_name="Radius", enabled=True, initial_value="0.1", connector=self.update_k_r)
        self.radius_layout.addWidget(self.radius_label)
        self.radius_layout.addWidget(self.radius_value)

        self.k_layout = self.create_container(geometry=[50 + 140, 295, 140, 20], vertical=False)
        self.k_label, self.k_value = self.create_label_and_input_field(label_name="k", enabled=True, initial_value="32", connector=self.update_k_r)
        self.k_layout.addWidget(self.k_label)
        self.k_layout.addWidget(self.k_value)

        self.bq_vs_kNN_params.addLayout(self.radius_layout)
        self.bq_vs_kNN_params.addLayout(self.k_layout)

    def original_pcd_controller(self) -> None:
        """
        Sets up the UI controls for managing the original PCD and its properties.

        This method initializes and configures the following UI elements:
            1. A slider for selecting the number of points in the point cloud.
            2. Input fields for setting the minimum and maximum range of the slider.

        The controls are connected to their respective callback methods.
        """
        # Create sampling controls (label and a slider)
        self.num_points_slider_label = self.create_label(label_name=f"Sample Points ({self.initial_num_pcd_points} points)", position=[50, 155], font_size=12)
        self.num_points_slider = self.create_slider(geometry=[50, 180, 300, 20], slider_range=[100, 10000], initial_value=self.initial_num_pcd_points, connector=self.update_point_cloud)

        # Link the FPS slider's maximum to the original slider's current value
        self.num_points_slider.valueChanged.connect(self.sampling_slider.setMaximum)

        # Create container for min/max input fields
        self.sample_range_layout = self.create_container(geometry=[50, 205, 300, 20])  # Position below the slider

        # Min input field
        self.min_label, self.min_input = self.create_label_and_input_field(label_name="Min:", enabled=True, initial_value="100", connector=self.update_slider_range)
        self.sample_range_layout.addWidget(self.min_label)
        self.sample_range_layout.addWidget(self.min_input)

        # Max input field
        self.max_label, self.max_input = self.create_label_and_input_field(label_name="Max:", enabled=True, initial_value="10000", connector=self.update_slider_range)
        self.sample_range_layout.addWidget(self.max_label)
        self.sample_range_layout.addWidget(self.max_input)

    def update_custom_slider(self) -> None:
        """Update the sampling points slider range based on the maximum and minimum values set by users."""
        self.sampling_slider.setMaximum(self.num_points_slider.value())

    def update_point_cloud(self, num_pcd_points: int) -> None:
        """
        Updates the point cloud visualization based on the current settings.

        :param num_pcd_points: The number of points to sample from the mesh.
        :return: None
        """
        # Update the point cloud and color if the number of points has changed
        if num_pcd_points != len(self.pcd.points):
            self.pcd = self.mesh.sample_points_poisson_disk(num_pcd_points)
            self.normalize_pcd(pcd=self.pcd)
        self.num_points_slider_label.setText(f"Sample Points ({num_pcd_points} points)")
        self.set_pcd_colors(pcd=self.pcd, colors=[[0.5, 0.5, 0.5] for _ in range(len(self.pcd.points))])

        # Update the sampling slider maximum based on the current number of points
        self.sampling_slider.setMaximum(len(self.pcd.points))

        # Use the current sampling slider value, ensuring it doesn't exceed the number of points
        current_sampling_value = min(self.sampling_slider.value(), len(self.pcd.points))

        # Resample using FPS and apply ball query and kNN algorithms and update the visualizers
        self.update_bq_vs_kNN(current_sampling_value)

        # Update the visualizer for the original PCD
        self.vis_original.clear_geometries()
        self.vis_original.add_geometry(self.pcd)
        self.view_control_original.set_zoom(1)

    def update_bq_vs_kNN(self, num_sampling_points: int, resample: bool = True) -> None:
        """
        Updates the FPS and ball query vs kNN visualizations by performing the following functions:
            1. Resamples the PCD using FPS and updates the FPS slider label and set FPS points to red (if requested)
            2. If the number of FPS points changed, or if resampled pick a single new random centroid
            3. Use the random centroid to implement ball query to pick k points within radius r
            4. Use the random centroid to implement kNN to pick k points
            5. Identify points selected by ball query, kNN, or both and assign colors for each group of points
            6. Create a green wireframe sphere for ball query visualization and blue lines for kNN visualization
            7. Update the ball query vs kNN PCD with the new colors
            8. Update the FPS visualizer (if FPS was re-sampled)

        :param num_sampling_points: The number of points to sample using FPS and random sampling.
        :param resample: If True, re-sample FPS and select a new centroid if needed. If False, reuse the previous FPS sample and centroid.
        """
        # Update the sampling slider label to reflect the current number of sampling points
        self.sampling_slider_label.setText(f"Sampling Points ({num_sampling_points} points)")

        pcd_array = np.asarray(self.pcd.points)

        # Only re-run FPS sampling if resample is True.
        if resample:
            # Apply FPS sampling
            fps_indices = fpsample.fps_sampling(pc=pcd_array[:, :3], n_samples=int(num_sampling_points))
            self.fps_indices = fps_indices  # store for later use
            self.fps = o3d.geometry.PointCloud()
            self.fps.points = o3d.utility.Vector3dVector(pcd_array)
            self.fps.normals = self.pcd.normals if self.pcd.has_normals() else None
            self.set_pcd_colors(pcd=self.fps, colors=[[0.5, 0.5, 0.5] for _ in range(len(self.fps.points))])

            # Color the FPS points red
            fps_colors = np.asarray(self.fps.colors)
            fps_colors[fps_indices] = [1, 0, 0]
            self.set_pcd_colors(pcd=self.fps, colors=fps_colors)
        else:
            # Reuse the stored FPS indices
            fps_indices = self.fps_indices

        # Update the centroid only if re-sampling is allowed and the number of sampling points has changed.
        if resample and ((not hasattr(self, "last_num_sampling_points")) or (num_sampling_points != self.last_num_sampling_points)):
            self.selected_centroid_idx = fps_indices[np.random.choice(len(fps_indices))]
            self.last_num_sampling_points = num_sampling_points

        # Use the selected centroid from the previous update if resample is False.
        centroid = pcd_array[self.selected_centroid_idx]

        # Get current parameters from input fields
        self.radius = float(self.radius_value.text())  # Radius for ball query
        self.k = int(self.k_value.text())  # Number of nearest neighbors and max points for ball query

        # Implement ball query
        dists = np.sum((pcd_array - centroid) ** 2, axis=1)  # Squared Euclidean distances
        ball_query_idxs = np.where(dists <= self.radius ** 2)[0]
        if len(ball_query_idxs) > self.k:
            ball_query_idxs = ball_query_idxs[:self.k]

        # Implement kNN
        knn_idxs = np.argpartition(dists, self.k)[:self.k]

        # Identify points selected by ball query, kNN, or both
        ball_set = set(ball_query_idxs)
        knn_set = set(knn_idxs)
        both_idxs = list(ball_set & knn_set)  # Intersection
        ball_only_idxs = list(ball_set - knn_set)  # Ball query only
        knn_only_idxs = list(knn_set - ball_set)  # kNN only

        # Assign colors for each group of points
        colors = np.full((len(pcd_array), 3), 0.5)  # Default gray
        colors[self.selected_centroid_idx] = [1, 0, 0]  # Red for the centroid
        colors[ball_only_idxs] = [0, 1, 0]  # Green for ball query only
        colors[knn_only_idxs] = [0, 0, 1]  # Blue for kNN only
        colors[both_idxs] = [1, 0, 1]  # Magenta for both

        # Create a green wireframe sphere for ball query visualization
        sphere = o3d.geometry.TriangleMesh.create_sphere(self.radius)
        sphere.translate(centroid)
        self.wireframe = o3d.geometry.LineSet.create_from_triangle_mesh(sphere)
        self.wireframe.paint_uniform_color([0, 1, 0])

        # Add blue lines for kNN visualization
        lines = [[0, j] for j in range(1, self.k + 1)]
        line_points = [centroid] + [pcd_array[idx] for idx in knn_idxs]
        self.line_set = o3d.geometry.LineSet()
        self.line_set.points = o3d.utility.Vector3dVector(line_points)
        self.line_set.lines = o3d.utility.Vector2iVector(lines)
        self.line_set.colors = o3d.utility.Vector3dVector([[0, 0, 1] for _ in lines])

        # Update the ball query vs kNN with the new colors
        self.bq_vs_kNN.points = o3d.utility.Vector3dVector(pcd_array)
        self.bq_vs_kNN.normals = self.pcd.normals if self.pcd.has_normals() else None
        self.bq_vs_kNN.colors = o3d.utility.Vector3dVector(colors)

        # Update the FPS visualizer (if FPS was re-sampled)
        self.vis_fps.clear_geometries()
        self.vis_fps.add_geometry(self.fps)
        self.view_control_fps.set_zoom(1)

        # Update the ball query vs kNN visualizer with the updated point cloud and helper geometries
        self.vis_bq_vs_kNN.clear_geometries()
        self.vis_bq_vs_kNN.add_geometry(self.bq_vs_kNN)
        self.vis_bq_vs_kNN.add_geometry(self.line_set)
        self.vis_bq_vs_kNN.add_geometry(self.wireframe)
        self.view_control_bq_vs_kNN.set_zoom(1)

    def update_k_r(self):
        """Updates the visualization when the k (number of nearest neighbors) or radius parameters are modified."""
        current_sampling_points = self.sampling_slider.value()  # Get the current number of sampling points from the slider
        self.update_bq_vs_kNN(current_sampling_points, resample=False)  # Update the visualization without reselecting the centroid.

    def set_pcd_colors(self, pcd, colors) -> None:
        """
        Helper method to set the colors of the provided point cloud.

        :param pcd: The point cloud to update.
        :param colors: The colors to assign to the point cloud.
        """
        pcd.colors = o3d.utility.Vector3dVector(colors)

    def normalize_pcd(self, pcd) -> None:
        """
        Normalize a PCD to fit within a unit sphere centered at the origin

        :param pcd: PCD to normalize
        :return: None
        """
        # Normalize PCD
        point_cloud = np.asarray(self.pcd.points, dtype=float)
        centroid = np.mean(point_cloud, axis=0)
        point_cloud_centered = point_cloud - centroid
        scale_factor = np.max(np.sqrt(np.sum(point_cloud_centered ** 2, axis=1)))
        point_cloud_normalized = point_cloud_centered / scale_factor
        pcd.points = o3d.utility.Vector3dVector(point_cloud_normalized)

    def update_STL_file(self) -> None:
        """Updates the application state to load and display a new STL file"""
        self.normalize_pcd(pcd=self.pcd)  # Normalize PCD
        self.update_point_cloud(self.num_points_slider.value())  # Update the original point cloud visualizer
