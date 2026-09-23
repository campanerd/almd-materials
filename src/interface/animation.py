"""Animation helpers tuned to what Windows 11 actually delivers.

Measured on this machine: after(8) yields a steady 15.5ms cadence (~64fps, 1ms jitter),
while the seemingly obvious after(16) straddles the Windows tick and alternates
16/31ms, which reads as judder. Progress is driven from the wall clock rather than
from a frame count so that jitter changes smoothness but never duration.

Two hard rules, both from measurement:
  - animate POSITION with place() only. Animating grid/pack geometry or height on a
    list reflows the whole container every frame (12 rows measured at 10fps).
  - animate COLOR with configure() on at most ~6 frames per frame; fading a whole
    40-row list at once measured 15.7fps, the same list staggered measured 61.6fps.
"""

import time

import customtkinter

FRAME_INTERVAL_MS = 8


def interpolate_color(start_color: str, end_color: str, progress: float) -> str:
    start = start_color.lstrip("#")
    end = end_color.lstrip("#")
    channels = (
        round(int(start[i:i + 2], 16) + (int(end[i:i + 2], 16) - int(start[i:i + 2], 16)) * progress)
        for i in (0, 2, 4)
    )
    return "#%02x%02x%02x" % tuple(max(0, min(255, channel)) for channel in channels)


def ease_out_cubic(progress: float) -> float:
    return 1 - (1 - progress) ** 3


def animate(widget, duration_ms: int, apply_progress, on_finished=None) -> None:
    """Run apply_progress(eased 0..1) until duration_ms elapses.

    Any tween already running on this widget is cancelled first, so a row whose
    hover flips mid-fade never has two loops fighting over the same color.
    """
    running_animation_id = getattr(widget, "_running_animation_id", None)
    if running_animation_id is not None:
        widget.after_cancel(running_animation_id)
        widget._running_animation_id = None

    start_time = time.perf_counter()

    def tick() -> None:
        if not widget.winfo_exists():
            return
        raw_progress = min(1.0, (time.perf_counter() - start_time) * 1000 / duration_ms)
        apply_progress(ease_out_cubic(raw_progress))
        if raw_progress < 1.0:
            widget._running_animation_id = widget.after(FRAME_INTERVAL_MS, tick)
        else:
            widget._running_animation_id = None
            if on_finished is not None:
                on_finished()

    tick()


def bind_including_children(widget, sequence: str, command) -> None:
    """Bind an event on a composite widget and every CustomTkinter child inside it.

    A bare widget.bind() on a row only covers the row's own canvas: a click or a
    pointer crossing that lands on a child label never reaches it. The isinstance
    guard matters -- CTkLabel.winfo_children() exposes the very tk widgets that
    CTkLabel.bind() already covers, so recursing past it fires the handler twice.
    """
    widget.bind(sequence, command, add=True)
    for child in widget.winfo_children():
        if isinstance(child, customtkinter.CTkBaseClass):
            bind_including_children(child, sequence, command)


def pointer_is_inside(widget) -> bool:
    pointer_x, pointer_y = widget.winfo_pointerxy()
    left, top = widget.winfo_rootx(), widget.winfo_rooty()
    return (
        left <= pointer_x < left + widget.winfo_width()
        and top <= pointer_y < top + widget.winfo_height()
    )


def resolve_color(color_pair: tuple[str, str]) -> str:
    return color_pair[1] if customtkinter.get_appearance_mode() == "Dark" else color_pair[0]
