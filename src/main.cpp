#include <iostream>
#include <random>
#include "jobshop/genetic.hpp"
#include "jobshop/file_io.hpp"
#include "jobshop/solution.hpp"
#include "jobshop/greedy.hpp"
#include "jobshop/exact.hpp"


int main() {
    // Ścieżka do przykładowej instancji
    std::string filename = "../data/instances/instance_large.txt";
    jobshop::JobShopInstance instance = jobshop::load_instance_from_file(filename);

    std::cout << "Jobs: " << instance.jobs.size() << "\n";
    std::cout << "Machines: " << instance.num_machines << "\n\n";

    for (const auto& job : instance.jobs) {
        std::cout << "Job " << job.job_id << ": ";
        for (const auto& op : job.operations) {
            std::cout << "[M" << op.machine_id << ",T" << op.processing_time << "] ";
        }
        std::cout << "\n";
    }

    std::cout << "\nTransport times matrix:\n";
    for (size_t i = 0; i < instance.num_machines; ++i) {
        for (size_t j = 0; j < instance.num_machines; ++j) {
            std::cout << instance.transport_times[i][j] << " ";
        }
        std::cout << "\n";
    }

    // Tworzymy prostą kolejność operacji: po kolei dla każdego zadania
    jobshop::Solution solution;
    for (const auto& job : instance.jobs) {
        for (size_t op_id = 0; op_id < job.operations.size(); ++op_id) {
            solution.operation_sequence.emplace_back(job.job_id, op_id);
        }
    }

    // Obliczamy makespan
    int makespan = jobshop::calculate_makespan(instance, solution);
    std::cout << "\nCalculated makespan: " << makespan << "\n";

    // Wypisz czasy startu operacji
    std::cout << "Operation start times:" << std::endl;
    for (size_t i = 0; i < solution.operation_sequence.size(); ++i) {
        auto [job_id, op_id] = solution.operation_sequence[i];
        std::cout << "Job " << job_id << ", Op " << op_id << ": " << solution.start_times[i] << std::endl;
    }

    std::random_device rd;
    std::mt19937 rng(rd());
    size_t population_size = 5;
    auto population = jobshop::generate_population(instance, population_size, rng);

    std::cout << "\nRandom population (" << population_size << "):\n";
    for (size_t i = 0; i < population.size(); ++i) {
        int ms = jobshop::calculate_makespan(instance, population[i]);
        std::cout << "Individual " << i << ": makespan = " << ms << "\n";
    }

    // Test selekcji turniejowej
    size_t tournament_size = 3;
    auto parent = jobshop::tournament_selection(population, instance, tournament_size, rng);
    int parent_makespan = jobshop::calculate_makespan(instance, parent);
    std::cout << "\nSelected parent (tournament):\n";
    for (const auto& op : parent.operation_sequence) {
        std::cout << "(" << op.first << "," << op.second << ") ";
    }
    std::cout << "\nParent makespan: " << parent_makespan << std::endl;

    // Wybierz dwóch różnych rodziców
    std::uniform_int_distribution<size_t> dist(0, population.size() - 1);
    size_t idx1 = dist(rng);
    size_t idx2 = dist(rng);
    while (idx2 == idx1) idx2 = dist(rng);

    const auto& parent1 = population[idx1];
    const auto& parent2 = population[idx2];

    jobshop::Solution child = jobshop::order_crossover(parent1, parent2, rng);
    int child_makespan = jobshop::calculate_makespan(instance, child);

    std::cout << "\nCrossover (OX) between Individual " << idx1 << " and Individual " << idx2 << ":\n";
    std::cout << "Child sequence:\n";
    for (const auto& op : child.operation_sequence) {
        std::cout << "(" << op.first << "," << op.second << ") ";
    }
    std::cout << std::endl;
    std::cout << "Child makespan: " << child_makespan << std::endl;

    // Mutacja dziecka
    jobshop::mutate_swap(child, rng);
    int mutated_makespan = jobshop::calculate_makespan(instance, child);
    std::cout << "\nChild after mutation (swap):\n";
    for (const auto& op : child.operation_sequence) {
        std::cout << "(" << op.first << "," << op.second << ") ";
    }
    std::cout << std::endl;
    std::cout << "Mutated child makespan: " << mutated_makespan << std::endl;

    // Uruchom algorytm genetyczny
    size_t generations = 50;
    // size_t tournament_size = 3; // już zdefiniowane wcześniej (linia 63)
    // size_t population_size = 5; // już zdefiniowane wcześniej (linia 53)
    double mutation_prob = 0.2;

    jobshop::Solution best = jobshop::run_genetic(
        instance, population_size, generations, tournament_size, mutation_prob, rng);
    int best_makespan = jobshop::calculate_makespan(instance, best);

    std::cout << "\nBest solution after evolution:" << std::endl;
    for (const auto& op : best.operation_sequence) {
        std::cout << "(" << op.first << "," << op.second << ") ";
    }
    std::cout << std::endl;
    std::cout << "Best makespan: " << best_makespan << std::endl;

    // ===  Uruchomienie algorytmu zachłannego ===
    jobshop::Solution solution2 = jobshop::greedy_schedule(instance);

    // === Wyświetlenie wyników ===
    std::cout << "Wynikowy harmonogram (kolejność operacji):\n";
    for (size_t i = 0; i < solution2.operation_sequence.size(); ++i) {
        auto [job_id, op_id] = solution2.operation_sequence[i];
        std::cout << "Operacja (" << job_id << "," << op_id << ") "
                  << "start: " << solution2.start_times[i] << " "
                  << "czas trwania: "
                  << instance.jobs[job_id].operations[op_id].processing_time
                  << "\n";
    }

    std::cout << "\nMakespan: " << solution2.makespan << " jednostek czasu\n";


//A-Star exact solver
std::cout << "\n=== Running exact A* solver (optimal, may still be expensive) ===\n";
jobshop::Solution optimal = jobshop::solve_exact(instance);
std::cout << "A* optimal makespan: " << optimal.makespan << "\n";
std::cout << "A* optimal sequence:\n";
for (size_t i = 0; i < optimal.operation_sequence.size(); ++i) {
    auto [job_id, op_id] = optimal.operation_sequence[i];
    std::cout << "(" << job_id << "," << op_id << ") start=" << optimal.start_times[i] << "\n";
}

    return 0;
}
