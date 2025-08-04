import asyncio
from libqtile.widget import base
from libqtile.log_utils import logger

try:
    import pulsectl_asyncio
except ImportError:
    pulsectl_asyncio = None

class PulseVolumeCustom(base._TextBox):
    def __init__(self, max_volume=153, step=2,
                 foreground=None, background_unmuted=None, background_muted=None,
                 **config):
        super().__init__("Loading...", **config)
        
        # Configurable settings
        self.max_volume = max_volume
        self.step = step
        
        # Theme settings
        self.foreground = foreground
        self.background_unmuted = background_unmuted
        self.background_muted = background_muted
        self.padding = 5
        
        # Icons
        self.volume_icons = ["", "", ""]
        self.mute_icon = ""

        # Internal state
        self.volume = 0
        self.is_muted = True
        self.pulse = None
        self.listener_task = None
        self.previous_text_length = 0

        self.add_callbacks({
            "Button1": self.toggle_mute,
            "Button4": self.increase_volume,
            "Button5": self.decrease_volume,
        })

    async def _config_async(self):
        if pulsectl_asyncio is None:
            self.text = "pulsectl-asyncio missing"
            if hasattr(self, "bar"):
                self.bar.draw()
            return

        try:
            self.pulse = pulsectl_asyncio.PulseAsync('qtile-pulse-custom')
            await self.pulse.connect()
            await self._update_status()
            self.listener_task = asyncio.create_task(self._listen_for_events())
        except Exception:
            logger.exception("PulseVolumeCustom: Failed to connect to pulseaudio")
            self.text = "Connection Error"
            if hasattr(self, "bar"):
                self.bar.draw()

    async def _listen_for_events(self):
        async for _ in self.pulse.subscribe_events('sink', 'server'):
            if not self.pulse.connected:
                break
            await self._update_status()

    async def _update_status(self):
        try:
            server_info = await self.pulse.server_info()
            if not server_info.default_sink_name:
                self.is_muted, self.text = True, "No sink"
            else:
                sink = await self.pulse.get_sink_by_name(server_info.default_sink_name)
                self.volume = int(round(sink.volume.value_flat * 100))
                self.is_muted = sink.mute
                
                if self.is_muted:
                    self.text = f"{self.mute_icon} muet"
                else:
                    icon_index = 0
                    if self.volume > 0: icon_index = 1
                    if self.volume >= 50: icon_index = 2
                    self.text = f"{self.volume_icons[icon_index]} {self.volume}%"

        except Exception:
            logger.exception("PulseVolumeCustom: Failed to update status")
            self.is_muted, self.text = True, "Update Error"
        
        if hasattr(self, "bar"):
            new_length = len(self.text)
            if new_length != self.previous_text_length:
                self.previous_text_length = new_length
                self.bar.draw()
            else:
                self.draw()

    def draw(self):
        if self.is_muted:
            self.background = self.background_muted
        else:
            self.background = self.background_unmuted
        super().draw()

    def finalize(self):
        if self.listener_task:
            self.listener_task.cancel()
        if self.pulse and self.pulse.connected:
            self.pulse.disconnect()
        super().finalize()

    async def _async_toggle_mute(self):
        if not self.pulse or not self.pulse.connected:
            return
        server_info = await self.pulse.server_info()
        sink = await self.pulse.get_sink_by_name(server_info.default_sink_name)
        await self.pulse.mute(sink, not self.is_muted)

    async def _async_set_volume(self, new_volume_percent):
        if not self.pulse or not self.pulse.connected:
            return
        server_info = await self.pulse.server_info()
        sink = await self.pulse.get_sink_by_name(server_info.default_sink_name)
        await self.pulse.volume_set_all_chans(sink, new_volume_percent / 100.0)

    def toggle_mute(self):
        """Toggle mute status using pulsectl-asyncio."""
        asyncio.create_task(self._async_toggle_mute())

    def increase_volume(self):
        """Increase volume using pulsectl-asyncio, respecting max_volume."""
        new_volume = min(self.volume + self.step, self.max_volume)
        asyncio.create_task(self._async_set_volume(new_volume))

    def decrease_volume(self):
        """Decrease volume using pulsectl-asyncio."""
        new_volume = max(self.volume - self.step, 0)
        asyncio.create_task(self._async_set_volume(new_volume))
