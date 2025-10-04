#ifndef JOBSHOP_GENETIC_HPP
#define JOBSHOP_GENETIC_HPP

#include "jobshop/core.hpp"
#include "jobshop/solution.hpp"
#include <vector>
#include <random>

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

} // namespace jobshop

#endif // JOBSHOP_GENETIC_HPP
