#include "jobshop/genetic.hpp"
#include <algorithm>

namespace jobshop {

Solution generate_random_solution(const JobShopInstance& instance, std::mt19937& rng) {
    Solution sol;
    for (const auto& job : instance.jobs) {
        for (size_t op_id = 0; op_id < job.operations.size(); ++op_id) {
            sol.operation_sequence.emplace_back(job.job_id, op_id);
        }
    }
    std::shuffle(sol.operation_sequence.begin(), sol.operation_sequence.end(), rng);
    return sol;
}

std::vector<Solution> generate_population(const JobShopInstance& instance, size_t population_size, std::mt19937& rng) {
    std::vector<Solution> population;
    for (size_t i = 0; i < population_size; ++i) {
        population.push_back(generate_random_solution(instance, rng));
    }
    return population;
}

Solution tournament_selection(const std::vector<Solution>& population, const JobShopInstance& instance, size_t tournament_size, std::mt19937& rng) {
    std::uniform_int_distribution<size_t> dist(0, population.size() - 1);
    Solution best = population[dist(rng)];
    Solution best_copy = best;
    int best_makespan = calculate_makespan(instance, best_copy);
    for (size_t i = 1; i < tournament_size; ++i) {
        const Solution& contender = population[dist(rng)];
        Solution contender_copy = contender;
        int contender_makespan = calculate_makespan(instance, contender_copy);
        if (contender_makespan < best_makespan) {
            best = contender;
            best_makespan = contender_makespan;
        }
    }
    return best;
}


} // namespace jobshop
