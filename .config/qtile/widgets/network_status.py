import time
from libqtile.widget import base
from libqtile.lazy import lazy

class NetworkStatus(base.InLoopPollText):
    """
    Un widget réseau qui affiche la vitesse totale, change d'icône et de couleur
    en fonction de l'état de la connexion.
    """
    def __init__(self, interface, home, interface_type='wired',
                 foreground=None, background_connected=None, background_disconnected=None,
                 **config):
        super().__init__("", **config)
        self.interface = interface
        self.update_interval = 3

        self.icons = {
            'wireless': {'connected': '󰖩', 'disconnected': '󰖪'},
            'wired':    {'connected': '󰈀', 'disconnected': '󰈂'}
        }[interface_type]

        self.background_connected = background_connected
        self.background_disconnected = background_disconnected

        # Variables pour le calcul de la vitesse
        self.last_update_time = 0
        self.last_total_bytes = 0

        # Réglages esthétiques
        self.padding = 5
        self.foreground = foreground

        self.add_callbacks({
            'Button1': lazy.spawn(f'{home}/.config/rofi/scripts/rofi-network-manager')
        })

    def _get_total_bytes(self):
        try:
            with open(f'/sys/class/net/{self.interface}/statistics/rx_bytes', 'r') as f:
                rx = int(f.read())
            with open(f'/sys/class/net/{self.interface}/statistics/tx_bytes', 'r') as f:
                tx = int(f.read())
            return rx + tx
        except FileNotFoundError:
            return 0

    def _format_speed(self, speed_bytes_per_sec):
        if speed_bytes_per_sec >= 1_000_000_000:
            return f"{speed_bytes_per_sec / 1_000_000_000:.2f} GB/s"
        if speed_bytes_per_sec >= 1_000_000:
            return f"{speed_bytes_per_sec / 1_000_000:.2f} MB/s"
        if speed_bytes_per_sec >= 1_000:
            return f"{speed_bytes_per_sec / 1_000:.1f} KB/s"
        return f"{speed_bytes_per_sec:.0f} B/s"

    def poll(self):
        try:
            with open(f'/sys/class/net/{self.interface}/operstate', 'r') as f:
                status = f.read().strip()
        except FileNotFoundError:
            status = 'down'

        if status == 'up':
            self.background = self.background_connected
            icon = self.icons['connected']
            
            current_time = time.time()
            current_bytes = self._get_total_bytes()
            
            if self.last_update_time == 0: # Premier passage ou reconnexion
                speed_str = self._format_speed(0)
            else:
                time_delta = current_time - self.last_update_time
                byte_delta = current_bytes - self.last_total_bytes
                speed = byte_delta / time_delta if time_delta > 0 else 0
                speed_str = self._format_speed(speed)
            
            self.last_total_bytes = current_bytes
            self.last_update_time = current_time
            
            return f"{icon} {speed_str}"
        else:
            self.background = self.background_disconnected
            self.last_update_time = 0  # Réinitialiser pour la prochaine connexion
            return f"{self.icons['disconnected']} Offline"
