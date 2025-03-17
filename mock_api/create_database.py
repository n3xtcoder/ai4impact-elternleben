import sqlite3
import uuid
from datetime import datetime, timedelta
import random

# Create database connection
conn = sqlite3.connect('mock_api.db')
cursor = conn.cursor()

# Create webinars table
cursor.execute('''
CREATE TABLE IF NOT EXISTS webinars (
    uuid TEXT PRIMARY KEY,
    host_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    start_time TEXT NOT NULL,
    duration INTEGER NOT NULL,
    agenda TEXT,
    join_url TEXT,
    status TEXT
)
''')

# Create webinar_registrants table
cursor.execute('''
CREATE TABLE IF NOT EXISTS webinar_registrants (
    uuid TEXT PRIMARY KEY,
    webinar_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    FOREIGN KEY (webinar_id) REFERENCES webinars (uuid)
)
''')

# Create experts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS experts (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    is_available BOOLEAN NOT NULL,
    zoom_host_id TEXT NOT NULL
)
''')

# Create appointments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    uuid TEXT PRIMARY KEY,
    expert_id TEXT NOT NULL,
    service TEXT NOT NULL,
    datetime TEXT NOT NULL,
    client_name TEXT,
    client_email TEXT,
    client_phone TEXT,
    is_booked BOOLEAN NOT NULL,
    status TEXT,           
    FOREIGN KEY (expert_id) REFERENCES experts (uuid)
)
''')

# German webinar topics
webinar_topics = [
    "Elternzeit und Elterngeld: Was Sie wissen müssen",
    "Frühkindliche Entwicklung: Die ersten 3 Jahre",
    "Gesunde Ernährung für Kleinkinder",
    "Einschlafrituale und Schlafprobleme bei Babys",
    "Erste Hilfe für Säuglinge und Kleinkinder",
    "Grenzen setzen in der Erziehung",
    "Sprachentwicklung fördern",
    "Geschwisterrivalität verstehen und bewältigen",
    "Trotzphase meistern",
    "Bindung und Beziehung in den ersten Lebensjahren"
]

# German webinar topics
webinar_topics = [
    "Elternzeit und Elterngeld: Was Sie wissen müssen",
    "Frühkindliche Entwicklung: Die ersten 3 Jahre",
    "Gesunde Ernährung für Kleinkinder",
    "Einschlafrituale und Schlafprobleme bei Babys",
    "Erste Hilfe für Säuglinge und Kleinkinder",
    "Grenzen setzen in der Erziehung",
    "Sprachentwicklung fördern",
    "Geschwisterrivalität verstehen und bewältigen",
    "Trotzphase meistern",
    "Bindung und Beziehung in den ersten Lebensjahren"
]

# German webinar agendas
webinar_agendas = [
    "In diesem Webinar besprechen wir die gesetzlichen Grundlagen der Elternzeit, erklären die Berechnung des Elterngeldes, führen durch das Antragsverfahren und wichtige Fristen, diskutieren Möglichkeiten zur Teilzeitarbeit während der Elternzeit und geben Tipps, wie Sie häufige Fehler vermeiden können.",
    "Dieses Webinar behandelt die wichtigsten motorischen Meilensteine im ersten Lebensjahr, die kognitive Entwicklung von 1-3 Jahren, soziale und emotionale Entwicklungsphasen, Warnzeichen, auf die Eltern achten sollten, sowie praktische Tipps zur Förderung der kindlichen Entwicklung im Alltag.",
    "Unser Ernährungswebinar deckt den Nährstoffbedarf in verschiedenen Altersstufen ab, gibt Anleitungen zur Beikosteinführung und zum Übergang zur Familienkost, bietet Strategien für den Umgang mit wählerischen Essern, präsentiert gesunde Snack-Ideen und Mahlzeitenplanung sowie Hilfestellung beim Erkennen von Allergien und Unverträglichkeiten.",
    "In diesem Webinar erfahren Sie alles über die Entwicklung des Schlafverhaltens im ersten Lebensjahr, wie Sie wirksame Einschlafrituale etablieren können, welche häufigen Schlafprobleme auftreten und was ihre Ursachen sind, welche sanften Methoden die Schlafqualität verbessern können und wann professionelle Hilfe sinnvoll ist.",
    "Dieses wichtige Webinar vermittelt lebensrettende Notfallmaßnahmen bei Säuglingen, den richtigen Umgang mit Fieber und Krankheiten, die korrekte Versorgung von Verletzungen, effektive Prävention von Haushaltsunfällen sowie eine Übersicht, was in einen gut ausgestatteten Notfallkoffer gehört.",
    "Unser Erziehungswebinar erklärt, warum Grenzen für Kinder wichtig sind, wie altersgerechte Regeln und Konsequenzen aussehen sollten, wie man konsequent bleiben kann ohne zu strafen, gibt Strategien zum Umgang mit Wutanfällen und zeigt, wie positive Verstärkung den Erziehungsalltag erleichtern kann.",
    "Das Sprachentwicklungswebinar behandelt die wichtigsten Meilensteine der kindlichen Sprachentwicklung, gibt Tipps zum Schaffen einer sprachanregenden Umgebung, zur Bedeutung von Vorlesen und Sprachspielen, zum Umgang mit Mehrsprachigkeit in der Familie und hilft, Anzeichen für Sprachentwicklungsverzögerungen frühzeitig zu erkennen.",
    "In diesem Webinar beleuchten wir die Ursachen für Geschwisterrivalität, geben praktische Hilfestellung zum Umgang mit Streit und Konflikten, zur gerechten Aufmerksamkeitsverteilung, zum Erkennen individueller Bedürfnisse und zeigen Wege auf, wie Sie positive Geschwisterbeziehungen aktiv fördern können.",
    "Unser Webinar zur Trotzphase erklärt die entwicklungspsychologischen Hintergründe, vermittelt effektive Strategien für den Umgang mit Trotzanfällen, hilft Eltern bei der Regulation eigener Emotionen, zeigt Wege zur Entschärfung von Konfliktsituationen und gibt Tipps, wie Sie die Autonomieentwicklung Ihres Kindes positiv unterstützen können.",
    "Dieses fundamentale Webinar erläutert die Grundlagen der Bindungstheorie, zeigt, wie Sie eine sichere Bindung aufbauen und stärken können, wie Feinfühligkeit im Alltag gelebt werden kann, was bindungsorientierte Erziehung bedeutet und welche langfristigen Auswirkungen frühe Bindungserfahrungen auf die Entwicklung haben."
]

# German webinar URLs
webinar_urls = [
    "https://mock-zoom.elternleben.de/webinare/elternzeit-und-elterngeld",
    "https://mock-zoom.elternleben.de/webinare/fruehkindliche-entwicklung",
    "https://mock-zoom.elternleben.de/webinare/gesunde-ernaehrung-kleinkinder",
    "https://mock-zoom.elternleben.de/webinare/einschlafrituale-schlafprobleme",
    "https://mock-zoom.elternleben.de/webinare/erste-hilfe-saeuglinge",
    "https://mock-zoom.elternleben.de/webinare/grenzen-setzen-erziehung",
    "https://mock-zoom.elternleben.de/webinare/sprachentwicklung-foerdern",
    "https://mock-zoom.elternleben.de/webinare/geschwisterrivalitaet",
    "https://mock-zoom.elternleben.de/webinare/trotzphase-meistern",
    "https://mock-zoom.elternleben.de/webinare/bindung-beziehung-erste-lebensjahre"
]

# German names for experts
expert_data = [
    ("Dr. Anna Weber", "Kinderärztin", "host_weber"),
    ("Thomas Schröder", "Entwicklungspsychologe", "host_schroeder"),
    ("Marion Fischer", "Hebamme", "host_fischer"),
    ("Prof. Dr. Klaus Neumann", "Pädagoge", "host_neumann"),
    ("Sabine Brandt", "Ernährungsberaterin", "host_brandt"),
    ("Julia Keller", "Schlafberaterin", "host_keller"),
    ("Martin Gruber", "Familientherapeut", "host_gruber"),
    ("Dr. Petra Schulz", "Kinderpsychologin", "host_schulz"),
    ("Sophie Zimmermann", "Logopädin", "host_zimmermann"),
    ("Daniel König", "Sozialpädagoge", "host_koenig")
]

# German client names
client_names = [
    "Familie Müller",
    "Eva und Thomas Schmidt",
    "Katharina Weber",
    "Michael und Sarah Becker",
    "Familie Wagner",
    "Laura und Jan Hoffmann",
    "Sandra Fischer",
    "Familie Klein",
    "Lisa und Mark Schneider",
    "Silvia und Paul Meyer"
]

# German client emails
client_emails = [
    "muster.familie.mueller@mail.com",
    "muster.schmidt.eva@web.de",
    "muster.k.weber@gx.de",
    "muster.becker.familie@online.de",
    "muster.wagner.jan@web.de",
    "muster.hoffmann.laura@mail.com",
    "muster.s.fischer@gx.de",
    "muster.familie.klein@online.de",
    "muster.schneider.lisa@web.de",
    "muster.meyer.silvia@mail.com"
]

# German client phone numbers
client_phones = [
    "+49 176 12345678",
    "+49 152 87654321",
    "+49 170 23456789",
    "+49 151 98765432",
    "+49 177 34567890",
    "+49 155 76543210",
    "+49 172 45678901",
    "+49 157 65432109",
    "+49 171 56789012",
    "+49 159 87654321"
]

# Service IDs in German contexts
services = [
    "erstberatung",
    "folgeberatung",
    "schlafberatung",
    "entwicklungscheck",
    "ernaehrungsberatung",
    "erziehungsberatung",
    "sprachentwicklung",
    "geschwisterrivalitaet",
    "trotzphasehilfe",
    "bindungsberatung"
]

# Insert experts
expert_ids = []
for name, specialty, zoom_host_id in expert_data:
    expert_id = str(uuid.uuid4())
    expert_ids.append(expert_id)
    cursor.execute(
        "INSERT INTO experts (uuid, name, specialty, is_available, zoom_host_id) VALUES (?, ?, ?, ?, ?)",
        (
            expert_id,
            name,
            specialty,
            random.choice([1, 1, 1, 0]),  # 75% available
            zoom_host_id
        )
    )

# Insert webinars
webinar_ids = []
start_date = datetime.now()
for i in range(10):
    webinar_id = str(uuid.uuid4())
    webinar_ids.append(webinar_id)
    webinar_start = start_date + timedelta(days=i*3, hours=random.randint(9, 17))
    
    # Select a random expert to be the host
    expert_id = random.choice(expert_ids)
    
    cursor.execute(
        "INSERT INTO webinars (uuid, host_id, topic, start_time, duration, agenda, join_url, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            webinar_id,
            expert_id,
            webinar_topics[i],
            webinar_start.strftime("%Y-%m-%dT%H:%M:%S"),
            random.choice([60, 90, 120]),
            f"{webinar_agendas[i]}",
            f"{webinar_urls[i]}",
            random.choice(["scheduled", "active", "completed"])
        )
    )

# Insert webinar registrations
german_first_names = ["Anna", "Thomas", "Laura", "Michael", "Sabine", "Klaus", "Petra", "Martin", "Sophia", "Daniel"]
german_last_names = ["Müller", "Schmidt", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann", "Koch", "Richter"]
german_domains = ["mail.com", "web.de", "gx.de", "online.de", "yaho.de"]

for webinar_id in webinar_ids:
    # Create 3-7 registrants per webinar
    num_registrants = random.randint(3, 7)
    for _ in range(num_registrants):
        first_name = random.choice(german_first_names)
        last_name = random.choice(german_last_names)
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(german_domains)}"
        
        cursor.execute(
            "INSERT INTO webinar_registrants (uuid, webinar_id, name, email) VALUES (?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                webinar_id,
                f"{first_name} {last_name}",
                email
            )
        )

# Insert appointments
for i in range(50):
    # Random date in next 30 days, between 9am and 5pm
    days_ahead = random.randint(1, 30)
    hour = random.randint(9, 17)
    appointment_date = datetime.now() + timedelta(days=days_ahead)
    appointment_date = appointment_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    # 25% of appointments are booked
    is_booked = random.choice([1, 0, 0, 0])
    
    client_idx = random.randint(0, len(client_names)-1)
    client_name = client_names[client_idx] if is_booked else None
    client_email = client_emails[client_idx] if is_booked else None
    client_phone = client_phones[client_idx] if is_booked else None
    
    # Set status based on booking status
    status = random.choice(["confirmed", "pending"]) if is_booked else None
    
    cursor.execute(
        "INSERT INTO appointments (uuid, expert_id, service, datetime, client_name, client_email, client_phone, is_booked, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            random.choice(expert_ids),
            random.choice(services),
            appointment_date.strftime("%Y-%m-%dT%H:%M:%S"),
            client_name,
            client_email,
            client_phone,
            is_booked,
            status
        )
    )

# Commit changes and close connection
conn.commit()

# Print counts
cursor.execute("SELECT COUNT(*) FROM webinars")
webinar_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM webinar_registrants")
registration_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM experts")
expert_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM appointments")
appointment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM appointments WHERE is_booked = 1")
booked_appointment_count = cursor.fetchone()[0]

print(f"Database seeded successfully with:")
print(f"- {webinar_count} webinars")
print(f"- {registration_count} webinar registrations")
print(f"- {expert_count} experts")
print(f"- {appointment_count} appointments ({booked_appointment_count} booked)")

conn.close()