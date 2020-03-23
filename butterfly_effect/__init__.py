import ppb


class Splash(ppb.BaseScene):
    background_color = 112, 31, 153

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count_down = 4

    def on_update(self, update_event: ppb.events.Update, signal):
        self.count_down -= update_event.time_delta
        if self.count_down <= 0:
            signal(ppb.events.ReplaceScene(Title()))


class Title(ppb.BaseScene):
    background_color = 31, 175, 204

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(
            ppb.Sprite(
                image=ppb.Image("butterfly_effect/resources/title.png"),
                size=2.5
            )
        )


scene_map = {
    "title": Title,
}
