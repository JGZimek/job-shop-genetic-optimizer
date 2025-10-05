#include "jobshop/file_io.hpp"

namespace jobshop {

JobShopInstance load_instance_from_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        throw std::runtime_error("Cannot open file: " + filename);
    }

    size_t n_jobs, n_machines;
    file >> n_jobs >> n_machines;

    JobShopInstance instance;
    instance.num_machines = n_machines;
    instance.jobs.resize(n_jobs);

    for (size_t j = 0; j < n_jobs; ++j) {
        instance.jobs[j].job_id = j;
        instance.jobs[j].operations.resize(n_machines);

        // Wczytaj maszyny
        for (size_t op = 0; op < n_machines; ++op) {
            size_t machine_id;
            file >> machine_id;
            instance.jobs[j].operations[op].machine_id = machine_id;
            instance.jobs[j].operations[op].job_id = j;
            instance.jobs[j].operations[op].operation_id = op;
        }

        // Wczytaj czasy przetwarzania
        for (size_t op = 0; op < n_machines; ++op) {
            int proc_time;
            file >> proc_time;
            instance.jobs[j].operations[op].processing_time = proc_time;
        }
    }

    // Wczytaj macierz czasów transportu
    instance.transport_times.resize(n_machines, std::vector<int>(n_machines, 0));
    for (size_t i = 0; i < n_machines; ++i) {
        for (size_t k = 0; k < n_machines; ++k) {
            file >> instance.transport_times[i][k];
        }
    }

    return instance;
}

} // namespace jobshop
