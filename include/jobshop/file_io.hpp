#ifndef JOBSHOP_FILE_IO_HPP
#define JOBSHOP_FILE_IO_HPP

#include "jobshop/solution.hpp"
#include <string>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace jobshop {

// Format detection
enum class FileFormat { TXT, CSV, JSON };
FileFormat detect_format(const std::string& filename);

// Main loader
JobShopInstance load_instance_from_file(const std::string& filename);

// Format-specific parsers
JobShopInstance parse_txt_format(std::ifstream& file);
JobShopInstance parse_csv_format(std::ifstream& file);
JobShopInstance parse_json_format(const std::string& filename);

// Validation
void validate_instance(const JobShopInstance& instance);

} // namespace jobshop

#endif // JOBSHOP_FILE_IO_HPP
