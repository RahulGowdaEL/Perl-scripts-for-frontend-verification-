.PHONY: default run_perl_script run_perl_script2

# Default target
default: run_perl_script run_perl_script2

run_perl_script :
	@echo "Running Perl script..."
	@echo "$(INPUT_DIR)"
	@echo "$(INPUT_FILE)"
	@perl $(PERL_SCRIPT) -input_file $(INPUT_FILE) -output_file $(OUTPUT_FILE)
	@echo "$(OUTPUT_FILE)"

run_perl_script2 :
	@echo "Running Perl script_lp..."
	@echo "$(INPUT_DIR_lp)"
	@echo "$(INPUT_FILE_lp)"
	/pkg/qct/software/perl/5.18.0/bin/perl $(PERL_SCRIPT_lp) -input_file $(INPUT_FILE_lp) -output_file $(OUTPUT_FILE_lp)
	@echo "$(OUTPUT_FILE_lp)"




.PHONY: run_perl_script
run_perl_script :
	@echo "Running Perl script..."
	@echo "$(INPUT_DIR)"
	@echo "$(INPUT_FILE)"
	@perl $(PERL_SCRIPT) -input_file $(INPUT_FILE) -output_file $(OUTPUT_FILE)
	@echo "$(OUTPUT_FILE)"
#-output_file $(OUTPUT_FILE)

.PHONY: run_perl_script2
run_perl_script2 :
	@echo "Running Perl script_lp..."
	@echo "$(INPUT_DIR_lp)"
	@echo "$(INPUT_FILE_lp)"
	/pkg/qct/software/perl/5.18.0/bin/perl $(PERL_SCRIPT_lp) -input_file $(INPUT_FILE_lp) -output_file $(OUTPUT_FILE_lp)
	@echo "$(OUTPUT_FILE_lp)"
