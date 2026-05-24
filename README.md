<div align="center">

# ⬡ API Health Monitor

**Automated REST API monitoring with real-time dashboard, uptime tracking, and instant alerts**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![APScheduler](https://img.shields.io/badge/APScheduler-3.10-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 📌 What is this?

**API Health Monitor** is a full-stack monitoring tool that automatically pings your REST API endpoints at scheduled intervals and tells you instantly when something goes down.

> Built the same concept used by enterprise tools like **Datadog**, **PagerDuty**, and **UptimeRobot** — from scratch in Python.

---

## 🔥 Features

| Feature | Description |
|---------|-------------|
| ✅ Real-time Dashboard | Live UI showing all endpoints, status, uptime, response time |
| 🔄 Auto Ping | Pings every N minutes using background scheduler |
| 📊 Uptime Tracking | Calculates uptime % across all ping history |
| ⚡ Response Time | Tracks average response time in milliseconds |
| 🔐 SSL Checker | Checks SSL certificate expiry for HTTPS endpoints |
| 📜 Ping History | Full log of every ping with status code and timestamp |
| 🚨 Down Alerts | Instant terminal alert when any endpoint goes DOWN |
| 📖 Swagger Docs | Auto-generated API documentation at `/docs` |

---
