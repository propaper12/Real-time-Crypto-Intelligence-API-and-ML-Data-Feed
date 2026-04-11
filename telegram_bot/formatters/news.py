from datetime import datetime


def format_news_flash(news_list: list) -> str:
    """Formats a list of crypto news items into a Telegram broadcast."""
    if not news_list:
        return "📰 <b>Haber verisi bulunamadı.</b>"

    ts = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [
        "📰 <b>RADARPRO FLAŞ HABERLER</b>",
        "━━━━━━━━━━━━━━━━━━━━━",
    ]

    icons = ["🔵", "🟣", "🟠", "🟡", "🔴"]
    for i, item in enumerate(news_list[:5]):
        icon  = icons[i % len(icons)]
        title = item.get("title", "Haber")
        date  = item.get("date", "")
        link  = item.get("link", "")
        lines.append(f"{icon} <a href='{link}'>{title}</a>")
        if date:
            lines.append(f"   <i>🕐 {date[:22]}</i>")

    lines += [
        "━━━━━━━━━━━━━━━━━━━━━",
        f"⏰ <code>{ts}</code> | 📡 <i>@RadarPro_Intelligence_Bot</i>",
    ]
    return "\n".join(lines)
