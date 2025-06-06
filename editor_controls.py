import enum

from math import pi, tan, atan2, degrees
from timeit import default_timer
import abc

from PyQt6.QtCore import Qt
from lib.vectors import Vector3, Plane, Vector2
from gizmo import AXIS_X, AXIS_Y, AXIS_Z
import numpy

import typing
if typing.TYPE_CHECKING:
    from bw_widgets import BolMapViewer

MOUSE_MODE_NONE = 0
MOUSE_MODE_MOVEWP = 1
MOUSE_MODE_ADDWP = 2
MOUSE_MODE_CONNECTWP = 3

MODE_TOPDOWN = 0
MODE_3D = 1


class ViewMode(enum.Enum):
    VIEW_TOPDOWN = 0
    VIEW_3D = 1


key_enums = {
    "Middle": Qt.MouseButton.MiddleButton,
    "Left": Qt.MouseButton.LeftButton,
    "Right": Qt.MouseButton.RightButton
}


class MouseMode(enum.Enum):
    NONE = 0
    ADD_OBJECT = 1
    PLUGIN = 2


class EditorMouseMode(object):
    def __init__(self):
        self.mode: MouseMode = MouseMode.NONE
        self.plugin_modes: list[str] = []
        self.plugin_mode_none: int = self.add_plugin_mode("NONE")
        self.plugin_mode: int = self.plugin_mode_none

        self.callback_change_to = {}
        self.callback_change_from = {}

    def add_change_to_callback(self, mode, func):
        self.callback_change_to[mode] = func

    def add_change_from_callback(self, mode, func):
        self.callback_change_from[mode] = func

    def set_mode(self, mode: MouseMode):
        assert isinstance(mode, MouseMode)
        self.mode = mode

    # Add plugin mode and return its index for identification
    def add_plugin_mode(self, mode_name: str):
        if mode_name not in self.plugin_modes:
            self.plugin_modes.append(mode_name)
            return len(self.plugin_modes) - 1
        else:
            return self.plugin_modes.index(mode_name)

    def set_plugin_mode(self, mode: int):
        assert 0 <= mode < len(self.plugin_modes)
        self.set_mode(MouseMode.PLUGIN)
        self.plugin_mode = mode

    def active(self, mode: MouseMode):
        return self.mode == mode

    def plugin_active(self, mode: int):
        return self.mode == MouseMode.PLUGIN and self.plugin_mode == mode


class Buttons(object):
    def __init__(self):
        self._buttons = {}
        for key in key_enums:
            self._buttons[key] = False

    def update_status(self, event):
        for key in key_enums:
            self._buttons = event.buttons() & key_enums[key]

    def just_pressed(self, event, key):
        return not self._buttons[key] and self.is_held(event, key)

    def is_held(self, event, key):
        self._buttons[key] = event.buttons() & key_enums[key]
        return self._buttons[key]

    def just_released(self, event, key):
        return self._buttons[key] and not self.is_held(event, key)


class MouseAction(object):
    def __init__(self, name):
        self.name = name

    def condition(self, editor, buttons, event):
        return True


class ClickAction(MouseAction):
    def __init__(self, name, key):
        super().__init__(name)
        self.key = key
        assert key in key_enums

    def condition(self, editor, buttons, event):
        return True

    def just_clicked(self, editor, buttons, event):
        pass

    def move(self, editor, buttons, event):
        pass

    def just_released(self, editor, buttons, event):
        pass


class ClickDragAction(MouseAction):
    def __init__(self, name, key):
        super().__init__(name)
        self.key = key
        assert key in key_enums

        self.first_click = None

    def just_clicked(self, editor, buttons, event):
        self.first_click = Vector2(event.position().x(), event.position().y())

    def move(self, editor, buttons, event):

        pass

    def just_released(self, editor, buttons, event):
        self.first_click = None

    def moved(self, event):
        return self.first_click.x != event.position().x() or self.first_click.y != event.position().y()


class PluginEventClickAction(ClickAction):
    def just_clicked(self, editor: "BolMapViewer", buttons, event):
        super().just_clicked(editor, buttons, event)

        x, y = event.position().x(), event.position().y()
        editor.plugin_handler.execute_event("topdown_click", editor, x, y)

        worldx, worldy = editor.mouse_coord_to_world_coord(x, y)
        editor.plugin_handler.execute_event("world_click", editor, worldx, worldy)

        height = editor.bwterrain.check_height(worldx, worldy)
        if height is None:
            height = editor.waterheight
        editor.plugin_handler.execute_event("terrain_click_2d", editor, Vector3(worldx, worldy, height))


class PluginEvent3DTerrainClickAction(ClickAction):
    def just_clicked(self, editor: "BolMapViewer", buttons, event):
        super().just_clicked(editor, buttons, event)
        x, y = event.position().x(), event.position().y()

        ray = editor.create_ray_from_mouseclick(x, y)
        editor.plugin_handler.execute_event("raycast_3d", editor, ray)

        swapped_ray = ray.swapped_yz()
        result = editor.bwterrain.ray_collide(swapped_ray)

        if result:
            print("we did hit something")
            point, d = result
            point.swap_yz()

            editor.plugin_handler.execute_event("terrain_click_3d", editor, ray, point)
        else:
            plane = Plane.xy_aligned(Vector3(0.0, 0.0, 0.0))
            collision = ray.collide_plane(plane)
            if collision is not False:
                place_at, _ = collision
                editor.plugin_handler.execute_event("terrain_click_3d", editor, ray, place_at)


class TopdownScroll(ClickDragAction):
    def move(self, editor, buttons, event):
        x, y = event.position().x(), event.position().y()
        d_x, d_y = event.position().x() - self.first_click.x, event.position().y() - self.first_click.y

        adjusted_dx = d_x * editor.zoom_factor  # (1.0 + (self.zoom_factor - 1.0))
        adjusted_dz = d_y * editor.zoom_factor  # (1.0 + (self.zoom_factor - 1.0))

        editor.offset_x += adjusted_dx
        editor.offset_z += adjusted_dz
        editor.do_redraw()
        self.first_click.x = event.position().x()
        self.first_click.y = event.position().y()


class TopdownSelect(ClickDragAction):
    def condition(self, editor, buttons, event):
        return (editor.gizmo.was_hit_at_all is not True) and editor.mouse_mode.active(MouseMode.NONE)

    def just_clicked(self, editor, buttons, event):
        super().just_clicked(editor, buttons, event)
        x, y = self.first_click.x, self.first_click.y

        selectstartx, selectstartz = editor.mouse_coord_to_world_coord(x, y)

        editor.selectionbox_start = (selectstartx, selectstartz)

        if editor.level_file is not None:
            #editor.selectionqueue.queue_selection(x, y, 1, 1,
            #                               editor.shift_is_pressed)
            editor.select_objects(x, y, shift=editor.shift_is_pressed)
            editor.do_redraw(forceselected=True)
            editor.do_redraw(forceselected=True)

    def move(self, editor, buttons, event):
        selectendx, selectendz = editor.mouse_coord_to_world_coord(event.position().x(), event.position().y())
        editor.selectionbox_end = (selectendx, selectendz)
        editor.do_redraw()

    def just_released(self, editor, buttons, event):
        if self.first_click is None:
            return

        selectstartx, selectstartz = self.first_click.x, self.first_click.y
        selectendx, selectendz = event.position().x(), event.position().y()

        startx = min(selectstartx, selectendx)
        endx = max(selectstartx, selectendx)
        startz = min(selectstartz, selectendz)
        endz = max(selectstartz, selectendz)

        #editor.selectionqueue.queue_selection(int(startx), int(endz), int(endx - startx) + 1, int(endz - startz) + 1,
        #                               editor.shift_is_pressed)
        if endx-startx != 0 or endz-startz != 0:
            editor.select_objects(int(startx), int(endz), int(endx - startx) + 1, int(endz - startz) + 1,
                                  shift=editor.shift_is_pressed)
            editor.do_redraw(forceselected=True)
        editor.last_selectionbox = (editor.selectionbox_start, editor.selectionbox_end)
        editor.selectionbox_start = editor.selectionbox_end = None
        editor.do_redraw()


class Gizmo2DMoveX(ClickDragAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_state = None
        self.moved = False
        self.was_hidden = False

    def just_clicked(self, editor, buttons, event):
        super().just_clicked(editor, buttons, event)

        self.start_state = editor.history.stash_selected()
        self.moved = False

    def move(self, editor, buttons, event):
        if editor.gizmo.was_hit["gizmo_x"]:
            editor.gizmo.hidden = True
            editor.gizmo.set_render_axis(AXIS_X)
            delta_x = event.position().x() - self.first_click.x
            self.first_click = Vector2(event.position().x(), event.position().y())
            editor.move_points.emit(delta_x*editor.zoom_factor, 0, 0)
            self.moved = True

    def just_released(self, editor, buttons, event):
        if self.moved:
            startstate = self.start_state
            editor.history.record_move(startstate)
            self.moved = False
            self.start_state = None

        super().just_released(editor, buttons, event)
        editor.gizmo.hidden = False
        editor.gizmo.reset_axis()
        editor.gizmo.move_to_average(editor.selected,
                                     editor.bwterrain,
                                     editor.waterheight,
                                     editor.dolphin.do_visualize())


class Gizmo2DMoveXZ(Gizmo2DMoveX):
    def move(self, editor, buttons, event):
        if editor.gizmo.was_hit["middle"]:
            editor.gizmo.hidden = True
            #editor.gizmo.set_render_axis(AXIS_X)
            delta_x = event.position().x() - self.first_click.x
            delta_z = event.position().y() - self.first_click.y
            self.first_click = Vector2(event.position().x(), event.position().y())
            editor.move_points.emit(delta_x*editor.zoom_factor, 0, -delta_z*editor.zoom_factor)
            self.moved = True


class Gizmo2DMoveZ(Gizmo2DMoveX):
    def move(self, editor, buttons, event):
        if editor.gizmo.was_hit["gizmo_z"]:
            editor.gizmo.hidden = True
            editor.gizmo.set_render_axis(AXIS_Z)
            delta_z = event.position().y() - self.first_click.y
            self.first_click = Vector2(event.position().x(), event.position().y())
            editor.move_points.emit(0, 0, -delta_z*editor.zoom_factor)
            self.moved = True


class Gizmo2DRotateY(Gizmo2DMoveX):
    def just_clicked(self, editor, buttons, event):
        super().just_clicked(editor, buttons, event)
        self.was_hidden = False

    def move(self, editor, buttons, event):
        if editor.gizmo.was_hit["rotation_y"]:
            editor.gizmo.hidden = True
            self.was_hidden = True
            #editor.gizmo.set_render_axis(AXIS_Z)

            x, y = editor.mouse_coord_to_world_coord(self.first_click.x, self.first_click.y)
            angle_start = atan2((y - editor.gizmo.position.z), x - editor.gizmo.position.x)

            x, y = editor.mouse_coord_to_world_coord(event.position().x(), event.position().y())
            angle = atan2((y - editor.gizmo.position.z), x - editor.gizmo.position.x)
            delta = angle_start - angle


            editor.rotate_current.emit(Vector3(0, delta, 0))

            self.first_click = Vector2(event.position().x(), event.position().y())
            self.moved = True

    def just_released(self, editor, buttons, event):
        super().just_released(editor, buttons, event)
        if self.was_hidden:
            editor.gizmo.hidden = False
        editor.gizmo.reset_axis()
        #editor.gizmo.move_to_average(editor.selected)


class AddObjectTopDown(ClickAction):
    def condition(self, editor, buttons, event):
        return False # editor.mousemode == MOUSE_MODE_ADDWP

    def just_clicked(self, editor, buttons, event):
        mouse_x, mouse_z = (event.position().x(), event.position().y())
        destx, destz = editor.mouse_coord_to_world_coord(mouse_x, mouse_z)

        editor.create_waypoint.emit(destx, -destz)


class RotateCamera3D(ClickDragAction):
    def condition(self, editor, buttons, event):
        return not buttons.is_held(event, "Left") #and editor.mousemode == MOUSE_MODE_NONE)

    def move(self, editor, buttons, event):
        curr_x, curr_y = event.position().x(), event.position().y()
        last_x, last_y = self.first_click.x, self.first_click.y

        diff_x = curr_x - last_x
        diff_y = curr_y - last_y

        self.first_click = Vector2(curr_x, curr_y)

        editor.camera_horiz = (editor.camera_horiz - diff_x * (pi / 500)) % (2 * pi)
        editor.camera_vertical = (editor.camera_vertical - diff_y * (pi / 600))
        if editor.camera_vertical > pi / 2.0:
            editor.camera_vertical = pi / 2.0
        elif editor.camera_vertical < -pi / 2.0:
            editor.camera_vertical = -pi / 2.0

        # print(self.camera_vertical, "hello")
        editor.do_redraw()


ufac = 500


class Select3D(ClickDragAction):
    def condition(self, editor: "BolMapViewer", buttons, event):
        return editor.mouse_mode.active(MouseMode.NONE) and not buttons.is_held(event, "Right") and not editor.gizmo.was_hit_at_all

    def just_clicked(self, editor, buttons, event):
        super().just_clicked(editor, buttons, event)

        #editor.select_objects(event.position().x(), event.position().y(), shift=editor.shift_is_pressed)
        #editor.selectionqueue.queue_selection(
        #    event.x(), event.y(), 1, 1,
        #    editor.shift_is_pressed)
        #print("WE HAVE SENT A REQUEST")
        #editor.do_redraw(forceselected=True)


        editor.camera_direction.normalize()

        ray = editor.create_ray_from_mouseclick(event.position().x(), event.position().y())
        editor.selectionbox_projected_origin = ray.origin + ray.direction*ufac# * 0.1

    def move(self, editor, buttons, event):
        upleft = editor.create_ray_from_mouseclick(self.first_click.x, event.position().y())
        upright = editor.create_ray_from_mouseclick(event.position().x(), event.position().y())
        downright = editor.create_ray_from_mouseclick(event.position().x(), self.first_click.y)

        editor.selectionbox_projected_coords = (
            upleft.origin + upleft.direction*ufac,# * 0.1,
            upright.origin + upright.direction*ufac,# * 0.1,
            downright.origin + downright.direction*ufac# * 0.1
        )

        #selectendx, selectendz = editor.mouse_coord_to_world_coord(event.x(), event.y())
        #editor.selectionbox_end = (selectendx, selectendz)
        editor.do_redraw()

    def just_released(self, editor, buttons, event):
        if self.first_click is None:
            return

        selectstartx, selectstartz = self.first_click.x, self.first_click.y
        selectendx, selectendz = event.position().x(), event.position().y()

        startx = min(selectstartx, selectendx)
        endx = max(selectstartx, selectendx)
        startz = min(selectstartz, selectendz)
        endz = max(selectstartz, selectendz)

        #editor.selectionqueue.queue_selection(int(startx), int(endz), int(endx - startx) + 1, int(endz - startz) + 1,
        #                               editor.shift_is_pressed)
        editor.select_objects(int(startx), int(endz), int(endx - startx) + 1, int(endz - startz) + 1,
                               shift=editor.shift_is_pressed)
        editor.do_redraw(forceselected=True)

        editor.selectionbox_projected_origin = None
        editor.selectionbox_projected_coords = None
        editor.do_redraw()


class AddObject3D(ClickAction):
    def condition(self, editor, buttons, event):
        return False #editor.mousemode == MOUSE_MODE_ADDWP

    def just_clicked(self, editor, buttons, event):
        #print("added object in 3d")
        ray = editor.create_ray_from_mouseclick(event.position().x(), event.position().y())
        place_at = None

        if editor.collision is not None:
            place_at = editor.collision.collide_ray(ray)

        if place_at is None:
            #print("colliding with plane")
            plane = Plane.xy_aligned(Vector3(0.0, 0.0, 0.0))

            collision = ray.collide_plane(plane)
            if collision is not False:
                place_at, _ = collision


        if place_at is not None:
            #print("placed at", place_at)
            editor.create_waypoint_3d.emit(place_at.x, place_at.z, -place_at.y)
        #else:
        #    print("nothing collided, aw")


vec = numpy.array([1, 0, 0, 0])


class Gizmo3DMoveX(Gizmo2DMoveX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_name = "gizmo_x"
        self.axis = AXIS_X
        self.dir = numpy.array([1, 0, 0, 0])

    def do_delta(self, delta):
        return delta, 0, 0

    def move(self, editor, buttons, event):
        if editor.gizmo.was_hit[self.axis_name]:
            editor.gizmo.hidden = True
            editor.gizmo.set_render_axis(self.axis)

            proj = numpy.dot(editor.modelviewmatrix, self.dir)
            proj[2] = proj[3] = 0.0
            proj = proj/numpy.linalg.norm(proj)
            delta = numpy.array([event.position().x() - self.first_click.x, event.position().y() - self.first_click.y, 0, 0])
            delta[1] = -delta[1]
            self.first_click = Vector2(event.position().x(), event.position().y())
            delta_x = numpy.dot(delta, proj)

            if editor.shift_is_pressed:
                editor.move_points.emit(*self.do_delta(delta_x))

            else:
                fac = 1/3.0
                editor.move_points.emit(*self.do_delta(delta_x * editor.gizmo_scale * fac))
            self.moved = True


class Gizmo3DMoveY(Gizmo3DMoveX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_name = "gizmo_y"
        self.axis = AXIS_Y
        self.dir = numpy.array([0, 0, 1, 0])

    def do_delta(self, delta):
        return 0, delta, 0


class Gizmo3DMoveZ(Gizmo3DMoveX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_name = "gizmo_z"
        self.axis = AXIS_Z
        self.dir = numpy.array([0, 1, 0, 0])

    def do_delta(self, delta):
        return 0, 0, delta


class Gizmo3DRotateY(Gizmo2DRotateY):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.angle_start = None
        self.axis_name = "rotation_y"

    def do_delta(self, delta):
        return 0, delta, 0

    def flip_rot(self, dir):
        vec = numpy.array([0, 0, 1])
        dirvec = numpy.array([dir.x, dir.y, dir.z])

        d = numpy.dot(vec, dirvec)

        if d >= 0:
            return 1
        else:
            return -1

    def move(self, editor, buttons, event):
        if editor.gizmo.was_hit[self.axis_name]:
            editor.gizmo.hidden = True

            proj = numpy.dot(editor.mvp_mat, numpy.array([
                editor.gizmo.position.x,
                editor.gizmo.position.z,
                editor.gizmo.position.y,
                1]
            ))

            # Dehogomization
            if proj[3] != 0.0:
                proj[0] = proj[0] / proj[3]
                proj[1] = proj[1] / proj[3]
                proj[2] = proj[2] / proj[3]

            # Transform to editor coords
            w = editor.canvas_width/2.0
            h = editor.canvas_height/2.0
            point_x = proj[0] * w + w
            point_y = -proj[1] * h + h

            x, y = event.position().x() - point_x, event.position().y() - point_y
            angle = atan2(y, x)
            if self.angle_start is not None:
                delta = self.angle_start - angle
                delta *= self.flip_rot(editor.camera_direction)

                # Sometimes on the first click the delta is too high resulting in
                # a big rotation. We will limit it this way
                if abs(delta) <= 0.3:
                    editor.rotate_current.emit(Vector3(*self.do_delta(delta)))
            self.angle_start = angle
            self.moved = True


class Gizmo3DRotateX(Gizmo3DRotateY):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_name = "rotation_x"

    def flip_rot(self, dir):
        vec = numpy.array([1, 0, 0])
        dirvec = numpy.array([dir.x, dir.y, dir.z])

        d = numpy.dot(vec, dirvec)

        if d >= 0:
            return -1
        else:
            return 1

    def do_delta(self, delta):
        return delta, 0, 0


class Gizmo3DRotateZ(Gizmo3DRotateY):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axis_name = "rotation_z"

    def flip_rot(self, dir):
        vec = numpy.array([0, -1, 0])
        dirvec = numpy.array([dir.x, dir.y, dir.z])

        d = numpy.dot(vec, dirvec)

        if d >= 0:
            return -1
        else:
            return 1

    def do_delta(self, delta):
        return 0, 0, delta


class UserControl(object):
    def __init__(self, editor_widget):
        self._editor_widget = editor_widget

        self.shift_pressed = False

        self.buttons = Buttons()

        self.clickdragactions = {"Left": [], "Right": [], "Middle": []}
        self.clickdragactions3d = {"Left": [], "Right": [], "Middle": []}

        self.add_action(TopdownScroll("2DScroll", "Middle"))

        self.add_action(Gizmo2DMoveX("Gizmo2DMoveX", "Left"))
        self.add_action(Gizmo2DMoveZ("Gizmo2DMoveZ", "Left"))
        self.add_action(Gizmo2DMoveXZ("Gizmo2DMoveXZ", "Left"))
        self.add_action(Gizmo2DRotateY("Gizmo2DRotateY", "Left"))
        self.add_action(TopdownSelect("2DSelect", "Left"))
        self.add_action(AddObjectTopDown("AddObject2D", "Left"))
        self.add_action(PluginEventClickAction("PluginClick", "Left"))

        self.add_action3d(RotateCamera3D("RotateCamera", "Right"))
        self.add_action3d(AddObject3D("AddObject3D", "Left"))
        self.add_action3d(Gizmo3DMoveX("Gizmo3DMoveX", "Left"))
        self.add_action3d(Gizmo3DMoveY("Gizmo3DMoveY", "Left"))
        self.add_action3d(Gizmo3DMoveZ("Gizmo3DMoveZ", "Left"))
        self.add_action3d(Gizmo3DRotateX("Gizmo3DRotateX", "Left"))
        self.add_action3d(Gizmo3DRotateY("Gizmo3DRotateY", "Left"))
        self.add_action3d(Gizmo3DRotateZ("Gizmo3DRotateZ", "Left"))
        self.add_action3d(Select3D("Select3D", "Left"))
        self.add_action3d(PluginEvent3DTerrainClickAction("PluginClick3D", "Left"))

        self.last_position_update = 0.0

    def add_action(self, action):
        self.clickdragactions[action.key].append(action)

    def add_action3d(self, action):
        self.clickdragactions3d[action.key].append(action)

    def handle_press(self, event):
        editor = self._editor_widget

        if editor.mode == MODE_TOPDOWN:
            self.handle_press_topdown(event)
        else:
            self.handle_press_3d(event)

    def handle_release(self, event):
        editor = self._editor_widget
        if editor.mode == MODE_TOPDOWN:
            self.handle_release_topdown(event)
        else:
            self.handle_release_3d(event)

        editor.selectionqueue.clear()
        editor.gizmo.reset_hit_status()
        #print("Gizmo hit status was reset!!!!", editor.gizmo.was_hit_at_all)
        editor.do_redraw()

    def handle_move(self, event):
        editor = self._editor_widget
        if editor.mode == MODE_TOPDOWN:
            self.handle_move_topdown(event)

            if default_timer() - self.last_position_update > 0.1:  # True:  # self.highlighttriangle is not None:
                event_x, event_y = event.position().x(), event.position().y()
                mapx, mapz = editor.mouse_coord_to_world_coord(event_x, event_y)
                self.last_position_update = default_timer()

                if editor.bwterrain is not None:
                    #height = editor.collision.collide_ray_downwards(mapx, -mapz)
                    height = editor.bwterrain.check_height(mapx, mapz)

                    if height is not None:
                        # self.highlighttriangle = res[1:]
                        # self.update()
                        editor.position_update.emit(event, (round(mapx, 2), round(height, 2), round(mapz, 2)))
                    else:
                        editor.position_update.emit(event, (round(mapx, 2), None, round(mapz, 2)))
                else:
                    editor.position_update.emit(event, (round(mapx, 2), None, round(mapz, 2)))
        else:
            self.handle_move_3d(event)

    def handle_press_topdown(self, event):
        editor = self._editor_widget

        editor.selectionqueue.queue_selection(event.position().x(), event.position().y(), 1, 1,
                                              editor.shift_is_pressed, do_gizmo=True)
        editor.do_redraw(forceselected=True)

        for key in key_enums.keys():
            if self.buttons.just_pressed(event, key):
                for action in self.clickdragactions[key]:
                    if action.condition(editor, self.buttons, event):
                        action.just_clicked(editor, self.buttons, event)

    def handle_release_topdown(self, event):
        editor = self._editor_widget

        for key in key_enums.keys():
            if self.buttons.just_released(event, key):
                for action in self.clickdragactions[key]:
                    if action.condition(editor, self.buttons, event):
                        action.just_released(editor, self.buttons, event)

    def handle_move_topdown(self, event):
        editor = self._editor_widget

        for key in key_enums.keys():
            if self.buttons.is_held(event, key):
                for action in self.clickdragactions[key]:
                    if action.condition(editor, self.buttons, event):
                        action.move(editor, self.buttons, event)
        return

    def handle_press_3d(self, event):
        editor = self._editor_widget

        editor.selectionqueue.queue_selection(event.position().x(), event.position().y(), 1, 1,
                                              editor.shift_is_pressed, do_gizmo=True)
        editor.do_redraw(forceselected=True)

        for key in key_enums.keys():
            if self.buttons.just_pressed(event, key):
                for action in self.clickdragactions3d[key]:
                    if action.condition(editor, self.buttons, event):
                        action.just_clicked(editor, self.buttons, event)

    def handle_release_3d(self, event):
        editor = self._editor_widget

        for key in key_enums.keys():
            if self.buttons.just_released(event, key):
                for action in self.clickdragactions3d[key]:
                    if action.condition(editor, self.buttons, event):
                        action.just_released(editor, self.buttons, event)

    def handle_move_3d(self, event):
        editor = self._editor_widget

        for key in key_enums.keys():
            if self.buttons.is_held(event, key):
                for action in self.clickdragactions3d[key]:
                    if action.condition(editor, self.buttons, event):
                        action.move(editor, self.buttons, event)


