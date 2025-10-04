#ifndef JOBSHOP_CORE_HPP
#define JOBSHOP_CORE_HPP

#include <vector>
#include <cstddef>

namespace jobshop {

struct Operation {
    std::size_t job_id;
    std::size_t operation_id;
    std::size_t machine_id;
    int processing_time;
};

struct Job {
    std::size_t job_id;
    std::vector<Operation> operations;
};

struct JobShopInstance {
    std::vector<Job> jobs;
    std::size_t num_machines;
    std::vector<std::vector<int>> transport_times;
};

} // namespace jobshop

#endif // JOBSHOP_CORE_HPP
