from visualizers import (
    VisualizePCD_FPS_vs_RandomSampling,
    VisualizePCD_BallQuery_vs_kNN,
)

if __name__ == '__main__':
    # Run the desired visualizer by uncommenting its line.
    VisualizePCD_FPS_vs_RandomSampling.run()  # FPS vs Random Sampling Visualizer
    # VisualizePCD_BallQuery_vs_kNN.run()     # Ball Query vs kNN Visualizer