#include <iostream>
#include "jobshop/core.hpp"
#include "jobshop/file_io.hpp"

int main() {
    // Ścieżka do przykładowej instancji
    std::string filename = "../data/instances/instance_small.txt";
    jobshop::JobShopInstance instance = jobshop::load_instance_from_file(filename);

    std::cout << "Jobs: " << instance.jobs.size() << "\n";
    std::cout << "Machines: " << instance.num_machines << "\n\n";

    for (const auto& job : instance.jobs) {
        std::cout << "Job " << job.job_id << ": ";
        for (const auto& op : job.operations) {
            std::cout << "[M" << op.machine_id << ",T" << op.processing_time << "] ";
        }
        std::cout << "\n";
    }

    std::cout << "\nTransport times matrix:\n";
    for (size_t i = 0; i < instance.num_machines; ++i) {
        for (size_t j = 0; j < instance.num_machines; ++j) {
            std::cout << instance.transport_times[i][j] << " ";
        }
        std::cout << "\n";
    }
    return 0;
}
