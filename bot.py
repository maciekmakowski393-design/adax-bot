import discord
from discord.ext import commands
import random
import asyncio
import json
import os
import re
from datetime import datetime, timedelta

# ================== TOKEN ZE ZMIENNYCH ŚRODOWISKOWYCH ==================
TOKEN = os.getenv("TOKEN")

# ================== PROSTY SERWER HTTP (BEZ BŁĘDÓW) ==================
# Ten serwer działa w tle i otwiera port, aby Render był zadowolony.
# Używamy asyncio i aiohttp w bezpieczny sposób.
import asyncio
from aiohttp import web
import threading

async def handle(request):
    return web.Response(text="Bot is running!")

def run_http_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = web.Application()
    app.router.add_get('/', handle)
    web.run_app(app, host='0.0.0.0', port=10000)

# Uruchamiamy serwer w osobnym wątku
thread = threading.Thread(target=run_http_server, daemon=True)
thread.start()

# ================== INTENCJE I BOT ==================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# LISTA SERWERÓW (dodaj tutaj ID swoich serwerów)
SERWERY = [
    discord.Object(id=1479710460877078538),
    discord.Object(id=1478454030538637363)
]

# Pliki danych
GIVEAWAY_FILE = "giveaways.json"
TICKETS_FILE = "tickets.json"
CUSTOM_STATUS_FILE = "custom_status.json"
WELCOME_CONFIG_FILE = "welcome_config.json"
GOODBYE_CONFIG_FILE = "goodbye_config.json"

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

active_giveaways = load_json(GIVEAWAY_FILE, {"next_id": 1, "giveaways": {}})
tickets_data = load_json(TICKETS_FILE, {})
custom_status = load_json(CUSTOM_STATUS_FILE, {})
welcome_config = load_json(WELCOME_CONFIG_FILE, {})
goodbye_config = load_json(GOODBYE_CONFIG_FILE, {})

invite_cache = {}

def save_giveaways():
    with open(GIVEAWAY_FILE, "w", encoding="utf-8") as f:
        json.dump(active_giveaways, f, indent=4, ensure_ascii=False)

def save_tickets():
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets_data, f, indent=4, ensure_ascii=False)

def save_custom_status():
    with open(CUSTOM_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_status, f, indent=4, ensure_ascii=False)

def save_welcome_config():
    with open(WELCOME_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(welcome_config, f, indent=4, ensure_ascii=False)

def save_goodbye_config():
    with open(GOODBYE_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(goodbye_config, f, indent=4, ensure_ascii=False)

# ================== EVENTY ==================
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} jest online!')
    try:
        for guild in bot.guilds:
            try:
                invites = await guild.invites()
                invite_cache[guild.id] = invites
                print(f'📦 Zbuforowano {len(invites)} zaproszeń dla: {guild.name}')
            except Exception as e:
                print(f'⚠️ Nie można pobrać zaproszeń dla {guild.name}: {e}')
        
        for guild in SERWERY:
            try:
                bot.tree.copy_global_to(guild=guild)
                synced = await bot.tree.sync(guild=guild)
                print(f'🔄 Synchro {len(synced)} komend dla serwera {guild.id}')
            except Exception as e:
                print(f'❌ Błąd synchro dla {guild.id}: {e}')
        
        for g_id, data in list(active_giveaways["giveaways"].items()):
            if data.get("active", False) and data['end_time'] > datetime.now().timestamp():
                asyncio.create_task(check_giveaway_end(g_id, data))
            elif data.get("active", False):
                await end_giveaway_by_id(g_id)
    except Exception as e:
        print(f'❌ Błąd synchronizacji: {e}')

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    channel_id = welcome_config.get(guild_id)
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel:
            count = member.guild.member_count
            await channel.send(f"{member.mention} jesteś **{count}** osobą na naszym serwerze! 🎉")

@bot.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)
    channel_id = goodbye_config.get(guild_id)
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel:
            embed = discord.Embed(
                description=f"{member.mention} opuścił nas... Mam nadzieję, że wrócisz do nas! 💔",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Żegnamy")
            await channel.send(embed=embed)

# ================== AUTOMATYCZNE ODPOWIEDZI ==================
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    content_lower = message.content.lower()
    response = None
    
    if "dupa" in content_lower:
        response = f"{message.author.mention} 🥒 w dupe to ci wsadzali ogórek 🥒"
    elif "adax" in content_lower:
        response = f"{message.author.mention} 👿 Zostaw adaxa on ci mame robi 👿"
    elif "doner" in content_lower:
        response = f"{message.author.mention} 🥙 Donerkebab to legitny mm i sprzedawca zachęcamy do mm z nim 🥙"
    elif "ania" in content_lower:
        response = f"{message.author.mention} 👧 Robiliśmy ją w dzieśięciu tak to o tobie ania nigy nie wiśiłem asz takiego jebania."
    elif "luki" in content_lower:
        response = f"{message.author.mention} 🎮 Luki nawet nie oddychał na live a dostał kurwa bana Pov luki : KUWRA JAPIERDOLE HITLE EE AUSTRIACKI 🎮"
    elif "co" in content_lower:
        response = f"{message.author.mention} 💩 gówno 💩"
    elif "essa" in content_lower:
        response = f"{message.author.mention} essa essa to bylo z twoja mama"
    elif "bambik" in content_lower:
        response = f"{message.author.mention} Bambik to ty nie masz fortnita nawet i niech doda 💀"
    elif "spierdalaj" in content_lower:
        response = f"{message.author.mention} spierdalala to twoja matka bo tym dymaniu"
    elif "elo" in content_lower:
        response = f"{message.author.mention} elo elo 3 2 0"
    elif "pachołek" in content_lower or "pacholek" in content_lower:
        response = f"{message.author.mention} Pachołek to spoko gość"
    elif "panto" in content_lower:
        response = f"{message.author.mention} Panto to legitny owner ale dostal bana na glownym i nie cierpi swoich ownerow"
    elif "szczeka" in content_lower or "szczekał" in content_lower or "szczekała" in content_lower:
        response = f"{message.author.mention} Szczekała to twoja cała rodzina po tą kiełbase"
    
    if response:
        await message.channel.send(response)
    
    await bot.process_commands(message)

# ================== TICKETY ==================
KATEGORIA_TICKETOW_ID = None

@bot.tree.command(name="ticket", description="🎟️ Tworzy panel ticketów z przyciskami")
async def ticket(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎟️ **PANEL TICKETÓW** 🎟️",
        description="Kliknij w odpowiedni przycisk, aby otworzyć ticket.\n"
                    "🆘 • **Pomoc** – wsparcie techniczne\n"
                    "🤝 • **Współpraca** – oferty współpracy\n"
                    "💼 • **Middleman** – potrzebujesz pośrednika\n"
                    "🛒 • **Zakup** – pytania o zakup",
        color=discord.Color.blue()
    )

    view = discord.ui.View(timeout=None)

    async def ticket_button_callback(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        ticket_type = interaction.data["custom_id"].replace("ticket_", "")
        nazwa_kanalu = f"ticket-{ticket_type}-{interaction.user.name}".lower().replace(" ", "-")

        guild = interaction.guild
        if KATEGORIA_TICKETOW_ID is None:
            kat = discord.utils.get(guild.categories, name="Tickety")
            if kat is None:
                kat = await guild.create_category("Tickety")
            kategoria = kat
        else:
            kategoria = guild.get_channel(KATEGORIA_TICKETOW_ID)
            if kategoria is None:
                kat = await guild.create_category("Tickety")
                kategoria = kat

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        admin_role = discord.utils.get(guild.roles, name="Admin")
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(nazwa_kanalu, category=kategoria, overwrites=overwrites)

        tickets_data[str(channel.id)] = {
            "user_id": str(interaction.user.id),
            "type": ticket_type,
            "created_at": datetime.now().isoformat()
        }
        save_tickets()

        embed_ticket = discord.Embed(
            title=f"🎫 Ticket: {ticket_type}",
            description=f"Witaj {interaction.user.mention}!\nOpisz swój problem lub zapytanie. Personel wkrótce się odezwie.\n\nAby zamknąć ticket, kliknij przycisk poniżej.",
            color=discord.Color.green()
        )
        close_btn = discord.ui.Button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.danger, custom_id=f"close_{channel.id}")

        async def close_callback(interaction: discord.Interaction):
            if interaction.user.id != int(tickets_data[str(channel.id)]["user_id"]) and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Nie masz uprawnień do zamknięcia tego ticketu!", ephemeral=True)
                return
            await interaction.response.send_message("🔒 Zamykanie ticketu za 5 sekund...")
            await asyncio.sleep(5)
            await channel.delete()
            if str(channel.id) in tickets_data:
                del tickets_data[str(channel.id)]
                save_tickets()

        close_btn.callback = close_callback
        view_ticket = discord.ui.View()
        view_ticket.add_item(close_btn)

        await channel.send(embed=embed_ticket, view=view_ticket)
        await interaction.followup.send(f"✅ Utworzono ticket: {channel.mention}", ephemeral=True)

    for label, style, custom_id in [
        ("🆘 Pomoc", discord.ButtonStyle.primary, "ticket_pomoc"),
        ("🤝 Współpraca", discord.ButtonStyle.success, "ticket_wspolpraca"),
        ("💼 Middleman", discord.ButtonStyle.secondary, "ticket_middleman"),
        ("🛒 Zakup", discord.ButtonStyle.danger, "ticket_zakup")
    ]:
        btn = discord.ui.Button(label=label, style=style, custom_id=custom_id)
        btn.callback = ticket_button_callback
        view.add_item(btn)

    await interaction.response.send_message(embed=embed, view=view)

# ================== GIVEAWAY ==================
def parse_czas(czas_str):
    czas_str = czas_str.lower().strip()
    if czas_str.endswith('m'):
        try: return int(czas_str[:-1]) * 60
        except: return None
    elif czas_str.endswith('h'):
        try: return int(czas_str[:-1]) * 3600
        except: return None
    elif czas_str.endswith('d'):
        try: return int(czas_str[:-1]) * 86400
        except: return None
    else: return None

@bot.tree.command(name="gcreate", description="🎁 Tworzy nowy giveaway")
async def gcreate(interaction: discord.Interaction, nagroda: str, czas: str, zwyciezcy: int = 1):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może tworzyć giveaway!", ephemeral=True)
        return
    czas_sek = parse_czas(czas)
    if czas_sek is None:
        await interaction.response.send_message("❌ Niepoprawny format czasu! Użyj: 10m, 1h, 2d", ephemeral=True)
        return
    giveaway_id = str(active_giveaways["next_id"])
    active_giveaways["next_id"] += 1
    end_time = datetime.now() + timedelta(seconds=czas_sek)
    embed = discord.Embed(
        title="🎁 **GIVEAWAY** 🎁",
        description=f"🆔 **ID:** {giveaway_id}\n🎁 **Nagroda:** {nagroda}\n👥 **Zwycięzców:** {zwyciezcy}\n⏱️ **Czas:** {czas}\n👤 **Uczestników:** 0\n\n⬇️ **Kliknij przycisk poniżej, żeby wziąć udział!**",
        color=discord.Color.gold(),
        timestamp=end_time
    )
    embed.set_footer(text=f"Utworzone przez {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    button = discord.ui.Button(label="🎉 Weź udział", style=discord.ButtonStyle.primary, custom_id=f"join_{giveaway_id}")

    async def button_callback(interaction: discord.Interaction):
        g_id = interaction.data["custom_id"].split("_")[1]
        if g_id not in active_giveaways["giveaways"]:
            await interaction.response.send_message("❌ Ten giveaway już nie istnieje!", ephemeral=True)
            return
        data = active_giveaways["giveaways"][g_id]
        if not data.get("active", False):
            await interaction.response.send_message("❌ Ten giveaway już się zakończył!", ephemeral=True)
            return
        if str(interaction.user.id) not in data['participants']:
            data['participants'].append(str(interaction.user.id))
            save_giveaways()
            await interaction.response.send_message("✅ Dołączyłeś do giveaway!", ephemeral=True)
            await update_giveaway_message(interaction.message, g_id)
        else:
            await interaction.response.send_message("❌ Już jesteś w tym giveaway!", ephemeral=True)

    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)
    msg = await interaction.original_response()
    active_giveaways["giveaways"][giveaway_id] = {
        'channel_id': str(msg.channel.id),
        'message_id': str(msg.id),
        'host_id': str(interaction.user.id),
        'prize': nagroda,
        'winners_count': zwyciezcy,
        'end_time': end_time.timestamp(),
        'participants': [],
        'active': True,
        'winners': []
    }
    save_giveaways()
    asyncio.create_task(check_giveaway_end(giveaway_id, active_giveaways["giveaways"][giveaway_id]))

async def update_giveaway_message(message, giveaway_id):
    if giveaway_id not in active_giveaways["giveaways"]:
        return
    data = active_giveaways["giveaways"][giveaway_id]
    embed = message.embeds[0]
    lines = embed.description.split('\n')
    new_desc = f"{lines[0]}\n{lines[1]}\n{lines[2]}\n{lines[3]}\n👤 **Uczestników:** {len(data['participants'])}\n\n⬇️ **Kliknij przycisk poniżej, żeby wziąć udział!**"
    embed.description = new_desc
    await message.edit(embed=embed)

async def check_giveaway_end(giveaway_id, data):
    end_time = datetime.fromtimestamp(data['end_time'])
    now = datetime.now()
    if end_time > now:
        await asyncio.sleep((end_time - now).total_seconds())
    await end_giveaway_by_id(giveaway_id)

async def end_giveaway_by_id(giveaway_id):
    if giveaway_id not in active_giveaways["giveaways"]:
        return
    data = active_giveaways["giveaways"][giveaway_id]
    if not data.get("active", False):
        return
    data['active'] = False
    participants = data['participants']
    winners_count = min(data['winners_count'], len(participants))
    channel = bot.get_channel(int(data['channel_id']))
    if not channel:
        save_giveaways()
        return
    try:
        message = await channel.fetch_message(int(data['message_id']))
    except:
        message = None
    if winners_count == 0:
        embed = discord.Embed(
            title="🎁 **GIVEAWAY ZAKOŃCZONY**",
            description=f"🆔 **ID:** {giveaway_id}\n🎁 **Nagroda:** {data['prize']}\n👤 **Uczestników:** {len(participants)}\n\n😢 Nikt nie wziął udziału!",
            color=discord.Color.red()
        )
    else:
        winners = random.sample(participants, winners_count)
        data['winners'] = winners
        winners_mentions = [f"<@{w}>" for w in winners]
        embed = discord.Embed(
            title="🎁 **GIVEAWAY ZAKOŃCZONY**",
            description=f"🆔 **ID:** {giveaway_id}\n🎁 **Nagroda:** {data['prize']}\n👤 **Uczestników:** {len(participants)}\n\n🏆 **Zwycięzcy:** {', '.join(winners_mentions)}\n\nGratulacje! 🥳",
            color=discord.Color.green()
        )
        await channel.send(f"🎉 Gratulacje dla {', '.join(winners_mentions)} w giveawayu **{data['prize']}** (ID: {giveaway_id})!")
    if message:
        await message.edit(embed=embed, view=None)
    save_giveaways()

@bot.tree.command(name="reroll", description="🔄 Losuje nowego zwycięzcę dla zakończonego giveaway")
async def reroll(interaction: discord.Interaction, id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    if id not in active_giveaways["giveaways"]:
        await interaction.response.send_message("❌ Nie znaleziono giveaway o podanym ID!", ephemeral=True)
        return
    data = active_giveaways["giveaways"][id]
    if data.get("active", False):
        await interaction.response.send_message("❌ Ten giveaway jeszcze trwa!", ephemeral=True)
        return
    participants = data['participants']
    if not participants:
        await interaction.response.send_message("❌ Nikt nie brał udziału!", ephemeral=True)
        return
    old_winners = data.get('winners', [])
    available = [p for p in participants if p not in old_winners]
    if not available:
        await interaction.response.send_message("❌ Wszyscy już wygrali!", ephemeral=True)
        return
    new = random.choice(available)
    data['winners'].append(new)
    save_giveaways()
    channel = bot.get_channel(int(data['channel_id']))
    if channel:
        await channel.send(f"🔄 **Nowy zwycięzca** w giveawayu **{data['prize']}** (ID: {id}): <@{new}>!")
    await interaction.response.send_message(f"✅ Nowy zwycięzca: <@{new}>", ephemeral=True)

# ================== KOMENDY ADMINISTRACYJNE ==================
@bot.tree.command(name="clear", description="🧹 Usuwa określoną liczbę wiadomości")
async def clear(interaction: discord.Interaction, liczba: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    if liczba < 1 or liczba > 100:
        await interaction.response.send_message("❌ Podaj liczbę od 1 do 100!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.channel.purge(limit=liczba + 1)
        await interaction.followup.send(f"✅ Usunięto **{liczba}** wiadomości! 🧹", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ Bot nie ma uprawnień do usuwania wiadomości na tym kanale!", ephemeral=True)

@bot.tree.command(name="ban", description="🔨 Banuje użytkownika")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Nie podano powodu"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Nie masz uprawnień!", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Bot nie ma uprawnień!", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Użytkownik {member.mention} został zbanowany. Powód: {reason}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

@bot.tree.command(name="kick", description="👢 Wyrzuca jednego lub więcej użytkowników (podaj wzmianki)")
async def kick(interaction: discord.Interaction, users: str, reason: str = "Nie podano powodu"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ Nie masz uprawnień!", ephemeral=True)
    if not interaction.guild.me.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ Bot nie ma uprawnień!", ephemeral=True)
    mentions = re.findall(r'<@!?(\d+)>', users)
    if not mentions:
        return await interaction.response.send_message("❌ Podaj poprawnych użytkowników (wzmianki).", ephemeral=True)
    kicked = []
    failed = []
    for user_id in mentions:
        member = interaction.guild.get_member(int(user_id))
        if member:
            try:
                await member.kick(reason=reason)
                kicked.append(member.mention)
            except Exception as e:
                failed.append(f"{member.mention} ({e})")
        else:
            failed.append(f"<@{user_id}> (nie na serwerze)")
    await interaction.response.send_message(
        f"✅ Wyrzucono: {', '.join(kicked) if kicked else 'brak'}\n❌ Nie udało się: {', '.join(failed) if failed else 'brak'}",
        ephemeral=True
    )

# ================== KOMENDY ZAPROSZEŃ ==================
@bot.tree.command(name="invites", description="📊 Pokazuje liczbę zaproszeń (swoich lub innego użytkownika)")
async def invites(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    guild = interaction.guild
    await interaction.response.defer(ephemeral=False)
    try:
        invites = await guild.invites()
        user_invites = [inv for inv in invites if inv.inviter and inv.inviter.id == member.id]
        total_uses = sum(inv.uses for inv in user_invites)
        active_links = len(user_invites)
        embed = discord.Embed(
            title=f"📊 **Zaproszenia – {member.display_name}**",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📈 Łącznie", value=f"**{total_uses}**", inline=True)
        embed.add_field(name="🎟️ Aktywnych linków", value=f"**{active_links}**", inline=True)
        embed.set_footer(text=f"Wywołane przez {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

@bot.tree.command(name="topinvites", description="🏆 Pokazuje ranking top 10 zapraszających")
async def topinvites(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer(ephemeral=False)
    try:
        invites = await guild.invites()
        inviter_stats = {}
        for inv in invites:
            if inv.inviter and not inv.inviter.bot:
                if inv.inviter.id not in inviter_stats:
                    inviter_stats[inv.inviter.id] = {
                        'member': inv.inviter,
                        'total_uses': 0,
                        'invites_count': 0
                    }
                inviter_stats[inv.inviter.id]['total_uses'] += inv.uses
                inviter_stats[inv.inviter.id]['invites_count'] += 1
        if not inviter_stats:
            embed = discord.Embed(title="🏆 Top 10 zapraszających", description="Brak danych o zaproszeniach.", color=discord.Color.orange())
            await interaction.followup.send(embed=embed)
            return
        sorted_inviters = sorted(inviter_stats.values(), key=lambda x: x['total_uses'], reverse=True)[:10]
        medals = ["🥇", "🥈", "🥉"]
        embed = discord.Embed(
            title="🏆 **TOP 10 ZAPRASZAJĄCYCH**",
            description=f"Na serwerze **{guild.name}**",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        ranking_text = ""
        for idx, data in enumerate(sorted_inviters, start=1):
            member = data['member']
            medal = medals[idx-1] if idx <= 3 else f"**{idx}.**"
            ranking_text += f"{medal} {member.mention} – **{data['total_uses']}** zaproszeń (📎 {data['invites_count']} linków)\n"
        embed.add_field(name="📋 Ranking", value=ranking_text, inline=False)
        total_server_invites = sum(inv.uses for inv in invites if inv.inviter and not inv.inviter.bot)
        embed.set_footer(text=f"📊 Łącznie na serwerze: {total_server_invites} zaproszeń")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

# ================== ZARZĄDZANIE ZAPROSZENIAMI ==================
@bot.tree.command(name="usunzaproszenia", description="🗑️ Usuwa wszystkie zaproszenia utworzone przez wybranego użytkownika")
async def usunzaproszenia(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)
    try:
        invites = await guild.invites()
        user_invites = [inv for inv in invites if inv.inviter and inv.inviter.id == member.id]
        if not user_invites:
            await interaction.followup.send(f"❌ Użytkownik {member.mention} nie ma żadnych aktywnych zaproszeń.", ephemeral=True)
            return
        deleted_count = 0
        for inv in user_invites:
            try:
                await inv.delete()
                deleted_count += 1
            except:
                pass
        await interaction.followup.send(f"🗑️ Usunięto **{deleted_count}** zaproszeń utworzonych przez {member.mention}.", ephemeral=True)
        invites_after = await guild.invites()
        invite_cache[guild.id] = invites_after
    except Exception as e:
        await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

@bot.tree.command(name="usunwszystkiezaproszenia", description="⚠️ Usuwa WSZYSTKIE zaproszenia na serwerze (wymaga potwierdzenia)")
async def usunwszystkiezaproszenia(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return

    class Potwierdzenie(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)

        @discord.ui.button(label="✅ Potwierdzam", style=discord.ButtonStyle.danger)
        async def potwierdz(self, interaction: discord.Interaction, button: discord.ui.Button):
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            guild = interaction.guild
            try:
                invites = await guild.invites()
                if not invites:
                    await interaction.followup.send("❌ Na serwerze nie ma żadnych zaproszeń.", ephemeral=True)
                    return
                deleted_count = 0
                for inv in invites:
                    try:
                        await inv.delete()
                        deleted_count += 1
                    except:
                        pass
                await interaction.followup.send(f"🗑️ Usunięto **{deleted_count}** zaproszeń z serwera.", ephemeral=True)
                invite_cache[guild.id] = []
            except Exception as e:
                await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

        @discord.ui.button(label="❌ Anuluj", style=discord.ButtonStyle.secondary)
        async def anuluj(self, interaction: discord.Interaction, button: discord.ui.Button):
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("❌ Anulowano usuwanie zaproszeń.", ephemeral=True)

    embed = discord.Embed(
        title="⚠️ **POTWIERDZENIE**",
        description="Czy na pewno chcesz usunąć **WSZYSTKIE** zaproszenia na tym serwerze? Tej operacji nie można cofnąć.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=Potwierdzenie(), ephemeral=True)

# ================== KOMENDA FAKEMESSAGE ==================
@bot.tree.command(name="fakemessage", description="📝 Wysyła wiadomość imitującą innego użytkownika (bez webhooków)")
async def fakemessage(interaction: discord.Interaction, member: discord.Member, treść: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    
    embed = discord.Embed(
        description=treść,
        color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_footer(text=f"Wywołane przez {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# ================== KOMENDA /typein ==================
@bot.tree.command(name="typein", description="📨 Bot wysyła wiadomość na wybranym kanale (dla administratorów)")
async def typein(interaction: discord.Interaction, kanał: discord.TextChannel, wiadomość: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    try:
        await kanał.send(wiadomość)
        await interaction.response.send_message(f"✅ Wiadomość wysłana na {kanał.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Bot nie ma uprawnień do wysyłania wiadomości na tym kanale!", ephemeral=True)

# ================== KOMENDA /changekanal ==================
@bot.tree.command(name="changekanal", description="🔄 Zmienia nazwy wszystkich kanałów tekstowych (dla administratorów)")
async def changekanal(interaction: discord.Interaction, nowa_nazwa: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    kanały = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
    if not kanały:
        await interaction.followup.send("❌ Brak kanałów tekstowych.", ephemeral=True)
        return
    sukces = 0
    błedy = 0
    for i, kanał in enumerate(kanały, start=1):
        try:
            nazwa = f"{nowa_nazwa}-{i}"
            await kanał.edit(name=nazwa)
            sukces += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            błedy += 1
            print(f"Błąd przy zmianie nazwy kanału {kanał.name}: {e}")
    await interaction.followup.send(f"✅ Zmieniono nazwy {sukces} kanałów. Błędów: {błedy}.", ephemeral=True)

# ================== KOMENDA /announce ==================
@bot.tree.command(name="announce", description="📢 Ogłoszenie na wszystkie kanały (max 100 powt.)")
async def announce_all(
    interaction: discord.Interaction,
    wiadomość: str,
    ile_razy: int = 1,
    zmiana_nazwy: str = None
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    if ile_razy < 1 or ile_razy > 100:
        await interaction.response.send_message("❌ Liczba powtórzeń musi być między 1 a 100!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    # ---- Część 1: wysyłanie ogłoszenia ----
    kanały_tekstowe = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
    if kanały_tekstowe:
        kanały_tekstowe = kanały_tekstowe[:100]
        sukces = 0
        błędy = 0
        for _ in range(ile_razy):
            for channel in kanały_tekstowe:
                try:
                    await channel.send(wiadomość)
                    sukces += 1
                    await asyncio.sleep(0.2)
                except Exception as e:
                    błędy += 1
                    print(f"Błąd na kanale {channel.name}: {e}")
        wynik = f"✅ Wysłano {sukces} wiadomości na {len(kanały_tekstowe)} kanałów (po {ile_razy} razy). Błędów: {błędy}."
    else:
        wynik = "❌ Brak kanałów tekstowych – pomijam wysyłanie."

    # ---- Część 2: opcjonalna zmiana nazw kanałów ----
    if zmiana_nazwy:
        wszystkie_kanały = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
        if not wszystkie_kanały:
            wynik += "\n❌ Brak kanałów do zmiany nazw."
        else:
            sukces_nazw = 0
            błedy_nazw = 0
            for i, kanał in enumerate(wszystkie_kanały, start=1):
                try:
                    nazwa = f"{zmiana_nazwy}-{i}"
                    await kanał.edit(name=nazwa)
                    sukces_nazw += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    błedy_nazw += 1
                    print(f"Błąd przy zmianie nazwy kanału {kanał.name}: {e}")
            wynik += f"\n🔄 Zmieniono nazwy {sukces_nazw} kanałów na `{zmiana_nazwy}-X`. Błędów: {błedy_nazw}."

    await interaction.followup.send(wynik, ephemeral=True)

# ================== KOMENDY STATUSÓW ==================
@bot.tree.command(name="setstatus1", description="✅ Ustawia pierwszy status dla użytkownika")
async def setstatus1(interaction: discord.Interaction, user: discord.Member, status: str, description: str):
    if status.lower() not in ["jestem", "nie ma"]:
        await interaction.response.send_message("❌ Status musi być `jestem` lub `nie ma`.", ephemeral=True)
        return
    if str(user.id) not in custom_status:
        custom_status[str(user.id)] = {"name": str(user)}
    custom_status[str(user.id)]["status1"] = status.lower()
    custom_status[str(user.id)]["desc1"] = description
    save_custom_status()
    await interaction.response.send_message(f"✅ Ustawiono pierwszy status dla {user.mention}: **{status}** – {description}", ephemeral=True)

@bot.tree.command(name="setstatus2", description="✅ Ustawia drugi status dla użytkownika")
async def setstatus2(interaction: discord.Interaction, user: discord.Member, status: str, description: str):
    if status.lower() not in ["jestem", "nie ma"]:
        await interaction.response.send_message("❌ Status musi być `jestem` lub `nie ma`.", ephemeral=True)
        return
    if str(user.id) not in custom_status:
        custom_status[str(user.id)] = {"name": str(user)}
    custom_status[str(user.id)]["status2"] = status.lower()
    custom_status[str(user.id)]["desc2"] = description
    save_custom_status()
    await interaction.response.send_message(f"✅ Ustawiono drugi status dla {user.mention}: **{status}** – {description}", ephemeral=True)

@bot.tree.command(name="editstatus", description="✏️ Edytuje istniejący status użytkownika (1 lub 2)")
async def editstatus(interaction: discord.Interaction, user: discord.Member, który: int, status: str, opis: str):
    if str(user.id) not in custom_status:
        await interaction.response.send_message(f"❌ Użytkownik {user.mention} nie ma jeszcze żadnych statusów.", ephemeral=True)
        return
    if który not in [1, 2]:
        await interaction.response.send_message("❌ Numer statusu musi być 1 lub 2.", ephemeral=True)
        return
    if status.lower() not in ["jestem", "nie ma"]:
        await interaction.response.send_message("❌ Status musi być `jestem` lub `nie ma`.", ephemeral=True)
        return
    key = f"status{który}"
    if key not in custom_status[str(user.id)]:
        await interaction.response.send_message(f"❌ Użytkownik {user.mention} nie ma ustawionego statusu {który}.", ephemeral=True)
        return
    custom_status[str(user.id)][key] = status.lower()
    custom_status[str(user.id)][f"desc{który}"] = opis
    save_custom_status()
    await interaction.response.send_message(f"✅ Zaktualizowano status {który} dla {user.mention}: **{status}** – {opis}", ephemeral=True)

@bot.tree.command(name="status", description="🟢 Wyświetla niestandardowe statusy użytkowników")
async def show_status(interaction: discord.Interaction):
    if not custom_status:
        await interaction.response.send_message("❌ Brak ustawionych statusów.", ephemeral=True)
        return
    embed = discord.Embed(
        title="🟢 **STATUS SERWERA**",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    for user_id, data in custom_status.items():
        member = interaction.guild.get_member(int(user_id))
        mention = member.mention if member else f"<@{user_id}> (opuścił serwer)"
        status_lines = []
        if "status1" in data:
            emoji1 = "✅" if data["status1"] == "jestem" else "❌"
            status_lines.append(f"**1:** {emoji1} {data['status1']} – {data['desc1']}")
        if "status2" in data:
            emoji2 = "✅" if data["status2"] == "jestem" else "❌"
            status_lines.append(f"**2:** {emoji2} {data['status2']} – {data['desc2']}")
        if not status_lines:
            status_lines = ["Brak ustawionych statusów"]
        embed.add_field(
            name=f"{mention}",
            value="\n".join(status_lines),
            inline=False
        )
    embed.set_footer(text=f"Wywołane przez {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ================== KOMENDA PRZYLOTY / ODLOTY ==================
@bot.tree.command(name="przyloty", description="🔧 Ustawia kanał powitalny (gdzie bot wita nowych użytkowników)")
async def przyloty(interaction: discord.Interaction, kanał: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    guild_id = str(interaction.guild.id)
    welcome_config[guild_id] = str(kanał.id)
    save_welcome_config()
    await interaction.response.send_message(f"✅ Kanał powitalny ustawiony na {kanał.mention}", ephemeral=True)

@bot.tree.command(name="odloty", description="🔧 Ustawia kanał pożegnalny (gdzie bot żegna opuszczających)")
async def odloty(interaction: discord.Interaction, kanał: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Tylko administrator może użyć tej komendy!", ephemeral=True)
        return
    guild_id = str(interaction.guild.id)
    goodbye_config[guild_id] = str(kanał.id)
    save_goodbye_config()
    await interaction.response.send_message(f"✅ Kanał pożegnalny ustawiony na {kanał.mention}", ephemeral=True)

# ================== KOMENDA PREFIKSOWA !gi ==================
@bot.command(name="gi")
async def gi(ctx):
    embed = discord.Embed(
        title="🤖 **AdaxBot Commands**",
        description="Hello! I'm **AdaxBot**, a multifunctional Discord bot created by **Adax_nrg**. Here are my commands:",
        color=discord.Color.purple()
    )
    embed.add_field(name="🎁 Giveaway", value="`/gcreate` – Create a giveaway\n`/reroll` – Reroll a giveaway", inline=False)
    embed.add_field(name="🛠️ Moderation", value="`/clear` – Clear messages\n`/ban` – Ban a user\n`/kick` – Kick multiple users", inline=False)
    embed.add_field(name="🎫 Tickets", value="`/ticket` – Create a ticket panel", inline=False)
    embed.add_field(name="📊 Invites", value="`/invites` – Check invites\n`/topinvites` – Top 10 inviters\n`/usunzaproszenia` – Delete user's invites\n`/usunwszystkiezaproszenia` – Delete all invites", inline=False)
    embed.add_field(name="📝 Fun", value="`/fakemessage` – Send a fake message\n`/typein` – Send a message as bot\n`/changekanal` – Change all text channel names\n`/announce` – Announce to all channels (max 100 repeats)", inline=False)
    embed.add_field(name="📌 Custom Status", value="`/setstatus1 <user> <jestem/nie ma> <opis>` – Set first status\n`/setstatus2 <user> <jestem/nie ma> <opis>` – Set second status\n`/editstatus <user> <1/2> <jestem/nie ma> <opis>` – Edit existing status\n`/status` – Show all custom statuses", inline=False)
    embed.add_field(name="📌 Welcome/Goodbye", value="`/przyloty #kanał` – Ustawia kanał powitalny\n`/odloty #kanał` – Ustawia kanał pożegnalny", inline=False)
    embed.add_field(name="💬 Auto-responses", value="Words like `dupa`, `adax`, `doner`, `ania`, `luki`, `co`, `essa`, `bambik`, `spierdalaj`, `elo`, `pachołek`, `panto`, `szczeka` trigger funny replies with mention!", inline=False)
    embed.set_footer(text="Bot made with ❤️ by Adax_nrg")
    await ctx.send(embed=embed)

# ================== KOMENDY PREFIKSOWE ==================
@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong!')

@bot.command()
async def siema(ctx):
    await ctx.send('👋 Siema!')

@bot.command()
async def kostka(ctx):
    await ctx.send(f'🎲 Wyrzuciłeś: **{random.randint(1,6)}**')

@bot.command()
async def hej(ctx):
    await ctx.send(f'👋 Hej {ctx.author.name}!')

# ================== START ==================
bot.run(TOKEN)
