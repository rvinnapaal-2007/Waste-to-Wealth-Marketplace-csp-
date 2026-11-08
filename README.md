# 🌾 Waste to Wealth Marketplace

**A website where farmers sell their farm waste, and companies buy it.**

> Community Service Project: *"From Waste to Wealth: Rural Agricultural Sustainability"*
> Kavuluru Village, G. Konduru Mandal, NTR District, Andhra Pradesh

🔗 **Live website:** _add your Render link here, for example https://your-name.onrender.com_

---

## 🧒 What is this? (Explained simply)

Imagine a farmer who grows sugarcane. He squeezes the sugarcane to make juice. What is left over is a pile of dry pulp. It is called **waste**, so he usually **burns it** or **throws it away**.

But that "waste" is not useless! 🎉

| Farm waste | What a company can make from it |
|---|---|
| 🎋 Sugarcane pulp (bagasse) | Plates and bowls you can throw away safely |
| 🌾 Paddy straw | Fuel blocks (biobriquettes), compost, mushroom beds |
| 🍚 Rice husk | Fuel blocks and boiler fuel |
| 🥜 Groundnut shells | Fuel blocks that can be used instead of charcoal |
| 🥥 Coconut shells | Charcoal and rope-like coir products |

The problem: the farmer does not know **who wants to buy** his waste, and the company does not know **who has waste to sell**.

**This website connects them.** Think of it like an online village market, only for farm waste. 🛒

---

## 🎬 How it works (3 easy steps)

```
   🚜 FARMER                    🌐 THE WEBSITE                  🏭 BUYER
   ---------                    --------------                  --------
1. Signs up and writes   -->   Shows the waste on the    -->   2. Signs up, looks at the
   "I have 500 kg of            Browse page for                   list, and clicks
   paddy straw. Price           everyone to see                   "Contact this farmer"
   Rs 1.5 per kg"

                         3. The farmer sees the buyer's phone number and calls him.
                            They make a deal. The farmer clicks "Mark sold". ✅
```

---

## ✨ What can you do on the website?

### If you are a farmer 🚜
- Create your own account (sign up) and log in
- Add your waste: type, how many kg, price, and when it is ready
- See all the buyers who asked for your waste, with their phone numbers
- Mark your waste as **sold**, or delete it

### If you are a buyer 🏭
- Create your own account (sign up) and log in
- Look at all the waste for sale
- **Search** by village or name, and **sort** by price or quantity
- Send a request to a farmer
- See the farmer's name, village and phone number in your dashboard

### Everybody (even without an account)
- See the home page with live numbers and a bar chart
- Browse all the waste that is for sale

### The admin (the manager of the website) 🔑
- See all farmers, buyers, listings and requests in one place

> 🔒 **Safety:** passwords are never saved as normal words. They are scrambled (hashed), so even the website owner cannot read them.

---

## 🖼️ Screenshots

_Add your pictures in a folder named `screenshots` and they will show here._

| Home page | Browse waste |
|---|---|
| ![Home](screenshots/home.png) | ![Browse](screenshots/browse.png) |

| Farmer dashboard | Buyer dashboard |
|---|---|
| ![Farmer](screenshots/farmer-dashboard.png) | ![Buyer](screenshots/buyer-dashboard.png) |

| Sign up page | Database in pgAdmin |
|---|---|
| ![Signup](screenshots/signup.png) | ![Database](screenshots/database.png) |

---

## 🧰 What was used to build it?

Think of the website like a **restaurant**:

| Part of the restaurant | Part of our project | Tool used |
|---|---|---|
| 🍽️ The menu and tables you see | **Frontend** (the pages) | HTML, CSS, JavaScript |
| 👨‍🍳 The kitchen that does the work | **Backend** (the brain) | Python and Flask |
| 🗄️ The big store room with ingredients | **Database** (the memory) | PostgreSQL |
| 👀 A window to look inside the store room | Database viewer | pgAdmin 4 |
| 📦 A lunch box that carries everything | Packaging | Docker |
| ☁️ The restaurant's address on the internet | Hosting | Render (website) and Neon (database) |

---

## 🗄️ What does the database remember?

The database is like four notebooks:

| Notebook (table) | What is written in it |
|---|---|
| `farmers` | Name, email, phone, village, scrambled password |
| `buyers` | Name, email, phone, company, type of buyer, scrambled password |
| `listings` | Each waste for sale: type, kg, price, village, sold or not |
| `inquiries` | Each request a buyer sent to a farmer |

---

## 🚀 How to run it on your own computer

You need **Docker Desktop** installed (it is free). Then:

**Step 1.** Download this project and open a terminal in the project folder.

**Step 2.** Type this one command and press Enter:

```
docker compose up -d --build
```

**Step 3.** Open your browser and go to:

```
http://localhost:5000
```

🎉 The website is running on your computer!

To stop it: `docker compose down`  ·  To start it again: `docker compose up -d`

### Want to see the saved data? (pgAdmin)
Connect pgAdmin 4 to the database with these settings:

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5433` |
| Database | `agri_marketplace` |
| Username | `postgres` |
| Password | `*****` |

Then open: Databases → agri_marketplace → Schemas → public → Tables.

### The admin page
Go to `http://localhost:5000/admin`. The admin password is set in `app.py` (`ADMIN_PASSWORD`). Change it before sharing the website with anyone.

---

## 📁 What is inside this folder?

```
📦 Waste-to-Wealth-Marketplace
 ┣ 📄 app.py                 ← the brain: all the rules of the website
 ┣ 📁 templates              ← the pages people see
 ┃  ┣ base.html              (top menu and bottom, shared by all pages)
 ┃  ┣ index.html             (home page)
 ┃  ┣ auth.html              (sign up and log in)
 ┃  ┣ listings.html          (browse waste)
 ┃  ┣ farmer.html            (farmer dashboard)
 ┃  ┣ buyer.html             (buyer dashboard)
 ┃  ┗ admin.html             (admin page)
 ┣ 📁 static
 ┃  ┗ style.css              (colours and design)
 ┣ 📄 requirements.txt       ← list of Python tools needed
 ┣ 📄 Dockerfile             ← recipe to pack the website in a "lunch box"
 ┣ 📄 docker-compose.yml     ← starts the website and the database together
 ┗ 📄 Procfile               ← tells the hosting site how to start the website
```

---

## 🌍 Why does this matter?

Burning farm waste makes **smoke and air pollution**, and the village loses useful material. When farmers sell the waste instead, they **earn extra money**, the air stays cleaner, and companies get **natural raw material**. 💚

This project supports these goals of the United Nations (SDGs):

| Goal | How we help |
|---|---|
| **SDG 2** Zero Hunger | Farmers earn more and farm in a better way |
| **SDG 12** Responsible Consumption and Production | Waste is used again instead of thrown away |
| **SDG 13** Climate Action | Less burning means less pollution |
| **SDG 15** Life on Land | Healthier soil and a cleaner environment |

---

## 👩‍💻 Team

| Name | Reg. No. |
|---|---|
| Damerla Lasya Surarchita | 24761A1215 |
| Challa Charan | 24761A1209 |
| Vinnapala Revanth | 24761A1265 |

**Guide:** Dr. B. Srinivasa Rao, Professor, Department of Information Technology
**College:** Lakireddy Bali Reddy College of Engineering (Autonomous), Mylavaram
**Academic Year:** 2026-2027

---

## 📌 Things this project does not do yet

- Forgotten passwords cannot be reset
- Payments are not on the website: the farmer and buyer talk on the phone
- Only English is available

These can be added in the future.

---

_Made with 💚 for the farmers of Kavuluru village._
