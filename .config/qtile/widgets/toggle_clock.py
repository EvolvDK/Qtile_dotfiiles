from libqtile import widget

class ToggleClock(widget.Clock):
    """
    Un widget d'horloge qui bascule entre le format court et long
    lors d'un clic gauche.
    """
    def __init__(self, **config):
        super().__init__(**config)
        self.short_format = self.format
        self.add_callbacks({'Button1': self.toggle_format})

    def toggle_format(self):
        """Bascule le format de l'horloge et redessine la barre."""
        if self.format == self.short_format:
            self.format = self.long_format
        else:
            self.format = self.short_format
        self.update(self.poll())
