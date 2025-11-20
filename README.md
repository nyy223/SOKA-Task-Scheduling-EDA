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

## Algoritma EDA
Algoritma ini dirancang untuk mencari solusi optimal dalam memetakan setiap task ke VM yang berbeda-beda kapasitas CPU-nya, sehingga menghasilkan **makespan** sekecil mungkin dengan **distribusi beban yang seimbang**.

### 1. Fungsi Biaya — *Estimated Makespan*
Fungsi biaya (`calculate_estimated_makespan`) digunakan untuk menghitung waktu eksekusi total (makespan) dari suatu solusi penjadwalan. Makespan dihitung sebagai **waktu eksekusi tertinggi** dari seluruh VM.

```bash
def calculate_estimated_makespan(solution: Dict[int, str], tasks_dict: Dict[int, Task], vms_dict: Dict[str, VM]) -> float:
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}
    
    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        
        # Estimasi waktu eksekusi: beban / jumlah core
        estimated_time = task.cpu_load / vm.cpu_cores
        vm_loads[vm_name] += estimated_time
        
    return max(vm_loads.values()) if vm_loads else 0.0
```

### 2. Inisialisasi Solusi Awal — Greedy Best-Fit
EDA membutuhkan solusi awal yang baik agar iterasi lebih stabil. Maka digunakan pendekatan Greedy, yaitu:
1. Urutkan task berdasarkan beban CPU terbesar.
2. Tempatkan task pada VM yang menyebabkan waktu selesai paling kecil.

```bash
def initialize_greedy(tasks, vms):
    vm_finish_times = {vm.name: 0.0 for vm in vms}
    initial_solution = {}
    
    # Sort task berdasarkan cpu_load terbesar → terkecil
    sorted_tasks = sorted(tasks, key=lambda t: t.cpu_load, reverse=True)
    
    for task in sorted_tasks:
        best_vm = None
        min_finish = float('inf')
        
        for vm in vms:
            est = task.cpu_load / vm.cpu_cores
            new_finish = vm_finish_times[vm.name] + est
            
            if new_finish < min_finish:
                min_finish = new_finish
                best_vm = vm.name
        
        initial_solution[task.id] = best_vm
        vm_finish_times[best_vm] = min_finish
        
    return initial_solution
```

### 3. Model Probabilitas Awal (Weighted by CPU Capacity)
EDA tidak mengacak penugasan task, tetapi membuat model probabilitas untuk setiap task. Probabilitas awal setiap VM dihitung berdasarkan total core
```bash
total_cores = sum(vm.cpu_cores for vm in vms)

for task in tasks:
    probability_model[task.id] = {
        vm.name: vm.cpu_cores / total_cores
        for vm in vms
    }
```
Akibatnya, VM dengan CPU lebih besar memiliki peluang lebih besar untuk dipilih.

### 4. Proses EDA (Sampling → Evaluation → Learning)
EDA berjalan dalam beberapa iterasi. Setiap iterasi terdiri dari:

**A. Sampling Populasi Solusi**

EDA menghasilkan beberapa solusi baru menggunakan model probabilitas. Untuk setiap task, dipilih VM berdasarkan probabilitas.
```bash
for task in tasks:
    vm_choices = list(probability_model[task.id].keys())
    vm_probs = list(probability_model[task.id].values())
    chosen_vm = random.choices(vm_choices, weights=vm_probs, k=1)[0]
    new_solution[task.id] = chosen_vm
```

**B. Evaluasi Solusi & Pemilihan Elite**

Setiap solusi dihitung cost (makespan-nya), lalu hanya elite (solusi terbaik) yang dipertahankan.
```bash
evaluated_population.sort(key=lambda x: x[0])
elite_solutions = [sol for cost, sol in evaluated_population[:elite_size]]
```

**C. Pembaruan Model Probabilitas**

Model probabilitas secara bertahap “belajar” untuk menugaskan task ke VM yang lebih optimal.
* EDA menghitung frekuensi pemilihan VM.
* VM dengan core besar diberikan bonus probability (capacity bias).
* Probabilitas dinormalisasi kembali.
```bash
capacity_bias = vms_dict[vm_name].cpu_cores / total_cores * (elite_size / 5)

new_prob = (freq + capacity_bias + 1e-6) / (elite_size + capacity_bias)
probability_model[task.id][vm_name] = new_prob
```

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

--- 
# **Analisis Hasil Algoritma Task Scheduling**

## **1. Ringkasan Metrik Performa Utama**

- **Total Tugas Selesai: 20**
  - Algoritma berhasil menyelesaikan seluruh tugas tanpa ada yang gagal. Ini menunjukkan sistem berjalan dengan stabil.

- **Makespan (Waktu Total): 25.1280 detik**
  - Makespan adalah waktu dari tugas pertama mulai hingga tugas terakhir selesai. Nilai ini menjadi acuan utama efisiensi algoritma, semakin kecil semakin baik.

- **Throughput: 0.7959 tugas/detik**
  - Rata-rata sistem menyelesaikan hampir 0.8 tugas per detik. Nilai ini dapat meningkat jika distribusi beban kerja diperbaiki.

- **Total CPU Time: 254.3979 detik**
  - Merupakan akumulasi waktu kerja seluruh CPU dari semua VM. Karena bekerja paralel, angka ini lebih besar dari Makespan.

- **Total Wait Time: 66.3394 detik**
  - Total waktu tunggu seluruh tugas sebelum dieksekusi. Angka ini menunjukkan adanya antrian yang cukup besar di beberapa VM.

- **Imbalance Degree: 1.5322**
  - Menunjukkan tingkat ketidakmerataan beban kerja antar VM. Semakin dekat ke 0 semakin seimbang. Nilai 1.53 menunjukkan ketidakseimbangan yang signifikan.

- **Resource Utilization (CPU): 67.4938%**
  - Pemanfaatan CPU berada di sekitar 67%. Masih ada ruang 30%+ yang tidak terpakai, kemungkinan akibat distribusi task yang tidak merata.

# **Analisis Berdasarkan Data eda_results.csv**

## **1. Distribusi Beban Kerja (Workload Distribution)**
Jumlah tugas yang dikerjakan setiap Virtual Machine (VM):

* **VM1** → 3 tugas
  (`task-5-1`, `task-3-5`, `task-4-6`)

* **VM2** → 2 tugas
  (`task-8-15`, `task-6-18`)

* **VM3** → 8 tugas
  (`task-6-0`, `task-8-2`, `task-2-3`, `task-4-7`,
  `task-1-11`, `task-9-13`, `task-1-14`, `task-2-16`)

* **VM4** → 7 tugas
  (`task-10-4`, `task-7-8`, `task-3-9`, `task-9-10`,
  `task-7-12`, `task-5-17`, `task-10-19`)

### **Kesimpulan Distribusi**
* VM3 dan VM4 menangani **15 dari 20 task** → 75% beban kerja.
* VM2 adalah yang paling sedikit bekerja (hanya 2 task).
* Algoritma cenderung memilih VM3 dan VM4, sehingga beban tidak merata.

## **2. Analisis Queue & Wait Time**
Data start_time dan wait_time menunjukkan antrean yang panjang pada VM tertentu.

### **Contoh pada VM3**
* `task-8-2` mulai paling awal (sekitar 0.002 detik).
* `task-1-11` Bisa mulai di detik **6.901**, dikarenakan harus menunggu task sebelumnya selesai.
* Tugas-tugas selanjutnya di VM3 juga mengalami antrian panjang.

### **Kesimpulan Antrean**
Karena VM3 dan VM4 terlalu penuh, antrian di dua VM ini sangat panjang, sementara VM2 sering idle dan tidak dimanfaatkan optimal.

## **3. Analisis Makespan (Waktu Total)**
* Tugas yang selesai paling akhir adalah **task-5-17** di VM4.
* Finishing time tugas ini adalah **25.1269 detik**.
* Jadi Makespan akhir sistem adalah sekitar **25.13 detik**.
Makespan ini bisa lebih rendah jika sebagian tugas di VM3/VM4 dipindahkan ke VM2 yang lebih kosong.

## Penutup
Hasil pengujian menunjukkan bahwa algoritma task scheduling berhasil mengeksekusi seluruh 20 tugas yang diberikan tanpa error, namun distribusi beban kerja antar VM masih belum optimal. Dengan makespan sebesar 25.128 detik, sistem mampu menyelesaikan seluruh task dalam waktu yang relatif cepat, meskipun nilai ini berpotensi diturunkan lebih jauh jika pemanfaatan VM lebih seimbang.

Walaupun throughput mencapai 0.7959 tugas/detik dan resource utilization berada di 67.49%, distribusi beban kerja lebih banyak terpusat pada VM3 dan VM4 yang menangani 75% task, sementara VM2 hanya menjalankan dua task. Ketidakseimbangan ini juga tercermin dari Imbalance Degree sebesar 1.5322, menunjukkan adanya konsentrasi beban yang cukup tinggi pada dua VM yang sama. Dampaknya, antrean eksekusi pada VM3 dan VM4 menjadi panjang, tercermin dari Total Wait Time yang mencapai 66.3394 detik.

Data pada eda_results.csv memperlihatkan pola antrean yang jelas: VM3 dan VM4 sering harus menunggu eksekusi task sebelumnya selesai, sementara VM2 sering berada dalam kondisi idle. Kondisi ini berkontribusi langsung pada membesarnya waktu tunggu dan meningkatnya finish time untuk beberapa task. Dengan redistribusi tugas ke VM2 yang lebih kosong, makespan dan metrik lain berpotensi membaik secara signifikan.

Secara keseluruhan, algoritma sudah berfungsi dengan stabil dan mampu menyelesaikan seluruh task, namun masih membutuhkan peningkatan pada aspek load balancing, terutama dalam pemilihan VM agar antrian dapat diminimalkan dan utilisasi sumber daya meningkat. Pembaruan strategi penjadwalan yang lebih sadar beban (load-aware scheduling) dapat menjadi langkah berikutnya untuk meningkatkan performa sistem secara keseluruhan.

