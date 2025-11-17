# eda_algorithm.py (Versi Final Lengkap dengan Fix dan Optimasi)

import random
from collections import namedtuple
from typing import List, Dict

# Definisi namedtuple yang sama dengan scheduler.py
VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])

# --- Fungsi Biaya (Cost Function) ---

def calculate_estimated_makespan(solution: Dict[int, str], tasks_dict: Dict[int, Task], vms_dict: Dict[str, VM]) -> float:
    """
    Fungsi Biaya. Memperkirakan makespan.
    Model: makespan = max(total_beban_cpu_vm / core_vm)
    """
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}
    
    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        
        # Estimasi waktu eksekusi: beban / jumlah core
        estimated_time = task.cpu_load / vm.cpu_cores
        vm_loads[vm_name] += estimated_time
        
    return max(vm_loads.values()) if vm_loads else 0.0

# --- Fungsi Inisialisasi Greedy (Awal yang Lebih Baik) ---

def initialize_greedy(tasks: List[Task], vms: List[VM]) -> Dict[int, str]:
    """
    Membuat solusi awal menggunakan strategi Greedy Best-Fit.
    """
    vms_dict = {vm.name: vm for vm in vms}
    
    # PERBAIKAN: Iterasi pada NamedTuple 'vms'
    vm_finish_times = {vm.name: 0.0 for vm in vms} 
    initial_solution = {}
    
    # Urutkan tugas dari yang terbesar ke terkecil
    sorted_tasks = sorted(tasks, key=lambda t: t.cpu_load, reverse=True)
    
    for task in sorted_tasks:
        best_vm_name = None
        min_finish_time = float('inf')
        
        for vm in vms_dict.values():
            estimated_time = task.cpu_load / vm.cpu_cores
            
            new_finish_time = vm_finish_times[vm.name] + estimated_time
            
            if new_finish_time < min_finish_time:
                min_finish_time = new_finish_time
                best_vm_name = vm.name 
        
        if best_vm_name:
            initial_solution[task.id] = best_vm_name
            vm_finish_times[best_vm_name] = min_finish_time
            
    return initial_solution

# --- Algoritma Estimation of Distribution (EDA) yang Dioptimalkan ---

def eda_optimize_schedule(
    tasks: List[Task], 
    vms: List[VM], 
    iterations: int, 
    population_size: int = 100,
    elite_size: int = 20
) -> Dict[int, str]:
    """
    Menjalankan algoritma EDA dengan inisialisasi Greedy dan bobot VM berbasis kapasitas.
    """
    
    print(f"Memulai Estimation of Distribution Algorithm ({iterations} iterasi, Populasi {population_size})...")
    
    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}
    vm_names = list(vms_dict.keys())
    num_vms = len(vm_names)
    num_tasks = len(tasks)
    
    if num_tasks == 0 or num_vms == 0:
        return {}

    # 1. Buat Solusi Awal (Menggunakan Greedy Initialization)
    best_assignment = initialize_greedy(tasks, vms)
    best_cost = calculate_estimated_makespan(best_assignment, tasks_dict, vms_dict)
    print(f"Estimasi Makespan Awal (Greedy): {best_cost:.2f}")

    # 2. Inisialisasi Model Distribusi
    probability_model: Dict[int, Dict[str, float]] = {}
    total_cores = sum(vm.cpu_cores for vm in vms)
    
    # Tetapkan probabilitas awal berdasarkan bobot CPU VM
    for task in tasks:
        vm_probs_weighted = {}
        for vm_name in vm_names:
            vm = vms_dict[vm_name]
            vm_probs_weighted[vm_name] = vm.cpu_cores / total_cores 
        probability_model[task.id] = vm_probs_weighted


    # 3. Iterasi EDA
    for i in range(1, iterations + 1):
        
        # --- A. Sampel: Buat Populasi dari Model Probabilitas ---
        population: List[Dict[int, str]] = []
        for _ in range(population_size):
            new_solution: Dict[int, str] = {}
            for task in tasks:
                vm_choices = list(probability_model[task.id].keys())
                vm_probs = list(probability_model[task.id].values())
                
                # Normalisasi bobot
                prob_sum = sum(vm_probs)
                if prob_sum > 0:
                    vm_probs = [p / prob_sum for p in vm_probs]
                
                chosen_vm = random.choices(vm_choices, weights=vm_probs, k=1)[0]
                new_solution[task.id] = chosen_vm
            population.append(new_solution)

        # --- B. Evaluasi: Hitung Biaya dan Ambil Elite ---
        evaluated_population = []
        for solution in population:
            cost = calculate_estimated_makespan(solution, tasks_dict, vms_dict)
            evaluated_population.append((cost, solution))

        evaluated_population.sort(key=lambda x: x[0])
        
        elite_solutions = [sol for cost, sol in evaluated_population[:elite_size]]
        current_best_cost = evaluated_population[0][0]
        
        # Perbarui solusi terbaik global
        if current_best_cost < best_cost:
            best_cost = current_best_cost
            best_assignment = evaluated_population[0][1]
            if i % 10 == 0 or i == 1:
                print(f"Iterasi {i}: Estimasi Makespan Baru: {best_cost:.2f}")
                
        # --- C. Belajar: Perbarui Model Probabilitas ---
        
        new_freq_model: Dict[int, Dict[str, int]] = {task.id: {vm: 0 for vm in vm_names} for task in tasks}
        
        for solution in elite_solutions:
            for task_id, vm_name in solution.items():
                new_freq_model[task_id][vm_name] += 1
        
        # Perbarui Model Probabilitas: Probabilitas = (Frekuensi + Bobot Kapasitas) / (Elite Size + Bobot Kapasitas)
        for task in tasks:
            for vm_name in vm_names:
                freq = new_freq_model[task.id][vm_name]
                
                # Bobot kapasitas sebagai bias
                capacity_bias = vms_dict[vm_name].cpu_cores / total_cores * (elite_size / 5) 
                
                new_prob = (freq + capacity_bias + 1e-6) / (elite_size + capacity_bias)
                probability_model[task.id][vm_name] = new_prob

    print(f"EDA Selesai. Estimasi Makespan Terbaik: {best_cost:.2f}")
    
    return best_assignment