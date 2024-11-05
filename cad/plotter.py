import pyvista as pv
import numpy as np

from cad.util import pv_faces


def cylinder(p1, p2, radius):
    return pv.Cylinder(
        center=(p1 + p2) / 2,
        direction=(p2 - p1),
        radius=radius,
        height=np.linalg.norm(p1 - p2),
    )


def show_model(floors, objs, grid, start, end, path, conf):
    # Build PyVista objects
    floor_surfs = list(map(lambda f: pv.PolyData(f.vertices, pv_faces(f.faces)), floors))
    obj_surfs = list(map(lambda f: pv.PolyData(f.vertices, pv_faces(f.faces)), objs))
    grid_surf = pv.PolyData(grid)

    radius = conf['wire_width']

    # Wire has cylinder structure
    path_surfs = [cylinder(path[i], path[i + 1], radius) for i in range(len(path) - 1)] + list(map(lambda p: pv.Sphere(center=p, radius=radius), path))

    plotter = pv.Plotter()
    plotter.background_color = "aqua"

    # Actors are used for visibility toggling
    floor_actors = list(map(lambda s: plotter.add_mesh(s, color='white'), floor_surfs))
    obj_actors = list(map(lambda s: plotter.add_mesh(s, color='silver'), obj_surfs))
    grid_actors = [plotter.add_mesh(grid_surf, color='black')]
    path_actors = list(map(lambda s: plotter.add_mesh(s, color='red'), path_surfs))

    # Add start and end points
    plotter.add_mesh(pv.Sphere(center=start, radius=radius+1), color='green')
    plotter.add_mesh(pv.Sphere(center=end, radius=radius+1), color='blue')

    def get_toggler(actors):
        def toggle_vis(flag):
            for a in actors:
                a.SetVisibility(flag)
        return toggle_vis

    # Add buttons with captions
    plotter.add_text(
        'floor',
        position=(10, 70),
        font_size=12,
    )
    plotter.add_checkbox_button_widget(
        get_toggler(floor_actors),
        position=(10, 10),
        value=True,
        color_on='white',
    )
    plotter.add_text(
        'objects',
        position=(100, 70),
        font_size=12,
    )
    plotter.add_checkbox_button_widget(
        get_toggler(obj_actors),
        position=(100, 10),
        value=True,
        color_on='silver',
    )
    plotter.add_text(
        'grid',
        position=(190, 70),
        font_size=12,
    )
    grid_actors[0].SetVisibility(False)
    plotter.add_checkbox_button_widget(
        get_toggler(grid_actors),
        position=(190, 10),
        value=False,
        color_on='black',
    )
    plotter.add_text(
        'path',
        position=(280, 70),
        font_size=12,
    )
    plotter.add_checkbox_button_widget(
        get_toggler(path_actors),
        position=(280, 10),
        value=True,
        color_on='red',
    )

    plotter.show()
