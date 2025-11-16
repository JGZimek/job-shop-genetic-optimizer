#include "jobshop/exact.hpp"
#include "jobshop/solution.hpp"

#include <queue>
#include <unordered_map>
#include <string>
#include <vector>
#include <limits>
#include <sstream>
#include <functional>
#include <algorithm>

namespace jobshop {

namespace {

using size_t = std::size_t;

// Serialize state vectors into a compact string key for unordered_map
static std::string make_state_key(const std::vector<size_t>& job_next,
                                  const std::vector<int>& machine_avail,
                                  const std::vector<int>& job_last_finish) {
    // format: j:J0,J1,...|m:M0,M1,...|t:T0,T1,...
    std::string s;
    s.reserve(64 + job_next.size()*4 + machine_avail.size()*4);
    // jobs
    for (size_t i = 0; i < job_next.size(); ++i) {
        if (i) s.push_back(',');
        s += std::to_string(job_next[i]);
    }
    s.push_back('|');
    for (size_t i = 0; i < machine_avail.size(); ++i) {
        if (i) s.push_back(',');
        s += std::to_string(machine_avail[i]);
    }
    s.push_back('|');
    for (size_t i = 0; i < job_last_finish.size(); ++i) {
        if (i) s.push_back(',');
        s += std::to_string(job_last_finish[i]);
    }
    return s;
}

// Compute an admissible lower bound h(state).
// We use: h = max( max_machine_avail, max_j (job_last_finish[j] + remaining_proc[j]) )
// This is transport-aware because remaining_proc counts processing times only; to be more transport-aware
// we could add minimal transport times but that risks complexity. This LB is admissible.
static int heuristic_lb(const JobShopInstance& instance,
                        const std::vector<int>& machine_avail,
                        const std::vector<int>& job_last_finish,
                        const std::vector<size_t>& job_next_op,
                        const std::vector<int>& remaining_proc) {
    int max_machine = 0;
    for (int t : machine_avail) if (t > max_machine) max_machine = t;

    int max_job = 0;
    for (size_t j = 0; j < job_next_op.size(); ++j) {
        int cand = job_last_finish[j] + remaining_proc[j];
        if (cand > max_job) max_job = cand;
    }
    return std::max(max_machine, max_job);
}

} // namespace

struct NodeInfo {
    int g; // current makespan (cost-so-far)
    std::string parent_key; // serialized parent state key (empty for root)
    std::pair<size_t,size_t> scheduled_op; // (job_id, op_id) that led to this node (meaning: this op is last scheduled)
    int start_time; // start time of that scheduled operation
};

// Priority queue element
struct PQItem {
    int f;
    int g;
    std::string key; // serialized state key
    // tie-breaker: smaller g first
    bool operator<(PQItem const& other) const {
        if (f != other.f) return f > other.f; // min-heap by f
        return g > other.g;
    }
};

Solution solve_exact(const JobShopInstance& instance) {
    Solution empty;
    const size_t num_jobs = instance.jobs.size();
    const size_t num_machines = instance.num_machines;

    // total ops
    size_t total_ops = 0;
    for (const auto& j : instance.jobs) total_ops += j.operations.size();
    if (total_ops == 0) return empty;

    // Precompute remaining processing time per job for each possible op index
    // remaining_proc[j] = sum of processing times of operations from job_next_op to end
    std::vector<int> job_total_proc(num_jobs, 0);
    for (size_t j = 0; j < num_jobs; ++j) {
        int s = 0;
        for (const auto& op : instance.jobs[j].operations) s += op.processing_time;
        job_total_proc[j] = s;
    }

    // initial state
    std::vector<size_t> init_job_next(num_jobs, 0);
    std::vector<int> init_machine_avail(num_machines, 0);
    std::vector<int> init_job_last_finish(num_jobs, 0);
    std::vector<int> init_remain_proc(num_jobs, 0);
    for (size_t j = 0; j < num_jobs; ++j) init_remain_proc[j] = job_total_proc[j];

    std::string init_key = make_state_key(init_job_next, init_machine_avail, init_job_last_finish);

    // visited map: state_key -> NodeInfo (stores best g reached for that state)
    std::unordered_map<std::string, NodeInfo> visited;
    visited.reserve(1 << 16);

    // priority queue
    std::priority_queue<PQItem> pq;

    int init_g = 0;
    int init_h = heuristic_lb(instance, init_machine_avail, init_job_last_finish, init_job_next, init_remain_proc);
    pq.push(PQItem{init_g + init_h, init_g, init_key});

    visited[init_key] = NodeInfo{init_g, std::string(), std::pair<size_t,size_t>{size_t(-1), size_t(-1)}, 0};

    // We'll also need to store per-state auxiliary data (job_next, machine_avail, job_last_finish, remaining_proc)
    // so that when we pop a key we can reconstruct the vectors. We'll store them in a separate map.
    struct Aux {
        std::vector<size_t> job_next;
        std::vector<int> machine_avail;
        std::vector<int> job_last_finish;
        std::vector<int> remain_proc;
    };
    std::unordered_map<std::string, Aux> aux_map;
    aux_map.reserve(1 << 16);
    aux_map[init_key] = Aux{init_job_next, init_machine_avail, init_job_last_finish, init_remain_proc};

    // A small counter for nodes popped (optional; can be removed)
    // size_t nodes_expanded = 0;

    while (!pq.empty()) {
        PQItem it = pq.top(); pq.pop();

        // If the popped state's g differs from visited stored g, it's stale - skip
        auto vit = visited.find(it.key);
        if (vit == visited.end()) continue;
        if (vit->second.g != it.g) continue;

        // Expand this node
        // nodes_expanded++;

        Aux curr = aux_map[it.key];
        const std::vector<size_t>& job_next = curr.job_next;
        const std::vector<int>& machine_avail = curr.machine_avail;
        const std::vector<int>& job_last_finish = curr.job_last_finish;
        const std::vector<int>& remain_proc = curr.remain_proc;
        int curr_g = it.g;

        // Check goal: all jobs finished
        bool goal = true;
        for (size_t j = 0; j < num_jobs; ++j) {
            if (job_next[j] < instance.jobs[j].operations.size()) { goal = false; break; }
        }
        if (goal) {
            // reconstruct solution by following parent pointers from visited map
            // collect sequence in reverse
            std::vector<std::pair<size_t,size_t>> seq_rev;
            std::vector<int> starts_rev;
            std::string cur_key = it.key;
            while (true) {
                auto info_it = visited.find(cur_key);
                if (info_it == visited.end()) break;
                NodeInfo info = info_it->second;
                if (info.parent_key.empty()) break; // root
                seq_rev.push_back(info.scheduled_op);
                starts_rev.push_back(info.start_time);
                cur_key = info.parent_key;
            }
            // reverse to get forward order
            std::reverse(seq_rev.begin(), seq_rev.end());
            std::reverse(starts_rev.begin(), starts_rev.end());

            Solution sol;
            sol.operation_sequence = std::move(seq_rev);
            sol.start_times = std::move(starts_rev);
            sol.makespan = curr_g;
            return sol;
        }

        // Generate successors: for every job with remaining op, schedule its next op
        for (size_t j = 0; j < num_jobs; ++j) {
            size_t op_idx = job_next[j];
            if (op_idx >= instance.jobs[j].operations.size()) continue; // job finished

            const Operation& op = instance.jobs[j].operations[op_idx];
            size_t m = op.machine_id;
            int proc = op.processing_time;

            // transport time from previous op in the same job (if any)
            int transport = 0;
            if (op_idx > 0) {
                size_t prev_m = instance.jobs[j].operations[op_idx - 1].machine_id;
                transport = instance.transport_times[prev_m][m];
            }

            int earliest_start = std::max(machine_avail[m], job_last_finish[j] + transport);
            int finish = earliest_start + proc;
            int new_g = std::max(curr_g, finish);

            // Build new state vectors
            std::vector<size_t> next_job_next = job_next;
            std::vector<int> next_machine_avail = machine_avail;
            std::vector<int> next_job_last_finish = job_last_finish;
            std::vector<int> next_remain_proc = remain_proc;

            next_job_next[j] = op_idx + 1;
            next_machine_avail[m] = finish;
            next_job_last_finish[j] = finish;
            next_remain_proc[j] = remain_proc[j] - proc;

            std::string next_key = make_state_key(next_job_next, next_machine_avail, next_job_last_finish);

            // If we have seen this state with a <= g, skip
            auto known = visited.find(next_key);
            if (known != visited.end() && known->second.g <= new_g) {
                continue;
            }

            // compute heuristic
            int h = heuristic_lb(instance, next_machine_avail, next_job_last_finish, next_job_next, next_remain_proc);
            int f = new_g + h;

            // store/update visited and aux
            visited[next_key] = NodeInfo{new_g, it.key, std::pair<size_t,size_t>{j, op_idx}, earliest_start};
            aux_map[next_key] = Aux{std::move(next_job_next), std::move(next_machine_avail),
                                    std::move(next_job_last_finish), std::move(next_remain_proc)};

            pq.push(PQItem{f, new_g, next_key});
        }
    }

    // If queue exhausted, no solution found (should not happen)
    return empty;
}

} // namespace jobshop
