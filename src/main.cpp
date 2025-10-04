#include <iostream>
#include <random>
#include "jobshop/genetic.hpp"
#include "jobshop/core.hpp"
#include "jobshop/file_io.hpp"
#include "jobshop/solution.hpp"

int main() {
    // Ścieżka do przykładowej instancji
    std::string filename = "../data/instances/instance_small.txt";
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

    // --- Test selekcji turniejowej ---
    size_t tournament_size = 3;
    auto parent = jobshop::tournament_selection(population, instance, tournament_size, rng);
    int parent_makespan = jobshop::calculate_makespan(instance, parent);
    std::cout << "\nSelected parent (tournament):\n";
    for (const auto& op : parent.operation_sequence) {
        std::cout << "(" << op.first << "," << op.second << ") ";
    }
    std::cout << "\nParent makespan: " << parent_makespan << std::endl;


    return 0;
}
