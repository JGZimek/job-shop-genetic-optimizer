#ifndef JOBSHOP_EXACT_HPP
#define JOBSHOP_EXACT_HPP
#include "jobshop/solution.hpp"
#include <optional>

namespace jobshop {

/*
 * Exact A* solver for Job Shop Scheduling with transport times.
 *
 * Returns the optimal Solution (operation sequence and start times).
 * If the instance is too big, this may use a lot of memory / time.
 */
Solution solve_exact(const JobShopInstance& instance);

} // namespace jobshop

#endif // JOBSHOP_EXACT_HPP