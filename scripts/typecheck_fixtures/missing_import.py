# PATTERN: import of nonexistent module; checker should report unresolved import
import nonexistent_module_xyz_123

print(nonexistent_module_xyz_123.value)
