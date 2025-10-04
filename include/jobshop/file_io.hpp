#ifndef JOBSHOP_FILE_IO_HPP
#define JOBSHOP_FILE_IO_HPP

#include "jobshop/core.hpp"
#include <string>

namespace jobshop {

JobShopInstance load_instance_from_file(const std::string& filename);

} // namespace jobshop

#endif // JOBSHOP_FILE_IO_HPP
