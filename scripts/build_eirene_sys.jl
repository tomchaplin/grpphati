import Pkg
Pkg.add("SharedArrays")
Pkg.add("Distributed")
Pkg.add("Eirene")
using PackageCompiler
create_sysimage(["Eirene"], sysimage_path="eirene_sys.so",
                precompile_execution_file="precompile_file.jl")
