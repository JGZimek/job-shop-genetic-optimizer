#include <iostream>
#include <iomanip>
#include <filesystem>
#include <chrono>
#include "jobshop/genetic.hpp"
#include "jobshop/file_io.hpp"
#include "jobshop/solution.hpp"

namespace fs = std::filesystem;
using Clock = std::chrono::high_resolution_clock;


// ===== HELPERS =====

void print_separator(char c = '=', int width = 70) {
    std::cout << std::string(width, c) << "\n";
}

void print_section(const std::string& title) {
    std::cout << "\n";
    print_separator();
    std::cout << "  " << title << "\n";
    print_separator();
}

void print_instance_info(const jobshop::JobShopInstance& instance) {
    print_section("INSTANCE INFORMATION");
    
    std::cout << "Problem Size:\n";
    std::cout << "  Jobs:     " << instance.jobs.size() << "\n";
    std::cout << "  Machines: " << instance.num_machines << "\n";
    
    std::cout << "\nJob Operation Sequences:\n";
    for (const auto& job : instance.jobs) {
        std::cout << "  Job " << std::setw(2) << job.job_id << ": ";
        for (const auto& op : job.operations) {
            std::cout << "[M" << op.machine_id << ",T" << op.processing_time << "] ";
        }
        std::cout << "\n";
    }

    std::cout << "\nTransport Times Matrix (from machine i to j):\n";
    std::cout << "       ";
    for (size_t j = 0; j < instance.num_machines; ++j) {
        std::cout << "M" << std::setw(2) << j << "  ";
    }
    std::cout << "\n";
    
    for (size_t i = 0; i < instance.num_machines; ++i) {
        std::cout << "  M" << std::setw(2) << i << ": ";
        for (size_t j = 0; j < instance.num_machines; ++j) {
            std::cout << std::setw(3) << instance.transport_times[i][j] << "  ";
        }
        std::cout << "\n";
    }
}

void print_solution(const jobshop::Solution& solution, const std::string& label = "Solution") {
    std::cout << "\n" << label << ":\n";
    std::cout << "  Sequence: ";
    for (size_t i = 0; i < solution.operation_sequence.size(); ++i) {
        auto [job_id, op_id] = solution.operation_sequence[i];
        std::cout << "(" << job_id << "," << op_id << ")";
        if (i < solution.operation_sequence.size() - 1) {
            std::cout << " ";
        }
    }
    std::cout << "\n";
}

void print_population_stats(const jobshop::JobShopInstance& instance,
                            std::vector<jobshop::Solution>& population,
                            const std::string& label = "Population Statistics") {
    std::cout << "\n" << label << " (" << population.size() << " individuals):\n";
    
    int best_ms = INT_MAX;
    int worst_ms = 0;
    double sum_ms = 0;
    
    for (size_t i = 0; i < population.size(); ++i) {
        int ms = jobshop::calculate_makespan(instance, population[i]);
        best_ms = std::min(best_ms, ms);
        worst_ms = std::max(worst_ms, ms);
        sum_ms += ms;
        
        std::cout << "    Individual " << std::setw(2) << i << ": " << ms << "\n";
    }
    
    double avg_ms = sum_ms / population.size();
    std::cout << "  Statistics:\n";
    std::cout << "    Best:  " << best_ms << "\n";
    std::cout << "    Worst: " << worst_ms << "\n";
    std::cout << "    Avg:   " << std::fixed << std::setprecision(1) << avg_ms << "\n";
}

std::string find_instance_file(const std::string& filename) {
    std::vector<std::string> possible_paths = {
        filename,
        "data/instances/" + filename,
        "./data/instances/" + filename,
        "../data/instances/" + filename,
        "../../data/instances/" + filename
    };
    
    for (const auto& path : possible_paths) {
        if (fs::exists(path)) {
            return path;
        }
    }
    
    throw std::runtime_error("Cannot find file: " + filename + 
                           "\n  Searched paths:\n" +
                           "  - data/instances/\n" +
                           "  - ./data/instances/\n" +
                           "  - ../data/instances/\n" +
                           "  Current path: " + fs::current_path().string());
}


// ===== MAIN =====

int main(int argc, char* argv[]) {
    try {
        // Configuration
        std::string instance_filename = (argc > 1) ? argv[1] : "jsp_06x06.txt";
        size_t population_size = (argc > 2) ? std::stoul(argv[2]) : 20;
        size_t generations = (argc > 3) ? std::stoul(argv[3]) : 100;
        size_t tournament_size = 3;
        double mutation_prob = 0.2;
        unsigned int seed = 42;

        print_section("JOB SHOP SCHEDULING WITH TRANSPORTATION TIMES");
        
        // ===== 1. LOAD INSTANCE =====
        std::cout << "\nLoading instance file...\n";
        std::cout << "  Current path: " << fs::current_path() << "\n";
        
        std::string filepath = find_instance_file(instance_filename);
        std::cout << "  Found: " << filepath << "\n\n";
        
        jobshop::JobShopInstance instance = jobshop::load_instance_from_file(filepath);
        print_instance_info(instance);

        // ===== 2. SIMPLE SEQUENTIAL SOLUTION =====
        print_section("SEQUENTIAL SOLUTION (BASELINE)");
        
        jobshop::Solution simple_solution;
        for (const auto& job : instance.jobs) {
            for (size_t op_id = 0; op_id < job.operations.size(); ++op_id) {
                simple_solution.operation_sequence.emplace_back(job.job_id, op_id);
            }
        }
        
        int simple_makespan = jobshop::calculate_makespan(instance, simple_solution);
        std::cout << "\nSequential makespan: " << simple_makespan << "\n";
        print_solution(simple_solution);

        // ===== 3. RANDOM POPULATION =====
        print_section("RANDOM POPULATION GENERATION");
        
        std::cout << "\nGenerating " << population_size << " random solutions...\n";
        auto population = jobshop::generate_population(instance, population_size, seed);
        print_population_stats(instance, population, "Initial Population Statistics");

        // ===== 4. TOURNAMENT SELECTION =====
        print_section("TOURNAMENT SELECTION TEST");
        
        auto selected_parent = jobshop::tournament_selection(population, instance, tournament_size, seed);
        int selected_makespan = jobshop::calculate_makespan(instance, selected_parent);
        
        std::cout << "\nTournament size: " << tournament_size << "\n";
        std::cout << "Selected parent makespan: " << selected_makespan << "\n";

        // ===== 5. CROSSOVER TEST =====
        print_section("CROSSOVER OPERATOR TEST");
        
        jobshop::Solution child = jobshop::order_crossover(population[0], population[1], seed);
        int child_makespan = jobshop::calculate_makespan(instance, child);
        
        std::cout << "\nParent 1 makespan: " << jobshop::calculate_makespan(instance, population[0]) << "\n";
        std::cout << "Parent 2 makespan: " << jobshop::calculate_makespan(instance, population[1]) << "\n";
        std::cout << "Child makespan:    " << child_makespan << "\n";

        // ===== 6. MUTATION TEST =====
        print_section("MUTATION OPERATOR TEST");
        
        std::cout << "\nBefore mutation: " << child_makespan << "\n";
        jobshop::mutate_swap(child, seed);
        int mutated_makespan = jobshop::calculate_makespan(instance, child);
        std::cout << "After mutation:  " << mutated_makespan << "\n";

        // ===== 7. GENETIC ALGORITHM =====
        print_section("GENETIC ALGORITHM OPTIMIZATION");
        
        std::cout << "\nAlgorithm Parameters:\n";
        std::cout << "  Population size:     " << population_size << "\n";
        std::cout << "  Generations:         " << generations << "\n";
        std::cout << "  Tournament size:     " << tournament_size << "\n";
        std::cout << "  Mutation probability: " << std::fixed << std::setprecision(2) << mutation_prob << "\n";
        std::cout << "  Random seed:         " << seed << "\n";
        std::cout << "\nRunning GA...\n";

        auto start_time = Clock::now();
        
        jobshop::Solution best = jobshop::run_genetic(
            instance, population_size, generations, tournament_size, mutation_prob, seed);
        
        auto end_time = Clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

        int best_makespan = jobshop::calculate_makespan(instance, best);
        double improvement = (100.0 * (simple_makespan - best_makespan) / simple_makespan);

        std::cout << "Optimization completed in " << duration.count() << " ms\n";

        // ===== RESULTS SUMMARY =====
        print_section("RESULTS SUMMARY");
        
        std::cout << "\nBaseline (Sequential):\n";
        std::cout << "  Makespan: " << simple_makespan << "\n";
        
        std::cout << "\nGenetic Algorithm:\n";
        std::cout << "  Makespan: " << best_makespan << "\n";
        std::cout << "  Improvement: " << std::fixed << std::setprecision(1) << improvement << "%\n";
        
        std::cout << "\nOptimal Solution:\n";
        print_solution(best);

        print_separator();
        
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\nError: " << e.what() << "\n";
        return 1;
    }
}
