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

} // namespace jobshop
