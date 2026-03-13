# 🌀 Vortex VCF

Glass-morphic web app that collects contacts & builds hype for exclusive VCF drops. Users enter name + number → see live counter → join Telegram channel.

![Preview](static/bg.png)

---

## ✨ Features

- **Glass UI** – Sleek design with your background image
- **Typewriter Hype** – Rotating messages that grab attention
- **Mega Join Button** – Impossible to miss Telegram link
- **Admin Dashboard** – Export CSV/VCF, delete contacts
- **Anti-Devtools** – Blocks inspection & hacking attempts

---

## ⚡ 60-Second Setup

```bash
# 1. Clone
git clone https://github.com/yourusername/vortex-vcf.git
cd vortex-vcf

# 2. Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Add your bg.png to /static folder

# 4. Create .env file
echo "ADMIN_USERNAME=your_username" > .env
echo "ADMIN_PASSWORD=your_password" >> .env
echo "SECRET_KEY=your_secret_key" >> .env

# 5. Run
python app.py
