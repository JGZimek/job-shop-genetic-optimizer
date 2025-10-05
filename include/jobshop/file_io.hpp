#ifndef JOBSHOP_FILE_IO_HPP
#define JOBSHOP_FILE_IO_HPP

#include "jobshop/solution.hpp"
#include <string>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace jobshop {

JobShopInstance load_instance_from_file(const std::string& filename);

} // namespace jobshop

#endif // JOBSHOP_FILE_IO_HPP
