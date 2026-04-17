/**
 * WMO weather codes → český popis + emoji ikona.
 * Podle https://open-meteo.com/en/docs#weathervariables
 */
export function weatherDescription(code: number, isDay: boolean): { label: string; icon: string } {
  const map: Record<number, { day: string; night: string; label: string }> = {
    0: { day: "☀️", night: "🌙", label: "Jasno" },
    1: { day: "🌤️", night: "🌙", label: "Převážně jasno" },
    2: { day: "⛅", night: "☁️", label: "Polojasno" },
    3: { day: "☁️", night: "☁️", label: "Zataženo" },
    45: { day: "🌫️", night: "🌫️", label: "Mlha" },
    48: { day: "🌫️", night: "🌫️", label: "Namrzající mlha" },
    51: { day: "🌦️", night: "🌦️", label: "Slabé mrholení" },
    53: { day: "🌦️", night: "🌦️", label: "Mrholení" },
    55: { day: "🌧️", night: "🌧️", label: "Silné mrholení" },
    61: { day: "🌦️", night: "🌦️", label: "Slabý déšť" },
    63: { day: "🌧️", night: "🌧️", label: "Déšť" },
    65: { day: "🌧️", night: "🌧️", label: "Silný déšť" },
    71: { day: "🌨️", night: "🌨️", label: "Slabé sněžení" },
    73: { day: "🌨️", night: "🌨️", label: "Sněžení" },
    75: { day: "❄️", night: "❄️", label: "Silné sněžení" },
    77: { day: "🌨️", night: "🌨️", label: "Sněhové zrní" },
    80: { day: "🌦️", night: "🌦️", label: "Slabé přeháňky" },
    81: { day: "🌧️", night: "🌧️", label: "Přeháňky" },
    82: { day: "⛈️", night: "⛈️", label: "Silné přeháňky" },
    85: { day: "🌨️", night: "🌨️", label: "Sněhové přeháňky" },
    95: { day: "⛈️", night: "⛈️", label: "Bouřka" },
    96: { day: "⛈️", night: "⛈️", label: "Bouřka s kroupami" },
    99: { day: "⛈️", night: "⛈️", label: "Silná bouřka s kroupami" },
  };
  const entry = map[code] || { day: "❓", night: "❓", label: "Neznámé" };
  return { icon: isDay ? entry.day : entry.night, label: entry.label };
}
