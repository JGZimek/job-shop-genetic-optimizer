#ifndef JOBSHOP_SOLUTION_HPP
#define JOBSHOP_SOLUTION_HPP

#include "jobshop/core.hpp"
#include <vector>
#include <utility>
#include <cstddef>

namespace jobshop {

struct Solution {
    std::vector<std::pair<size_t, size_t>> operation_sequence; // <job_id, operation_id>
    std::vector<int> start_times; // czasy startu operacji
    int makespan = 0;
};

// Deklaracja funkcji obliczającej makespan
int calculate_makespan(const JobShopInstance& instance, Solution& solution);

} // namespace jobshop

#endif // JOBSHOP_SOLUTION_HPP
