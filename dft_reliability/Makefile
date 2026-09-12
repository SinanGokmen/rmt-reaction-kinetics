.PHONY: restore data verify paper reproduce
restore:
	python3 src/restore_results.py
data:
	python3 src/download_data.py
verify: restore data
	OPENBLAS_NUM_THREADS=1 python3 src/verify_reliability.py
	OPENBLAS_NUM_THREADS=1 python3 src/verify_small_seed.py
paper:
	python3 src/build_pdf.py
reproduce: data
	OPENBLAS_NUM_THREADS=1 python3 src/audit_data.py
	OPENBLAS_NUM_THREADS=1 python3 src/denoise_benchmark.py
	OPENBLAS_NUM_THREADS=1 python3 src/analyze_results.py
	OPENBLAS_NUM_THREADS=1 python3 src/verify_theory.py
	OPENBLAS_NUM_THREADS=1 python3 src/synthetic_covariance.py
	OPENBLAS_NUM_THREADS=1 python3 src/build_figures.py
	OPENBLAS_NUM_THREADS=1 python3 src/reliability_benchmark.py
	OPENBLAS_NUM_THREADS=1 python3 src/analyze_reliability.py
	OPENBLAS_NUM_THREADS=1 python3 src/small_seed_benchmark.py
	OPENBLAS_NUM_THREADS=1 python3 src/analyze_small_seed.py
	python3 src/write_small_seed_section.py
	$(MAKE) verify paper
