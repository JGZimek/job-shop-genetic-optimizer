#include "jobshop/genetic.hpp"

namespace jobshop {

Solution generate_random_solution(const JobShopInstance& instance, unsigned int seed) {
    std::mt19937 rng(seed > 0 ? seed : std::time(nullptr));
    Solution sol;
    for (const auto& job : instance.jobs) {
        for (size_t op_id = 0; op_id < job.operations.size(); ++op_id) {
            sol.operation_sequence.emplace_back(job.job_id, op_id);
        }
    }
    std::shuffle(sol.operation_sequence.begin(), sol.operation_sequence.end(), rng);
    return sol;
}

std::vector<Solution> generate_population(const JobShopInstance& instance, size_t population_size, unsigned int seed) {
    std::mt19937 rng(seed > 0 ? seed : std::time(nullptr));
    std::vector<Solution> population;
    for (size_t i = 0; i < population_size; ++i) {
        population.push_back(generate_random_solution(instance, rng()));
    }
    return population;
}

Solution tournament_selection(const std::vector<Solution>& population, const JobShopInstance& instance, size_t tournament_size, unsigned int seed) {
    std::mt19937 rng(seed > 0 ? seed : std::time(nullptr));
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

// Hash dla pary (job_id, operation_id)
struct PairHash {
    std::size_t operator()(const std::pair<size_t, size_t>& p) const noexcept {
        return std::hash<size_t>{}(p.first) ^ (std::hash<size_t>{}(p.second) << 1);
    }
};

Solution order_crossover(const Solution& parent1, const Solution& parent2, unsigned int seed) {
    std::mt19937 rng(seed > 0 ? seed : std::time(nullptr));
    size_t n = parent1.operation_sequence.size();
    Solution child;
    child.operation_sequence.resize(n);

    // Wybierz losowy przedział
    std::uniform_int_distribution<size_t> dist(0, n - 1);
    size_t start = dist(rng);
    size_t end = dist(rng);
    if (start > end) std::swap(start, end);

    std::unordered_set<std::pair<size_t, size_t>, PairHash> taken;

    // Skopiuj fragment z pierwszego rodzica
    for (size_t i = start; i <= end; ++i) {
        child.operation_sequence[i] = parent1.operation_sequence[i];
        taken.insert(child.operation_sequence[i]);
    }

    // Uzupełnij pozostałe pozycje z drugiego rodzica w kolejności
    size_t idx = (end + 1) % n;
    size_t p2_idx = (end + 1) % n;
    while (idx != start) {
        if (taken.find(parent2.operation_sequence[p2_idx]) == taken.end()) {
            child.operation_sequence[idx] = parent2.operation_sequence[p2_idx];
            taken.insert(child.operation_sequence[idx]);
            idx = (idx + 1) % n;
        }
        p2_idx = (p2_idx + 1) % n;
    }
    return child;
}

void mutate_swap(Solution& solution, unsigned int seed) {
    std::mt19937 rng(seed > 0 ? seed : std::time(nullptr));
    size_t n = solution.operation_sequence.size();
    if (n < 2) return;
    std::uniform_int_distribution<size_t> dist(0, n - 1);
    size_t i = dist(rng);
    size_t j = dist(rng);
    while (j == i) j = dist(rng);
    std::swap(solution.operation_sequence[i], solution.operation_sequence[j]);
}

Solution run_genetic(
    const JobShopInstance& instance,
    size_t population_size,
    size_t generations,
    size_t tournament_size,
    double mutation_prob,
    unsigned int seed
) {
    std::mt19937 rng(seed > 0 ? seed : std::time(nullptr));
    auto population = generate_population(instance, population_size, rng());
    Solution best_overall = population[0];
    int best_makespan = calculate_makespan(instance, best_overall);

    for (size_t gen = 0; gen < generations; ++gen) {
        std::vector<Solution> new_population;
        while (new_population.size() < population_size) {
            // Selekcja
            Solution parent1 = tournament_selection(population, instance, tournament_size, rng());
            Solution parent2 = tournament_selection(population, instance, tournament_size, rng());
            // Krzyżowanie
            Solution child = order_crossover(parent1, parent2, rng());
            // Mutacja
            std::uniform_real_distribution<double> prob(0.0, 1.0);
            if (prob(rng) < mutation_prob) {
                mutate_swap(child, rng());
            }
            new_population.push_back(child);
            // Aktualizuj najlepszego
            Solution child_copy = child;
            int ms = calculate_makespan(instance, child_copy);
            if (ms < best_makespan) {
                best_makespan = ms;
                best_overall = child;
            }
        }
        population = std::move(new_population);
    }
    return best_overall;
}

} // namespace jobshop
