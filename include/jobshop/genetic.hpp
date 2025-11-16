#ifndef JOBSHOP_GENETIC_HPP
#define JOBSHOP_GENETIC_HPP

#include "jobshop/solution.hpp"
#include <vector>
#include <random>
#include <unordered_set>
#include <algorithm>
#include <utility>
#include <cstddef>
#include <ctime>

namespace jobshop {

// Generuje losową permutację operacji
Solution generate_random_solution(const JobShopInstance& instance, unsigned int seed = 0);

// Generuje całą populację
std::vector<Solution> generate_population(const JobShopInstance& instance, size_t population_size, unsigned int seed = 0);

// Wybór turniejowy
Solution tournament_selection(const std::vector<Solution>& population, const JobShopInstance& instance, size_t tournament_size, unsigned int seed = 0);

// Krzyżowanie porządkowe (Order Crossover - OX)
Solution order_crossover(const Solution& parent1, const Solution& parent2, unsigned int seed = 0);

// Mutacja przez zamianę dwóch operacji miejscami
void mutate_swap(Solution& solution, unsigned int seed = 0);

// Główna funkcja algorytmu genetycznego
Solution run_genetic(
    const JobShopInstance& instance,
    size_t population_size,
    size_t generations,
    size_t tournament_size,
    double mutation_prob,
    unsigned int seed = 0
);

} // namespace jobshop

#endif // JOBSHOP_GENETIC_HPP
