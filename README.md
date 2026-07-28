# 🏛️ eBharat Tender — E-Procurement & Tender Management System

[![Django Version](https://img.shields.io/badge/Django-6.0.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Razorpay](https://img.shields.io/badge/Razorpay-EMD%20Payments-blue?style=for-the-badge&logo=razorpay)](https://razorpay.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media%20Storage-blueviolet?style=for-the-badge&logo=cloudinary)](https://cloudinary.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap)](https://getbootstrap.com/)

**eBharat Tender** is a full-featured, secure e-procurement and bidding web platform built specifically on **Django 6.0.2**. It streamlines the entire tendering lifecycle: from Government/Department tender publishing, bidder profile verification (Aadhaar/PAN/GSTIN), document-based bidding, **Razorpay EMD payment integration**, to admin bid evaluation and contract awarding.

---

## 📸 Screenshots & Workflow Placement Guide

> 💡 **Where & How to place Screenshots:**
> Create a folder named `assets/screenshots/` in your repository root and add your screenshots matching the filenames below.

| # | Screen Name | Suggested Image Path | Exact Alt Text (Copy & Paste) |
|---|:---|:---|:---|
| **1** | **Public Landing Page** | `assets/screenshots/01_home.png` | `![eBharat Tender Home Page](assets/screenshots/01_home.png)` |
| **2** | **User Registration & Gov ID Upload** | `assets/screenshots/02_registration.png` | `![User Registration with Gov ID Upload](assets/screenshots/02_registration.png)` |
| **3** | **Tender Search & Catalog** | `assets/screenshots/03_tender_list.png` | `![Tender Discovery and Category Filter](assets/screenshots/03_tender_list.png)` |
| **4** | **Tender Details & Document Download** | `assets/screenshots/04_tender_detail.png` | `![Tender Detail View with Auto ID EBT-YYYY-XXXX](assets/screenshots/04_tender_detail.png)` |
| **5** | **Bid Submission Portal** | `assets/screenshots/05_bid_submission.png` | `![Bid Submission with Technical and Financial Uploads](assets/screenshots/05_bid_submission.png)` |
| **6** | **Razorpay EMD Payment Gateway** | `assets/screenshots/06_razorpay_emd.png` | `![Razorpay EMD Payment Gateway](assets/screenshots/06_razorpay_emd.png)` |
| **7** | **Core Admin Dashboard** | `assets/screenshots/07_admin_dashboard.png` | `![Core Admin Dashboard for Approval and Awarding](assets/screenshots/07_admin_dashboard.png)` |

---

## ⚙️ Core Modules & Workflow Architecture

```mermaid
flowchart TD
    subgraph 1. User & Identity Management (accounts)
        U[New User Registration] --> Profile[UserProfile Creation: Role & Gov ID]
        Profile --> GovCheck{Gov ID Verification: Aadhaar/PAN/GSTIN}
        GovCheck -->|Admin Approved| VerifiedUser[Verified Bidder / Tender Creator]
        GovCheck -->|Rejected| PendingUser[Pending Profile]
    end

    subgraph 2. Tender Creation & Publishing (tenders)
        Creator[Tender Creator / Department] --> CreateTender[Create Tender Draft]
        CreateTender --> AutoID[Auto-Generate ID: EBT-2026-XXXX]
        AutoID --> TenderDoc[Upload Specifications to Cloudinary/Local]
        TenderDoc --> ActiveTender[Published Open Tender]
    end

    subgraph 3. Bidding & EMD Payment (bids)
        VerifiedUser --> ViewTender[Browse & Search Active Tenders]
        ViewTender --> BidForm[Submit Application & Company Details]
        BidForm --> UploadDocs[Upload GST, Tech & Financial Documents]
        UploadDocs --> EMD[Razorpay EMD Amount Payment]
        EMD -->|Payment Success| SubmittedBid[Submitted Bid Application]
    end

    subgraph 4. Evaluation & Contract Awarding (coreadmin)
        Admin[System / Department Admin] --> ReviewBids[Review Submitted Bids]
        ReviewBids --> Award[Award Winning Bidder 🏆]
        Award --> Notify[In-App Notification Triggered]
    end
```

---

## 🛠️ Project Stack & Exact Features

### 🔐 1. `accounts` App (Authentication & KYC)
- **Role-Based Users**: `Tender Creator` & `Bidder`.
- **Gov ID Upload & Verification**: Support for Aadhaar Card, PAN Card, Voter ID, Passport, Driving License, GSTIN Certificate.
- **Masked ID Security**: Auto-masks sensitive numbers (e.g., `********1234`).
- **Google OAuth Integration**: Powered by `django-allauth`.
- **In-App Notifications**: Real-time notifications for approval/rejection and bidding alerts.

### 📋 2. `tenders` App (Tender Lifecycle Management)
- **Auto Tender ID Generation**: Formatted as `EBT-YYYY-0001` (e.g., `EBT-2026-0001`).
- **Custom Filtering**: Filter tenders by **Department**, **Category**, **Status** (`open`, `closed`, `draft`, `awarded`), and **Location**.
- **Financial Parameters**: Auto-tracks **Estimated Value** & **EMD Amount**.
- **Document Management**: Attachment of official tender specs.

### 💼 3. `bids` App (Contractor Application & Payments)
- **Comprehensive Bid Submissions**: Company registration address, GST number, bidder designation, official contact.
- **Multi-Document Verification**: Separate file uploads for **GST Certificate**, **Financial Statement**, **Technical Document**, and **Financial Proposal**.
- **Razorpay EMD Gateway**: Integrated Razorpay order creation (`razorpay_order_id`, `razorpay_payment_id`, signature validation) for EMD (Earnest Money Deposit).
- **Status Lifecycle**: `Pending` ➔ `Approved` / `Rejected` ➔ `Awarded 🏆`.

### 🎛️ 4. `coreadmin` App (Custom Administration Portal)
- Dedicated admin portal for reviewing pending user profile verifications, approving tender drafts, evaluating bid submissions, and awarding contracts.

### 💳 5. `funding` & `public` Apps
- Public discovery pages and funding tracking modules for project allocations.

---

## 📁 Precise Project Folder Structure

```text
ebharatTender/
├── eBhatat_Tender/                   # Main Project Root Directory
│   ├── accounts/                     # User Registration, Profiles & KYC Signals
│   │   ├── models.py                 # UserProfile, Department, Category, Notification, AdminRequest
│   │   ├── pdf_utils.py              # PDF Generation utilities
│   │   └── media_utils.py            # Local & Cloudinary helper scripts
│   ├── tenders/                      # Tender creation & management logic
│   │   ├── models.py                 # Tenderss (Auto ID generator EBT-YYYY-XXXX)
│   │   └── views.py                  # Tender Listing, Search & Detail Views
│   ├── bids/                         # Bidding portal & Payment gateway
│   │   ├── models.py                 # TenderApplication (EMD & Document Uploads)
│   │   └── views.py                  # Bid Submission & Razorpay Processing
│   ├── coreadmin/                    # Custom Management & Moderation Panel
│   ├── funding/                      # Funding & Budget allocation app
│   ├── public/                       # Landing Page & Public Search
│   ├── eBhatat_Tender/               # Project Settings, URLs & WSGI/ASGI
│   │   ├── settings.py               # Configured with Cloudinary & Razorpay
│   │   └── media_config.py           # Smart Cloudinary vs Local Storage switcher
│   ├── ebahtar_tenderDB.sqlite3      # SQLite Database File
│   └── manage.py                     # Django CLI
├── requirements.txt                  # Python Package Dependencies
├── .env                              # Environment Variables
├── assets/
│   └── screenshots/                  # Place README Screenshots Here
└── README.md                         # Project Documentation
```

---

## ⚡ Quick Setup & Running Locally

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ebharatTender.git
cd ebharatTender
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables (`.env`)
Create a `.env` file in the root directory:
```env
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Cloudinary Setup (Optional - Falls back to local media automatically)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Razorpay EMD Payment Credentials
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

### 5. Run Migrations & Start Server
```bash
cd eBhatat_Tender
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser.

---

## 📜 License

This project is open-source and available under the **MIT License**.
