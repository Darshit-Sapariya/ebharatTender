# 🏛️ eBharat Tender

> Modern E-Procurement & Tender Bidding Portal built with **Django, Python & Bootstrap**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0.2-green?logo=django)
![Razorpay](https://img.shields.io/badge/Razorpay-EMD%20Payments-blue?logo=razorpay)
![Cloudinary](https://img.shields.io/badge/Cloudinary-Media%20Storage-blueviolet?logo=cloudinary)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

**eBharat Tender** is a modern **e-procurement and digital bidding management web application** designed for government agencies, private organizations, contractors, and financial institutions.

The application digitizes the traditional offline tender submission process into a transparent online workflow—enabling organizations to publish tenders, contractors to submit technical/financial bids with document uploads, pay EMD fees securely via Razorpay, and admins to evaluate and award contracts.

Built using:

- Python
- Django
- HTML5
- CSS3 & Bootstrap 5
- JavaScript / jQuery
- Cloudinary
- SQLite / PostgreSQL

---

# ✨ Features

## 🏢 User Registration & Profile Verification (KYC)

- Role-based User Registration (Tender Creator & Bidder)
- Government ID Upload (Aadhaar, PAN Card, Voter ID, Passport, Driving License, GSTIN)
- Sensitive Government ID Masking (`********1234`)
- Google OAuth2 Social Login (`django-allauth`)
- In-App Notifications for Account Approvals & Status Updates

---

## 📋 Tender Management

- Create & Draft Tenders with Detailed Specifications
- Auto Tender ID Generation (`EBT-2026-0001`)
- Department & Category Classification
- Estimated Tender Value & EMD Fee Calculation
- Pre-bid Meeting Date & Tender Closing Deadlines
- Public Tender Searching & Filtering (by Department, Location, Status)
- Downloadable Tender Document Uploads

---

## 💼 Bidding & Application Portal

- Online Bid Application Form
- Company Profile & GST Details Submission
- Multi-Document Upload Support:
  - GST Certificate Document
  - Financial Statements
  - Technical Bid Documents
  - Financial Bid Documents
- Real-time Bid Status Tracking (`Pending`, `Approved`, `Rejected`, `Awarded 🏆`)

---

## 💳 Razorpay EMD Payment Gateway

- Integrated Razorpay Online Payment Gateway
- Automatic Order Generation & Payment Verification
- Safe Earnest Money Deposit (EMD) Transaction Tracking
- Payment Status Management (`Pending`, `Paid`, `Refunded`)

---

## 🎛️ Core Admin & Moderation Panel

- Custom Management Portal for System Administrators
- User Profile KYC Approval & Rejection with Admin Remarks
- Tender Publishing Approval Workflow
- Bidders Evaluation & Contract Awarding (`Awarded 🏆`)
- Automated Email & In-App Notification Triggers

---

## 📊 Funding & Financial Tracking

- Project Budget Allocation
- Escrow Security Deposit Management
- Milestone-based Financial Tracking

---

## ⚡ Other Features

- Responsive Bootstrap 5 UI
- Fast Search & Datatables Integration
- Cloud & Local Media Switcher (Cloudinary + Local Filesystem)
- Dynamic Notifications System

---

# 🖥 Screenshots

## Home Page

![Home Page](assets/screenshots/01_home.png)

---

## User Registration & KYC Upload

![User Registration](assets/screenshots/02_registration.png)

---

## Tender Search & Catalog

![Tender Search](assets/screenshots/03_tender_list.png)

---

## Tender Details Page

![Tender Details](assets/screenshots/04_tender_detail.png)

---

## Bid Submission Portal

![Bid Submission](assets/screenshots/05_bid_submission.png)

---

## Razorpay EMD Payment Gateway

![Razorpay Payment](assets/screenshots/06_razorpay_emd.png)

---

## Core Admin Dashboard

![Admin Panel](assets/screenshots/07_admin_dashboard.png)

---

# 🛠 Tech Stack

| Technology | Usage |
|------------|-------|
| Python | Backend |
| Django 6.0.2 | Framework |
| SQLite / PostgreSQL | Database |
| HTML5 | Frontend Markup |
| CSS3 | Styling |
| Bootstrap 5 | UI Components |
| JavaScript / jQuery | Client Side |
| Razorpay API | EMD Payment Integration |
| Cloudinary | Cloud File & PDF Storage |
| WhiteNoise | Static Files Serving |

---

# 🚀 Installation

Clone Repository

```bash
git clone https://github.com/Darshit-Sapariya/ebharatTender.git
```

Move into project

```bash
cd ebharatTender
```

Create Virtual Environment

```bash
python -m venv .venv
```

Activate Virtual Environment

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Move into Django app directory

```bash
cd eBhatat_Tender
```

Apply Migrations

```bash
python manage.py migrate
```

Create Admin Superuser

```bash
python manage.py createsuperuser
```

Run Django Server

```bash
python manage.py runserver
```

Open your browser and visit: `http://127.0.0.1:8000/`

---

# 👨‍💻 Developer

**Darshit Sapariya**  
Python Django Developer  

⭐ If you like this project, don't forget to Star the repository.
