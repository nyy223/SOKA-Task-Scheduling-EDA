# SOKA Task Scheduling menggunakan Estimation of Distribution Algorithm (EDA)
Proyek ini mengimplementasikan algoritma Estimation of Distribution Algorithm (EDA) untuk menyelesaikan masalah penjadwalan tugas (Task Scheduling) pada lingkungan komputasi awan heterogen (Heterogeneous Computing Environment). Tujuannya adalah untuk meminimalkan Makespan (waktu selesai total) dan memaksimalkan Resource Utilization (pemanfaatan sumber daya).

## Anggota Kelompok F
| No | Nama Anggota        | NRP           |
|----|---------------------|---------------|
| 1. | Revalina Fairuzy Azhari Putri    | 5027231001    |
| 2. | Nayla Raissa A      | 5027231054    |
| 4. | Aisha Ayya R.       | 5027231056    | 
| 5. | Aisyah Rahmasari    | 5027231072    |

## Arsitektur Proyek

Proyek terdiri dari dua komponen utama menggunakan Docker Compose:

**1. Server Flask (VM Environment)**
Mensimulasikan 4 VM heterogen dengan jumlah CPU berbeda:

| VM  | Jumlah Core |
|-----|--------------|
| VM1 | 1 Core       |
| VM2 | 2 Cores      |
| VM3 | 4 Cores      |
| VM4 | 8 Cores      |

**Total CPU: 15 Cores**

**2. Scheduler Python (EDA)**
Mengimplementasikan algoritma EDA untuk menentukan penjadwalan optimal dan mengirimkan hasilnya ke VM untuk dieksekusi.

## Installation

**1. Clone Repository**
```bash
git clone 
cd SOKA-Task-Scheduling-EDA
```

**2. Instal Lingkungan Virtual**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Cara Menjalankan
**1. Jalankan Server Flask (VM)**

```docker compose up --build -d```

**2. Jalankan Scheduler (EDA)**

```uv run scheduler.py```

## Hasil dan Analisis
<img width="634" height="407" alt="Screenshot 2025-11-17 at 21 57 14" src="https://github.com/user-attachments/assets/cca143dc-c6da-40fd-89e5-eab1e764d069" />

<img width="366" height="166" alt="Screenshot 2025-11-17 at 21 02 51" src="https://github.com/user-attachments/assets/41c5ea3c-6e8f-4d14-bc48-ac634502d1e2" />
Siap, Aisyah! Ini aku rapihin penulisannya biar **rapih, clean, dan gampang kamu copy ke GitHub** (markdown-friendly).

---

# **Analisis Hasil Eksekusi Algoritma Penjadwalan Tugas**

Berikut adalah ringkasan analisis dari hasil eksekusi algoritma penjadwalan tugas yang kamu jalankan. Penjelasan dibuat lebih jelas dan mudah dibaca.

## **1. Ringkasan Metrik Performa Utama**

### **Total Tugas Selesai: 20**
Algoritma berhasil menyelesaikan seluruh tugas tanpa ada yang gagal. Ini menunjukkan sistem berjalan dengan stabil.

### **Makespan (Waktu Total): 25.1280 detik**
Makespan adalah waktu dari tugas pertama mulai hingga tugas terakhir selesai. Nilai ini menjadi acuan utama efisiensi algoritma—semakin kecil semakin baik.

### **Throughput: 0.7959 tugas/detik**
Rata-rata sistem menyelesaikan hampir 0.8 tugas per detik. Nilai ini dapat meningkat jika distribusi beban kerja diperbaiki.

### **Total CPU Time: 254.3979 detik**
Merupakan akumulasi waktu kerja seluruh CPU dari semua VM. Karena bekerja paralel, angka ini lebih besar dari Makespan.

### **Total Wait Time: 66.3394 detik**
Total waktu tunggu seluruh tugas sebelum dieksekusi. Angka ini menunjukkan adanya antrian yang cukup besar di beberapa VM.

### **Imbalance Degree: 1.5322**
Menunjukkan tingkat ketidakmerataan beban kerja antar VM. Semakin dekat ke 0 semakin seimbang. Nilai 1.53 menunjukkan ketidakseimbangan yang signifikan.

### **Resource Utilization (CPU): 67.4938%**
Pemanfaatan CPU berada di sekitar 67%. Masih ada ruang 30%+ yang tidak terpakai, kemungkinan akibat distribusi task yang tidak merata.
