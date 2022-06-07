from typing import List, Optional

import napari
from napari.layers import Tracks
from napari.utils.events import Event
from napari.utils.events import Event
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QWidget

from .visualisation import (
    MPLPropertyPlotter,
    PropertyPlotterBase,
    TreePlotterQWidgetBase,
    VisPyPlotter,
)

GUI_MAXIMUM_WIDTH = 400


class Arboretum(QWidget):
    """
    Tree viewer widget.
    """

    def __init__(self, viewer: napari.Viewer, parent=None):
        super().__init__(parent=parent)
        self.viewer = viewer
        self.plotter: TreePlotterQWidgetBase = VisPyPlotter()
        self.property_plotter: PropertyPlotterBase = MPLPropertyPlotter(viewer)

        # Set plugin layout
        layout = QGridLayout()
        # Make the tree plot a bigger than the property plot
        for row, stretch in zip([0, 1], [2, 1]):
            layout.setRowStretch(row, stretch)
        self.setLayout(layout)

        # Add tree plotter
        row, col = 0, 0
        layout.addWidget(self.plotter.get_qwidget(), row, col)
        # Add property plotter
        row = 1
        layout.addWidget(self.property_plotter.get_qwidget(), row, col)

        # Update the list of tracks layers stored in this object if the layer
        # list changes
        self.viewer.layers.events.changed.connect(self.update_tracks_layers)
        # Update the horizontal time line if the current z-step changes
        self.viewer.dims.events.current_step.connect(self.draw_current_time_line)

        self.tracks_layers: List[Tracks] = []
        self.update_tracks_layers()

    @property
    def tracks(self) -> Tracks:
        """
        Tracks layer being plotted in the widget.
        """
        return self._tracks

    @tracks.setter
    def tracks(self, tracks: Tracks) -> None:
        self._tracks = tracks
        self.plotter.tracks = tracks
        self.property_plotter.tracks = tracks

    @property
    def track_id(self) -> int:
        """
        ID of the specific track being plotted in the widget.
        """
        return self._track_id

    @track_id.setter
    def track_id(self, track_id: int) -> None:
        self._track_id = track_id
        self.plotter.track_id = track_id
        self.property_plotter.track_id = track_id

    def update_tracks_layers(self, event: Optional[Event] = None) -> None:
        """
        Save a copy of all the tracks layers that are present in the viewer.
        """
        layers = [layer for layer in self.viewer.layers if isinstance(layer, Tracks)]

        for layer in layers:
            if layer not in self.tracks_layers:
                # Add callback to draw graph when layer clicked
                self.append_mouse_callback(layer)
                # Add callback to change tree colours when layer colours changed
                layer.events.color_by.connect(self.plotter.update_edge_colors)
                layer.events.colormap.connect(self.plotter.update_edge_colors)
                layer.events.color_by.connect(self.property_plotter.plot_property)

        self.tracks_layers = layers

    def append_mouse_callback(self, track_layer: Tracks) -> None:
        """
        Add a mouse callback to ``track_layer`` to draw the tree
        when the layer is clicked.
        """

        @track_layer.mouse_drag_callbacks.append
        def show_tree(tracks: Tracks, event: Event) -> None:
            self.tracks = tracks

            cursor_position = event.position
            track_id = tracks.get_value(cursor_position, world=True)
            if track_id is not None:
                # Setting this property automatically triggers re-drawing of the
                # tree and property graph
                self.track_id = track_id

    def draw_current_time_line(self, event: Optional[Event] = None) -> None:
        if not self.plotter.has_tracks:
            return
        z_value = self.viewer.dims.current_step[0]
        self.plotter.draw_current_time_line(z_value)
