#ifndef JOBSHOP_GENETIC_HPP
#define JOBSHOP_GENETIC_HPP

#include "jobshop/solution.hpp"
#include <vector>
#include <random>
#include <unordered_set>
#include <algorithm>
#include <utility>
#include <cstddef>

namespace jobshop {

// Generuje losową permutację operacji
Solution generate_random_solution(const JobShopInstance& instance, std::mt19937& rng);

// Generuje całą populację
std::vector<Solution> generate_population(const JobShopInstance& instance, size_t population_size, std::mt19937& rng);

// Wybór turniejowy
Solution tournament_selection(const std::vector<Solution>& population, const JobShopInstance& instance, size_t tournament_size, std::mt19937& rng);

// Krzyżowanie porządkowe (Order Crossover - OX)
Solution order_crossover(const Solution& parent1, const Solution& parent2, std::mt19937& rng);

// Mutacja przez zamianę dwóch operacji miejscami
void mutate_swap(Solution& solution, std::mt19937& rng);

// Główna funkcja algorytmu genetycznego
Solution run_genetic(
    const JobShopInstance& instance,
    size_t population_size,
    size_t generations,
    size_t tournament_size,
    double mutation_prob,
    std::mt19937& rng
);


} // namespace jobshop

#endif // JOBSHOP_GENETIC_HPP
